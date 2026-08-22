# FT8 / Digital Modes Real-Time Monitor & PSKReporter Relay

A real-time FT8/FT4 and digital modes monitoring system built with Python, Flask, and WebSockets. The application connects directly to **WSJT-X / JTDX** (via UDP and WebSockets) and to **PSKReporter** (via MQTT streams using `mosquitto_sub.exe`), cross-references incoming decodes with your local ADIF logs and custom databases, and serves live statistics to an interactive web dashboard (`index.html`).

---

## ✨ Features

- **Real-Time UDP Decoding:** Intercepts live decodes directly from WSJT-X / JTDX over UDP (ports `2333` and `2342`) and automatically relays them to secondary applications (e.g., GridTracker on port `2237`).
- **PSKReporter MQTT Feeds:** Subscribes to live RX/TX spots via MQTT (`mqtt.pskreporter.info`) using the background `mosquitto_sub.exe` utility.
- **Advanced Log & Award Tracking:**
  - Highlights confirmed vs. needed Maidenhead Grid Squares per band.
  - Dynamically tracks Japanese Prefectures (JA callsigns) against band-specific target lists (`need_prefs.txt`).
  - Identifies active **LoTW** (Logbook of The World) users.
  - Flags long-distance DX spots (>2000 km) and wanted QTH locators (`wanted_QTH.txt`).
- **Interactive Web Interface:** Served on `http://127.0.0.1:8000/` with live Socket.IO updates and interactive reply capabilities back to WSJT-X.

---

## 🛠️ 1. Script Requirements & Dependencies

### System Requirements (External Tools)
- **Mosquitto Client Tools (`mosquitto_sub` / `mosquitto_sub.exe`)**
  - Used by the script to subscribe to PSKReporter MQTT data streams (`pskr/filter/...`).
  - **Windows:** Download and install [Eclipse Mosquitto](https://mosquitto.org/download/). Ensure `mosquitto_sub.exe` is added to your system `PATH` (default log location: `C:\Program Files\Mosquitto\on4iq_rx.json`).
  - **Linux / Raspberry Pi:** 
    ```bash
    sudo apt update && sudo apt install mosquitto-clients
    ```
- **Amateur Radio Software**
  - **WSJT-X** or **JTDX** with UDP reporting enabled under **Settings -> Reporting** on ports `2342` or `2333`.

### Python Dependencies (For `requirements.txt`)

Install all required Python packages using `pip`:

```bash
pip install flask flask-socketio websockets

```bash
⚙️ 2. Configuration (Callsign & Locator)

To configure the application for your station, open main.py and modify the global variables at the top of the file with your callsign and QTH locator:
# --- 2. CONFIGURATION AND DEFINITIONS ---
MOJ_LOKATOR = "JO20AR"  # Change to your QTH locator (e.g., JO20AR)
MOJ_POZIVNI = "ON4IQ"   # Change to your callsign (e.g., ON4IQ)
WANTED_DATOTEKA = "wanted_QTH.txt"
LOTW_DATOTEKA = "lotw-user-activity.csv"
WSJT_LOG = "wsjtx_log.adi"
JSON_FILE_PATH = r"C:\Program Files\Mosquitto\on4iq_rx.json"  # Adjust Windows path accordingly

```bash
