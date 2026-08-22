import asyncio
import csv
import json
import math
import os
import re
import socket
import struct
import subprocess
import sys
import threading
import time
import websockets
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# --- 2. KONFIGURACIJA I DEFINICIJE ---
MOJ_LOKATOR = "JN65XF"
MOJ_POZIVNI = "9A5CW"
WANTED_DATOTEKA = "wanted_QTH.txt"
LOTW_DATOTEKA = "lotw-user-activity.csv"
WSJT_LOG = "wsjtx_log.adi"
JSON_FILE_PATH = r"C:\Program Files\Mosquitto\9a5cw_rx.json"

WSJTX_PORT = 2342
JTDX_PORT = 2333
RELAY_PORT = 2237
WS_PORT = 8001
HTTP_PORT = 8000

# Globalne varijable
lotw_users = set()
wanted_lokatori = set()
lotw_korisnici = set()
logirani_qsos = set()
wkd_calls = set()
cfm_calls = set()
cfm_grids = set()
cfm_prefectures = set()
ja_call_to_pref = {}
connected_clients = set()
last_decodes = {}
call_to_grid = {}
current_active_band = "12m"

rx_stavke = []
tx_stavke = []
mqtt_process_rx = None
mqtt_process_tx = None


# --- 3. POMOĆNE MATEMATIČKE I GEOGRAFSKE FUNKCIJE ---

def locator_to_latlon(locator):
    locator = locator.upper().strip()
    if len(locator) < 4:
        return 0.0, 0.0
    lon = (ord(locator[0]) - ord("A")) * 20 - 180
    lat = (ord(locator[1]) - ord("A")) * 10 - 90
    lon += (ord(locator[2]) - ord("0")) * 2
    lat += (ord(locator[3]) - ord("0")) * 1
    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord("A") + 0.5) / 12
        lat += (ord(locator[5]) - ord("A") + 0.5) / 24
    else:
        lon += 1.0
        lat += 0.5
    return lat, lon


def load_needed_prefs():
    needed = {}
    if not os.path.exists("need_prefs.txt"):
        return needed
    
    with open("need_prefs.txt", "r", encoding='utf-8') as f:
        for line in f:
            if ':' not in line: continue
            band, prefs = line.split(':', 1)
            band = band.strip().lower()
            pref_list = {p.strip().lower() for p in prefs.split(',') if p.strip()}
            needed[band] = pref_list
    return needed

    
