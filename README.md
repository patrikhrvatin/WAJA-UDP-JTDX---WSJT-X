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
 ```
## ⚙️ 2. Configuration (Callsign & Locator)

To configure the application for your station, open main.py and modify the global variables at the top of the file with your callsign and QTH locator:
```bash
# --- 2. CONFIGURATION AND DEFINITIONS ---
MOJ_LOKATOR = "JO20RR"  # Change to your QTH locator (e.g., JO20RR)
MOJ_POZIVNI = "ON4IQX"   # Change to your callsign (e.g., ON4IQX)
WANTED_DATOTEKA = "wanted_QTH.txt"
LOTW_DATOTEKA = "lotw-user-activity.csv"
WSJT_LOG = "wsjtx_log.adi"
JSON_FILE_PATH = r"C:\Program Files\Mosquitto\on4iq_rx.json"  # Adjust Windows path accordingly - it is created automatically!
```

In the main application entry point (if __name__ == "__main__":), ensure the MQTT subscription topics reflect your callsign:
```bash
# RX MQTT: Listening for spots where you are the receiver
args=("on4iqx_rx.json", "RX", "pskr/filter/v2/+/+/+/ON4IQX/#")

# TX MQTT: Listening for spots where you are the transmitter
args=("on4iqx_tx.json", "TX", "pskr/filter/v2/+/+/ON4IQX/#")
 ```
### 📝 3. Japanese Prefectures File (need_prefs.txt)

To track wanted Japanese Prefectures per amateur band, create a text file named need_prefs.txt in the root directory. Modify or add target prefectures line-by-line using the format band: Prefecture1, Prefecture2, ....
```bash
6m: Kagoshima, Tokushima, Fukui, Gunma
10m: Aomori, Nagano, Mie, Nara, Wakayama, Hyogo, Toyama, Ishikawa, Yamaguchi, Tokushima, Kochi, Fukuoka, Nagasaki, Oita, Miyazaki
12m: Kyoto, Fukui, Okinawa
15m: Mie, Wakayama, Fukui, Yamaguchi, Tottori, Tokushima, Nagasaki, Oita, Miyazaki, Hokkaido, Aichi, Yamagata
17m: Aomori, Tokushima, Nagasaki
20m: Yamagata, Kyoto, Nara, Wakayama, Fukui, Tokushima, Kochi, Nagasaki, Miyazaki, Okinawa
30m: Fukui, Yamaguchi, Nagasaki, Miyazaki
40m: Yamagata, Fukui, Kochi, Nagasaki
80m:
160m:
```

### 📂 4. Required Databases & Project StructurePlace the following files in the root directory of your project:
### File Description:
                      lotwreport.adi ADIF export of confirmed contacts from LoTW 
                      wsjtx_log.adi Local log file from WSJT-X / JTDX
                      wanted_QTH.txt Target 4-digit or 6-digit Grid Locators (one per line, e.g., JO21, JN65)
                      need_prefs.txt Band-by-band list of needed Japanese prefectures 
                      lotw-user-activity.csv / lotw.csv List of active LoTW users
                      ja_dtb_big.csv Database mapping Japanese callsigns to prefecture names 
                      templates/index.html The primary Web UI template rendered by Flask

### Project Directory Layout:
ft8-monitor/
├── templates/
│   └── index.html
├── main.py
├── need_prefs.txt
├── wanted_QTH.txt
├── lotwreport.adi
├── wsjtx_log.adi
├── lotw.csv
├── ja_dtb_big.csv
└── requirements.txt

### 🚀 5. Installation & Usage

     1. Clone the repository:
    git clone [https://github.com/YOUR_USERNAME/ft8-monitor.git](https://github.com/YOUR_USERNAME/ft8-monitor.git)
cd ft8-monitor (your script folder)
     2. Install dependencies:
pip install -r requirements.txt
   
     3. Run the script:
   python flask_map16.py

     4. Access the Web Interface:
Open your browser and navigate to:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 6. Network Port Reference

    8000 – Flask Web Interface (HTTP) – Connect here to view index.html

    8001 – WebSocket server for low-latency communication with WSJT-X

    2333 / 2342 – Inbound UDP listening ports for WSJT-X / JTDX decodes

    2237 – Outbound UDP Relay port (forwards decodes to secondary apps like GridTracker or your Main Logger - using Winlog32 for UDP logging)


### 🔗 Advanced Setup: Sharing wsjtx_log.adi Across Multiple Applications

If you are running both WSJT-X and JTDX simultaneously or want this script to instantly read logs from another directory without duplicating files, you can create an NTFS Hardlink.

This allows multiple programs to read and write to the exact same log file in real time.
Using Link Shell Extension (GUI Method - Windows):

    Download and install Link Shell Extension.

    Navigate to your primary log directory (e.g., %LOCALAPPDATA%\WSJT-X).

    Right-click your original wsjtx_log.adi file and select Pick Link Source.

    Open your ft8-monitor project directory (or JTDX directory).

    Right-click on an empty space, select Drop As... -> Hardlink.

Using Windows Command Prompt (CLI Method):

Alternatively, you can create a hardlink natively via cmd (run as Administrator):

mklink /H "C:\path\to\ft8-monitor\wsjtx_log.adi" "%LOCALAPPDATA%\WSJT-X\wsjtx_log.adi"


   