def izracunaj_qtf_i_udaljenost(loc1, loc2):
    try:
        lat1, lon1 = locator_to_latlon(loc1)
        lat2, lon2 = locator_to_latlon(loc2)
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_lambda = math.radians(lon2 - lon1)
        y = math.sin(d_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
        bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
        R = 6371.0
        dphi = math.radians(lat2 - lat1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(bearing), round(R * c)
    except Exception:
        return 0, 0


def get_band_from_freq(freq_hz):
    if 1800000 <= freq_hz <= 2000000: return "160m"
    if 3500000 <= freq_hz <= 4000000: return "80m"
    if 5350000 <= freq_hz <= 5450000: return "60m"
    if 7000000 <= freq_hz <= 7300000: return "40m"
    if 10100000 <= freq_hz <= 10150000: return "30m"
    if 14000000 <= freq_hz <= 14350000: return "20m"
    if 18068000 <= freq_hz <= 18168000: return "17m"
    if 21000000 <= freq_hz <= 21450000: return "15m"
    if 24890000 <= freq_hz <= 24990000: return "12m"
    if 28000000 <= freq_hz <= 29700000: return "10m"
    if 40000000 <= freq_hz <= 42000000: return "8m"    
    if 50000000 <= freq_hz <= 54000000: return "6m"    
    if 69900000 <= freq_hz <= 70500000: return "4m"    
    return "FT8"


# --- 4. UČITAVANJE BAZA I LOGOVA ---

def parse_adif(filepath):
    calls = set()
    grid_bands = set() 
    states = set()
    call_grid_map = {}
    logirani = set()
    if not os.path.exists(filepath):
        return calls, grid_bands, states, call_grid_map, logirani
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    records = content.split('<eor>')
    for rec in records:
        rec_upper = rec.upper()
        call_match = re.search(r'<CALL:\d+>([^<\s]+)', rec_upper)
        grid_match = re.search(r'<GRIDSQUARE:\d+>([^<\s]+)', rec_upper)
        band_match = re.search(r'<BAND:\d+>([^<\s]+)', rec_upper) 
        
        call_val = None
        grid_val = None
        band_val = "6m" 
        
        if call_match:
            call_val = call_match.group(1).strip()
            calls.add(call_val)
        if grid_match:
            grid_val = grid_match.group(1).strip()[:4]
        if band_match:
            raw_b = band_match.group(1).strip().lower()
            band_val = raw_b.replace("mhz", "m")
            
        if grid_val:
            grid_bands.add((band_val, grid_val)) 
            
        if call_val and grid_val:
            call_grid_map[call_val] = grid_val
            
        if call_val and band_val:
            logirani.add((call_val.upper(), band_val))

        state_match = re.search(r'<STATE:\d+>([^<\s]+)', rec_upper)
        if state_match:
            val = state_match.group(1).strip()
            if val.isdigit():
                states.add(int(val))
    return calls, grid_bands, states, call_grid_map, logirani


def load_lotw_csv(filepath="lotw.csv"):
    global lotw_users, lotw_korisnici
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().split(',')
                if parts:
                    call = parts[0].strip().upper().replace('"', '')
                    if call:
                        lotw_users.add(call)
    except Exception:
        pass


def load_databases():
    global wkd_calls, cfm_calls, cfm_grids, cfm_prefectures, ja_call_to_pref, call_to_grid
    global wanted_lokatori, lotw_korisnici, logirani_qsos
    
    c_calls, c_grids, c_states, c_map, _ = parse_adif('lotwreport.adi')
    cfm_calls.update(c_calls)
    cfm_grids.update(c_grids)
    cfm_prefectures.update(c_states)
    call_to_grid.update(c_map)
    
    w_calls, _, _, w_map, logirani = parse_adif(WSJT_LOG)
    wkd_calls.update(w_calls)
    call_to_grid.update(w_map)
    logirani_qsos.update(logirani)
    
    if os.path.exists(WANTED_DATOTEKA):
        w = set()
        with open(WANTED_DATOTEKA, "r", encoding="utf-8") as f:
            for line in f:
                l = line.strip().upper()
                if l and not l.startswith("#"):
                    w.add(l)
        wanted_lokatori = w

    if os.path.exists(LOTW_DATOTEKA):
        l_set = set()
        try:
            with open(LOTW_DATOTEKA, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        c = row[0].strip().upper()
                        if c and not c.startswith("#"):
                            l_set.add(c)
            lotw_korisnici = l_set
        except Exception:
            pass

    load_lotw_csv('lotw.csv')
    lotw_korisnici.update(lotw_users)

    if os.path.exists('ja_dtb_big.csv'):
        with open('ja_dtb_big.csv', 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    call = parts[0].strip().upper()
                    pref_name = parts[1].strip()
                    ja_call_to_pref[call] = pref_name


# --- 5. AUTOMATSKO OSVJEŽAVANJE LOGA U POZADINI ---

def background_refresh_wsjt_log(interval=15):
    global wkd_calls, logirani_qsos, call_to_grid
    last_mtime = 0
    while True:
        try:
            if os.path.exists(WSJT_LOG):
                current_mtime = os.path.getmtime(WSJT_LOG)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    w_calls, _, _, w_map, logirani = parse_adif(WSJT_LOG)
                    wkd_calls.update(w_calls)
                    call_to_grid.update(w_map)
                    logirani_qsos.update(logirani)
        except Exception:
            pass
        time.sleep(interval)


# --- 6. PSKREPORTER CACHE FUNKCIJE ---

def load_pskreporter_grid_cache(file_path):
    global call_to_grid
    if not os.path.exists(file_path):
        return
    try:
        temp_cache = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    if not line_str.startswith("{"):
                        line_str = "{" + line_str
                    data = json.loads(line_str)
                    call = data.get("sc")
                    grid = data.get("sl")
                    if call and grid:
                        temp_cache[call] = grid
        call_to_grid.update(temp_cache)
    except Exception:
        pass


def background_reload_pskreporter(json_file_path, interval=60):
    global call_to_grid
    while True:
        try:
            temp_cache = {}
            with open(json_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_str = line.strip()
                    if line_str:
                        if not line_str.startswith("{"):
                            line_str = "{" + line_str
                        data = json.loads(line_str)
                        call = data.get("sc")
                        grid = data.get("sl")
                        if call and grid:
                            temp_cache[call] = grid
            call_to_grid = temp_cache
        except Exception:
            pass
        time.sleep(interval)


# --- 7. LOGIRANJE I OBRADA SPOTOVA ---

def log_decoded_to_file(band, call, locator, message):
    if not locator:
        locator = "N/A"
    log_line = f"{band}: {call} {locator} | Poruka: {message}\n"
    try:
        with open("decoded_log.txt", "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass


def odredi_tag(sender, lokator, dist, band):
    if dist > 2000:
        return "dx"
    if (sender.upper(), band.lower()) in logirani_qsos:
        return "vec_u_logu"
    if lokator:
        if lokator in wanted_lokatori or lokator[:4] in wanted_lokatori:
            return "wanted"
    if sender.upper() in lotw_korisnici:
        return "lotw"
    return "normal"


def parse_json_line_safely(raw_line):
    """Sanacija neispravnih JSON linija kojima nedostaje početna zagrada."""
    s = raw_line.strip()
    if not s:
        return None
    if not s.startswith("{"):
        s = "{" + s
    try:
        return json.loads(s)
    except Exception:
        return None


def obradi_zapis_mqtt(zapis, mod, emit_socket=True):
    if not isinstance(zapis, dict):
        return

    t_stamp = zapis.get("t", time.time())
    vrijeme = time.strftime("%H:%M:%S", time.localtime(t_stamp))

    sender = zapis.get("sc", "Unknown").upper()
    receiver = zapis.get("rc", "Unknown").upper()
    s_loc = zapis.get("sl", "").upper()
    r_loc = zapis.get("rl", "").upper()

    if mod == "RX":
        target = sender
        t_loc = s_loc
    else:
        target = receiver
        t_loc = r_loc

    band = zapis.get("b", "Unknown")
    clean_band = str(band).strip().lower()
    mode = zapis.get("md", "Unknown")
    report = zapis.get("rp", "N/A")
    freq = f"{zapis.get('f', 0) / 1000.0:.3f} kHz"

    qtf, dist = izracunaj_qtf_i_udaljenost(MOJ_LOKATOR, t_loc)
    lat, lon = locator_to_latlon(t_loc) if t_loc else (0.0, 0.0)
    tag = odredi_tag(target, t_loc, dist, band)

    je_lotw = target in lotw_korisnici
    je_u_logu = (target, clean_band) in logirani_qsos
    
    pref_val = ja_call_to_pref.get(target, None)
    
    pref_status = "NONE"
    is_needed_pref = False
    if pref_val:
        needed_prefs_list = load_needed_prefs()
        wanted_on_band = needed_prefs_list.get(clean_band, set())
        if pref_val.strip().lower() in wanted_on_band:
            pref_status = "NEEDED"
            is_needed_pref = True
        else:
            pref_status = "CFM"

    podatak = {
        "time": vrijeme,
        "callsign": target,
        "sender": sender,
        "receiver": receiver,
        "locator": t_loc,
        "lat": lat,
        "lon": lon,
        "qtf": f"{qtf}°" if t_loc else "N/A",
        "distance": f"{dist} km" if t_loc else "N/A",
        "distance_int": dist,
        "band": band,
        "mode": mode,
        "report": report,
        "frequency": freq,
        "tag": tag,
        "mod": mod,
        "lotw": je_lotw,
        "in_log": je_u_logu,
        "pref_name": pref_val,
        "pref_status": pref_status,
        "is_needed": is_needed_pref
    }

    if mod == "RX":
        rx_stavke.insert(0, podatak)
        if len(rx_stavke) > 500: rx_stavke.pop()
    else:
        tx_stavke.insert(0, podatak)
        if len(tx_stavke) > 500: tx_stavke.pop()

    if emit_socket:
        socketio.emit("novi_spot", podatak)


def preload_existing_mqtt(json_file, mod):
    """Učitavanje postojećih zapisa iz datoteke radi brzog prikaza u tabovima pri pokretanju."""
    if not os.path.exists(json_file):
        return
    try:
        with open(json_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for line in lines[-200:]:
                zapis = parse_json_line_safely(line)
                if zapis:
                    obradi_zapis_mqtt(zapis, mod, emit_socket=False)
    except Exception:
        pass


def pokreni_mqtt(json_file, mod, topic):
    global mqtt_process_rx, mqtt_process_tx
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    
    dir_name = os.path.dirname(json_file)
    if dir_name and not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name, exist_ok=True)
        except Exception:
            pass

    preload_existing_mqtt(json_file, mod)

    cmd = ["mosquitto_sub", "-h", "mqtt.pskreporter.info", "-t", topic]
    try:
        proc = subprocess.Popen(cmd, stdout=open(json_file, "a", encoding="utf-8"), stderr=subprocess.PIPE, creationflags=flags)
        if mod == "RX":
            mqtt_process_rx = proc
        else:
            mqtt_process_tx = proc
    except Exception:
        return

    while not os.path.exists(json_file):
        time.sleep(0.5)

    with open(json_file, "r", encoding="utf-8") as f_in:
        f_in.seek(0, os.SEEK_END)
        while True:
            line = f_in.readline()
            if not line:
                time.sleep(0.2)
                continue
            
            zapis = parse_json_line_safely(line)
            if zapis:
                obradi_zapis_mqtt(zapis, mod, emit_socket=True)


# --- 8. UDP I WEBSOCKET (WSJT-X / JTDX) DIO ---

def send_wsjtx_reply(target_call, rx_df, message, target_port=2333):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    magic = 0xadbccabb
    schema = 2
    
    def pack_string(s):
        if s is None:
            return struct.pack(">I", 0xffffffff)
        encoded = s.encode('utf-8')
        return struct.pack(">I", len(encoded)) + encoded

    msg_type_5 = 5 
    packet5 = struct.pack(">III", magic, schema, msg_type_5)
    packet5 += pack_string("WSJT-X")
    packet5 += pack_string(message)        
    packet5 += struct.pack(">?", True)

    msg_type_2 = 2
    packet2 = struct.pack(">III", magic, schema, msg_type_2)
    packet2 += pack_string("WSJT-X")
    packet2 += struct.pack(">?", True)

    for port in [JTDX_PORT, WSJTX_PORT]:
        sock.sendto(packet5, ("127.0.0.1", port))
        sock.sendto(packet2, ("127.0.0.1", port))


async def ws_handler(websocket):
    connected_clients.add(websocket)
    try:
        async for msg in websocket:
            try:
                data = json.loads(msg)
                if data.get("action") == "reply":
                    send_wsjtx_reply(
                        target_call=data["call"],
                        rx_df=data["df"],
                        message=data["message"],
                        target_port=data.get("port", WSJTX_PORT)
                    )
            except Exception:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)


async def broadcast_decode(data):
    if connected_clients:
        msg = json.dumps(data)
        await asyncio.gather(*(client.send(msg) for client in connected_clients), return_exceptions=True)


def parse_jtdx_universal(packet, bind_port=2333):
    global current_active_band, call_to_grid
    try:
        if len(packet) < 16:
            return None
        magic = struct.unpack(">I", packet[0:4])[0]
        if magic != 0xadbccabb and magic != 0xadbccbda:
            return None

        if len(packet) >= 12:
            msg_type = struct.unpack(">I", packet[8:12])[0]
            if msg_type == 1:
                for i in range(12, len(packet) - 8):
                    val = struct.unpack(">Q", packet[i:i+8])[0]
                    if 1000000 <= val <= 300000000:
                        current_active_band = get_band_from_freq(val)
                        break
                return None
            if msg_type != 2:
                return None

        raw_text = packet.decode('latin-1', errors='ignore')
        snr, df = -10, 1500
        
        possible_ints = []
        for i in range(12, len(packet) - 4):
            try:
                val = struct.unpack(">i", packet[i:i+4])[0]
                if -35 <= val <= 35:
                    possible_ints.append(('snr', val))
                elif 50 <= val <= 3500:
                    possible_ints.append(('df', val))
            except Exception:
                continue

        for t, val in possible_ints:
            if t == 'snr' and snr == -10:
                snr = val
            elif t == 'df':
                df = val
                break

        words = re.findall(r'[A-Z0-9/]{2,}', raw_text)
        ignored_words = ["WSJT", "JTDX", "FT8", "FT4", "JT65", "NONE", "RR73", "73", "RRR", "CQ", "QRZ", "DE"]
        valid_words = [w for w in words if w not in ignored_words and any(c.isdigit() for c in w) and 3 <= len(w) <= 7]

        if not valid_words:
            return None

        clean_words = []
        grid = ""
        for w in valid_words:
            if re.match(r'^[A-R]{2}[0-9]{2}$', w):
                grid = w
            else:
                clean_words.append(w)

        call = clean_words[-1] if clean_words else valid_words[-1]
        for cw in clean_words:
            if "9A5CW" not in cw:
                call = cw 

        if not grid:
            for w in words:
                if re.match(r'^[A-R]{2}[0-9]{2}$', w) and w not in ignored_words:
                    grid = w
                    break

        if not grid and call in call_to_grid:
            grid = call_to_grid[call]
        if grid:
            call_to_grid[call] = grid

        filtered_words = [w for w in words if w not in ["WSJT", "JTDX", "FT8"][:6]]
        while filtered_words:
            first = filtered_words[0]
            if (first.isdigit() and len(first) <= 3) or first == "BH":
                filtered_words.pop(0)
            else:
                break
        
        if filtered_words and filtered_words[0] == "BH":
            filtered_words.pop(0)

        message = " ".join(filtered_words)
        active_band = globals().get('current_active_band', '6m')

        detected_mode = "FT8"
        raw_upper = raw_text.upper()
        if "FT4" in raw_upper or "MSK" in raw_upper:
            detected_mode = "FT4"
        elif "Q65" in raw_upper:
            detected_mode = "Q65"
        elif "JT65" in raw_upper:
            detected_mode = "JT65"

        is_calling_me = ("9A5CW" in message and not message.startswith("CQ"))

        return {
            "time": time.strftime("%H:%M:%S"),
            "band": active_band,
            "mode": detected_mode,  
            "snr": snr,
            "df": df,
            "call": call,
            "message": message if message else f"CQ {call}",
            "grid": grid,
            "is_calling_me": is_calling_me
        }
    except Exception:
        return None


def listen_on_port(bind_port, relay_port, loop):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", bind_port))
    except Exception:
        return

    relay_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    needed_prefs_list = load_needed_prefs()
    last_prefs_mtime = 0

    while True:
        try:
            if os.path.exists("need_prefs.txt"):
                current_mtime = os.path.getmtime("need_prefs.txt")
                if current_mtime != last_prefs_mtime:
                    needed_prefs_list = load_needed_prefs()
                    last_prefs_mtime = current_mtime

            data, addr = sock.recvfrom(65535)
            relay_sock.sendto(data, ("127.0.0.1", relay_port))

            parsed = parse_jtdx_universal(data, bind_port)
            if parsed:
                call = parsed["call"]
                grid = parsed["grid"]
                clean_band = parsed["band"].strip().lower()

                log_decoded_to_file(
                    parsed["band"], call, grid, parsed["message"]
                )

                last_decodes[call] = {
                    "time": parsed["time"],
                    "mode": parsed["mode"],
                    "snr": parsed["snr"],
                    "df": parsed["df"],
                    "band": parsed["band"],
                    "message": parsed["message"],
                }

                # --- Obrada prefektura ---
                pref_val = ja_call_to_pref.get(call, None)
                pref_status = "NONE"
                is_needed = False

                if pref_val:
                    wanted_on_band = needed_prefs_list.get(clean_band, set())
                    if pref_val.strip().lower() in wanted_on_band:
                        pref_status = "NEEDED"
                        is_needed = True
                    else:
                        pref_status = "CFM"

                # --- Obrada Grid statusa ---
                grid_status = "NONE"
                if grid:
                    short_grid = grid[:4].upper()
                    if (clean_band, short_grid) in cfm_grids:
                        grid_status = "CFM"
                    else:
                        grid_status = "NEEDED"

                is_lotw = call in lotw_users or call in lotw_korisnici
                is_u_logu = (call.upper(), clean_band) in logirani_qsos

                # --- Slanje u SocketIO ---
                out = {
                    "time": parsed["time"],
                    "band": parsed["band"],
                    "mode": parsed["mode"],
                    "snr": parsed["snr"],
                    "df": parsed["df"],
                    "call": call,
                    "message": parsed["message"],
                    "grid": grid,
                    "grid_status": grid_status,
                    "pref_num": pref_val,
                    "pref_name": pref_val,
                    "pref_status": pref_status,
                    "is_needed": is_needed,
                    "is_new": is_needed,
                    "is_lotw": is_lotw,
                    "is_calling_me": parsed["is_calling_me"],
                    "in_log": is_u_logu,
                    "port": bind_port,
                    "receivedAt": time.time() * 1000,
                }

                socketio.emit("novi_ft8_decode", out)

        except Exception:
            pass


def start_udp_listener(loop):
    threading.Thread(target=listen_on_port, args=(WSJTX_PORT, RELAY_PORT, loop), daemon=True).start()
    threading.Thread(target=listen_on_port, args=(JTDX_PORT, RELAY_PORT, loop), daemon=True).start()


async def start_websocket_server():
    async with websockets.serve(ws_handler, "0.0.0.0", WS_PORT):
        await asyncio.Future()


def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server())


# --- 9. FLASK RUTE ---

@app.route("/")
def index():
    return render_template("index.html", moj_pozivni=MOJ_POZIVNI, moj_lokator=MOJ_LOKATOR)


@app.route("/api/data")
def api_data():
    return jsonify({
        "rx": rx_stavke[:100],
        "tx": tx_stavke[:100],
        "status": {
            "rx_count": len(rx_stavke),
            "tx_count": len(tx_stavke),
            "wanted": len(wanted_lokatori),
            "lotw": len(lotw_korisnici),
            "log": len(logirani_qsos),
        },
    })


@app.route("/api/qth", methods=["POST"])
def post_qth():
    global MOJ_LOKATOR
    data = request.json
    if "locator" in data:
        loc = data["locator"].strip().upper()
        if len(loc) >= 4:
            MOJ_LOKATOR = loc
            return jsonify({"success": True, "locator": MOJ_LOKATOR})
    return jsonify({"success": False}), 400


# --- 10. GLAVNO POKRETANJE APLIKACIJE ---

if __name__ == "__main__":
    load_databases()
    load_pskreporter_grid_cache(JSON_FILE_PATH)

    threading.Thread(target=background_refresh_wsjt_log, args=(15,), daemon=True).start()

    # RX MQTT: Slušamo spotove gdje ste vi primatelj
    threading.Thread(
        target=pokreni_mqtt,
        args=("9a5cw_rx.json", "RX", "pskr/filter/v2/+/+/+/9A5CW/#"),
        daemon=True,
    ).start()

    # TX MQTT: Slušamo spotove gdje ste vi pošiljatelj
    threading.Thread(
        target=pokreni_mqtt,
        args=("9a5cw_tx.json", "TX", "pskr/filter/v2/+/+/9A5CW/#"),
        daemon=True,
    ).start()
    
    threading.Thread(target=background_reload_pskreporter, args=(JSON_FILE_PATH, 30), daemon=True).start()

    loop = asyncio.new_event_loop()
    threading.Thread(target=run_asyncio_loop, args=(loop,), daemon=True).start()
    start_udp_listener(loop)

    print(f"[+] Web sučelje i Flask-SocketIO pokrenuti na: http://localhost:{HTTP_PORT}/")
    print(f"[+] WebSocket poslužitelj spreman na portu {WS_PORT}.")
    
    socketio.run(app, host='127.0.0.1', port=HTTP_PORT, debug=False)