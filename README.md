# FT8 / Digital Modes Real-Time Monitor & PSKReporter Relay

A real-time FT8/FT4 and digital modes monitoring application built with Python, Flask, and WebSockets. It intercepts UDP decodes from **WSJT-X** / **JTDX**, utilizes `mosquitto_sub.exe` to stream live MQTT data feeds from **`mqtt.pskreporter.info`**, cross-references incoming callsigns with your local ADIF logs and databases, and displays live statistics on an interactive Web Dashboard.

---

## ✨ Features

- **Live UDP Processing:** Intercepts live decodes directly from WSJT-X / JTDX over UDP (ports `2333` and `2342`) and relays them to secondary software (e.g., GridTracker on port `2237`).
- **PSKReporter MQTT Stream:** Subscribes to real-time RX/TX spots via MQTT (`mqtt.pskreporter.info`) using the `mosquitto_sub.exe` utility.
- **Log & Award Tracking:**
  - Highlights confirmed vs. needed Maidenhead Grid Squares per band.
  - Tracks Japanese Prefectures (JA calls) against band-specific target lists.
  - Identifies active **LoTW** (Logbook of The World) users.
  - Marks DX spots (>2000 km) and wanted QTH locators.
- **WebSocket Control:** Supports sending double-click reply commands back to WSJT-X / JTDX.

---

## 🛠️ System Requirements

### 1. External Tools
- **Python 3.8+**
- **Mosquitto MQTT Client (`mosquitto_sub.exe`)**
  - Used to handle the MQTT data transfer and subscription from `mqtt.pskreporter.info`.
  - **Linux / Debian / Raspberry Pi:** 
    ```bash
    sudo apt update && sudo apt install mosquitto-clients
    ```
  - **Windows:** Download and install [Eclipse Mosquitto](https://mosquitto.org/download/). Make sure `mosquitto_sub.exe` is added to your system `PATH` so the script can execute it in the background.
- **WSJT-X or JTDX**
  - Enable UDP Server reporting in **Settings -> Reporting** (Default ports: `2333` or `2342`).

---

## 📦 Installation and examples how to run:
# FT8 / Digital Modes Real-Time Monitor & PSKReporter Relay

The script is a real-time system for monitoring and analyzing FT8 and other digital amateur radio decodes. It connects to **WSJT-X / JTDX** (via UDP and WebSocket protocols) and to **PSKReporter** (via MQTT service), cross-references decoded callsigns against your logs and databases, and serves live data through a **Flask + Socket.IO** web interface (`index.html`).

---

## ✨ Features

- **Live UDP Processing:** Intercepts live decodes directly from WSJT-X / JTDX over UDP (ports `2333` and `2342`) and relays them to secondary software (e.g., GridTracker on port `2237`).
- **PSKReporter MQTT Stream:** Subscribes to real-time RX/TX spots via MQTT (`mqtt.pskreporter.info`) using the `mosquitto_sub.exe` utility.
- **Log & Award Tracking:**
  - Highlights confirmed vs. needed Maidenhead Grid Squares per band.
  - Tracks Japanese Prefectures (JA calls) against band-specific target lists.
  - Identifies active **LoTW** (Logbook of The World) users.
  - Marks DX spots (>2000 km) and wanted QTH locators.
- **WebSocket Control:** Supports sending double-click reply commands back to WSJT-X / JTDX.

---

## 🛠️ 1. Script Requirements & Dependencies

### System Requirements (External Tools)
- **Mosquitto Client Tools (`mosquitto_sub` / `mosquitto_sub.exe`)**
  - The script executes the `mosquitto_sub` command to subscribe to PSKReporter MQTT topics (`pskr/filter/...`).
  - **Windows:** Install [Eclipse Mosquitto](https://mosquitto.org/download/) and add it to your system `PATH` (the script defaults to storing JSON logs like `C:\Program Files\Mosquitto\on4iq_rx.json`).
  - **Linux / Raspberry Pi:** 
    ```bash
    sudo apt update && sudo apt install mosquitto-clients
    ```
- **Amateur Radio Software**
  - **WSJT-X** or **JTDX** with UDP reporting enabled in **Settings -> Reporting** on ports `2342` or `2333`.

### Python Dependencies (For `requirements.txt`)
Install the required packages using `pip`:
```bash
pip install flask flask-socketio websockets

Configuration (Callsign & Locator)

To use your own station details, open main.py and change the global configuration variables near the top of the file to match your callsign and grid locator (for example, ON4IQ and JO20AR):
# --- 2. CONFIGURATION AND DEFINITIONS ---
MOJ_LOKATOR = "JO20AR"  # Change to your QTH locator (e.g., JO20AR)
MOJ_POZIVNI = "ON4IQ"   # Change to your callsign (e.g., ON4IQ)
WANTED_DATOTEKA = "wanted_QTH.txt"
LOTW_DATOTEKA = "lotw-user-activity.csv"
WSJT_LOG = "wsjtx_log.adi"
JSON_FILE_PATH = r"C:\Program Files\Mosquitto\on4iq_rx.json"  # Adjust path accordingly

In the main execution section, make sure the MQTT subscription topics also reflect your callsign:

# RX MQTT: Listening for spots where you are the receiver
args=("on4iq_rx.json", "RX", "pskr/filter/v2/+/+/+/ON4IQ/#")

# TX MQTT: Listening for spots where you are the transmitter
args=("on4iq_tx.json", "TX", "pskr/filter/v2/+/+/ON4IQ/#")

Set up web templates:
Create a templates directory in the project root and place your index.html file inside. The Flask application serves this file as the main web interface:
ft8-monitor/
├── templates/
│   └── index.html
├── main.py
└── ...
Required Databases & FilesTo enable full tracking and identification features, place the following files in the project root directory:FileDescriptionlotwreport.adiADIF export of confirmed contacts from LoTWwsjtx_log.adiLocal log file from WSJT-X / JTDXwanted_QTH.txtList of target 4-digit / 6-digit Grid Locators (one per line)need_prefs.txtNeeded Japanese prefectures per band (e.g., 6m: 01, 02, 15)lotw-user-activity.csv / lotw.csvList of active LoTW usersja_dtb_big.csvDatabase mapping Japanese callsigns to prefecture codes

Usage & Web Interface

    Run the application from your terminal:
    Bash

python main.py

Open your web browser and navigate to the local address to access the index.html dashboard:
Plaintext

    [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

📡 Port Reference

    8000 – Flask Web Dashboard (HTTP) – Connect here to view index.html

    8001 – WebSocket server for low-latency WSJT-X commands

    2333 / 2342 – Inbound UDP listening ports for WSJT-X / JTDX decodes

    2237 – Outbound UDP Relay port (forwards decodes to other apps like GridTracker)


Markdown

# FT8 / Digital Modes Real-Time Monitor & PSKReporter Relay

The script is a real-time system for monitoring and analyzing FT8 and other digital amateur radio decodes. It connects to **WSJT-X / JTDX** (via UDP and WebSocket protocols) and to **PSKReporter** (via MQTT service), cross-references decoded callsigns against your logs and databases, and serves live data through a **Flask + Socket.IO** web interface (`index.html`).

---

## ✨ Features

- **Live UDP Processing:** Intercepts live decodes directly from WSJT-X / JTDX over UDP (ports `2333` and `2342`) and relays them to secondary software (e.g., GridTracker on port `2237`).
- **PSKReporter MQTT Stream:** Subscribes to real-time RX/TX spots via MQTT (`mqtt.pskreporter.info`) using the `mosquitto_sub.exe` utility.
- **Log & Award Tracking:**
  - Highlights confirmed vs. needed Maidenhead Grid Squares per band.
  - Tracks Japanese Prefectures (JA calls) against band-specific target lists.
  - Identifies active **LoTW** (Logbook of The World) users.
  - Marks DX spots (>2000 km) and wanted QTH locators.
- **WebSocket Control:** Supports sending double-click reply commands back to WSJT-X / JTDX.

---

## 🛠️ 1. Script Requirements & Dependencies

### System Requirements (External Tools)
- **Mosquitto Client Tools (`mosquitto_sub` / `mosquitto_sub.exe`)**
  - The script executes the `mosquitto_sub` command to subscribe to PSKReporter MQTT topics (`pskr/filter/...`).
  - **Windows:** Install [Eclipse Mosquitto](https://mosquitto.org/download/) and add it to your system `PATH` (the script defaults to storing JSON logs like `C:\Program Files\Mosquitto\on4iq_rx.json`).
  - **Linux / Raspberry Pi:** 
    ```bash
    sudo apt update && sudo apt install mosquitto-clients
    ```
- **Amateur Radio Software**
  - **WSJT-X** or **JTDX** with UDP reporting enabled in **Settings -> Reporting** on ports `2342` or `2333`.

### Python Dependencies (For `requirements.txt`)
Install the required packages using `pip`:
```bash
pip install flask flask-socketio websockets

⚙️ Configuration (Callsign & Locator)

To use your own station details, open main.py and change the global configuration variables near the top of the file to match your callsign and grid locator (for example, ON4IQ and JO20AR):
Python

# --- 2. CONFIGURATION AND DEFINITIONS ---
MOJ_LOKATOR = "JO20AR"  # Change to your QTH locator (e.g., JO20AR)
MOJ_POZIVNI = "ON4IQ"   # Change to your callsign (e.g., ON4IQ)
WANTED_DATOTEKA = "wanted_QTH.txt"
LOTW_DATOTEKA = "lotw-user-activity.csv"
WSJT_LOG = "wsjtx_log.adi"
JSON_FILE_PATH = r"C:\Program Files\Mosquitto\on4iq_rx.json"  # Adjust path accordingly

In the main execution section, make sure the MQTT subscription topics also reflect your callsign:
Python

# RX MQTT: Listening for spots where you are the receiver
args=("on4iq_rx.json", "RX", "pskr/filter/v2/+/+/+/ON4IQ/#")

# TX MQTT: Listening for spots where you are the transmitter
args=("on4iq_tx.json", "TX", "pskr/filter/v2/+/+/ON4IQ/#")

📦 Installation & Setup

    Clone the repository:
    Bash

git clone [https://github.com/YOUR_USERNAME/ft8-monitor.git](https://github.com/YOUR_USERNAME/ft8-monitor.git)
cd ft8-monitor

Set up web templates:
Create a templates directory in the project root and place your index.html file inside. The Flask application serves this file as the main web interface:
Plaintext

    ft8-monitor/
    ├── templates/
    │   └── index.html
    ├── main.py
    └── ...

📂 Required Databases & Files

To enable full tracking and identification features, place the following files in the project root directory:
File	Description
lotwreport.adi	ADIF export of confirmed contacts from LoTW
wsjtx_log.adi	Local log file from WSJT-X / JTDX
wanted_QTH.txt	List of target 4-digit / 6-digit Grid Locators (one per line)
need_prefs.txt	Needed Japanese prefectures per band (e.g., 6m: 01, 02, 15)
lotw-user-activity.csv / lotw.csv	List of active LoTW users
ja_dtb_big.csv	Database mapping Japanese callsigns to prefecture codes
🚀 Usage & Web Interface

    Run the application from your terminal:
    Bash

python main.py

Open your web browser and navigate to the local address to access the index.html dashboard:
Plaintext

    [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

📡 Port Reference

    8000 – Flask Web Dashboard (HTTP) – Connect here to view index.html

    8001 – WebSocket server for low-latency WSJT-X commands

    2333 / 2342 – Inbound UDP listening ports for WSJT-X / JTDX decodes

    2237 – Outbound UDP Relay port (forwards decodes to other apps like GridTracker)

dodajte strukturu needed_prefs.txt gdje se rade izmjene i upisuju nove tražene prefekture po opsezima:

6m: Kagoshima,Tokushima, Fukui,Gunma

10m: Aomori, Nagano, Mie, Nara, Wakayama, Hyogo, Toyama, Ishikawa, Yamaguchi, Tokushima, Kochi, Fukuoka, Nagasaki, Oita, Miyazaki

12m: Kyoto, Fukui, Okinawa

15m: Mie, Wakayama, Fukui, Yamaguchi, Tottori, Tokushima, Nagasaki, Oita, Miyazaki, Hokkaido, Aichi, Yamagata

17m: Aomori, Tokushima, Nagasaki

20m: Yamagata, Kyoto, Nara, Wakayama, Fukui, Tokushima, Kochi, Nagasaki, Miyazaki, Okinawa

30m: Fukui, Yamaguchi, Nagasaki, Miyazaki

40m: Yamagata, Fukui, Kochi, Nagasaki

80m:

160m:
Markdown

# FT8 / Digital Modes Real-Time Monitor & PSKReporter Relay

The script is a real-time system for monitoring and analyzing FT8 and other digital amateur radio decodes. It connects to **WSJT-X / JTDX** (via UDP and WebSocket protocols) and to **PSKReporter** (via MQTT service), cross-references decoded callsigns against your logs and databases, and serves live data through a **Flask + Socket.IO** web interface (`index.html`).

---

## ✨ Features

- **Live UDP Processing:** Intercepts live decodes directly from WSJT-X / JTDX over UDP (ports `2333` and `2342`) and relays them to secondary software (e.g., GridTracker on port `2237`).
- **PSKReporter MQTT Stream:** Subscribes to real-time RX/TX spots via MQTT (`mqtt.pskreporter.info`) using the `mosquitto_sub.exe` utility.
- **Log & Award Tracking:**
  - Highlights confirmed vs. needed Maidenhead Grid Squares per band.
  - Tracks Japanese Prefectures (JA calls) against band-specific target lists.
  - Identifies active **LoTW** (Logbook of The World) users.
  - Marks DX spots (>2000 km) and wanted QTH locators.
- **WebSocket Control:** Supports sending double-click reply commands back to WSJT-X / JTDX.

---

## 🛠️ 1. Script Requirements & Dependencies

### System Requirements (External Tools)
- **Mosquitto Client Tools (`mosquitto_sub` / `mosquitto_sub.exe`)**
  - The script executes the `mosquitto_sub` command to subscribe to PSKReporter MQTT topics (`pskr/filter/...`).
  - **Windows:** Install [Eclipse Mosquitto](https://mosquitto.org/download/) and add it to your system `PATH` (the script defaults to storing JSON logs like `C:\Program Files\Mosquitto\on4iq_rx.json`).
  - **Linux / Raspberry Pi:** 
    ```bash
    sudo apt update && sudo apt install mosquitto-clients
    ```
- **Amateur Radio Software**
  - **WSJT-X** or **JTDX** with UDP reporting enabled in **Settings -> Reporting** on ports `2342` or `2333`.

### Python Dependencies (For `requirements.txt`)
Install the required packages using `pip`:
```bash
pip install flask flask-socketio websockets

⚙️ Configuration (Callsign & Locator)

To use your own station details, open main.py and change the global configuration variables near the top of the file to match your callsign and grid locator (for example, ON4IQ and JO20AR):
Python

# --- 2. CONFIGURATION AND DEFINITIONS ---
MOJ_LOKATOR = "JO20AR"  # Change to your QTH locator (e.g., JO20AR)
MOJ_POZIVNI = "ON4IQ"   # Change to your callsign (e.g., ON4IQ)
WANTED_DATOTEKA = "wanted_QTH.txt"
LOTW_DATOTEKA = "lotw-user-activity.csv"
WSJT_LOG = "wsjtx_log.adi"
JSON_FILE_PATH = r"C:\Program Files\Mosquitto\on4iq_rx.json"  # Adjust path accordingly

In the main execution section, make sure the MQTT subscription topics also reflect your callsign:
Python

# RX MQTT: Listening for spots where you are the receiver
args=("on4iq_rx.json", "RX", "pskr/filter/v2/+/+/+/ON4IQ/#")

# TX MQTT: Listening for spots where you are the transmitter
args=("on4iq_tx.json", "TX", "pskr/filter/v2/+/+/ON4IQ/#")

📝 Japanese Prefectures File (need_prefs.txt)

To track wanted Japanese Prefectures per amateur band, create a text file named need_prefs.txt in the root directory. Add or edit your target prefectures line-by-line using the format band: Prefecture1, Prefecture2, ....
Structure and Example (need_prefs.txt):
Plaintext

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

📦 Installation & Setup

    Clone the repository:
    Bash

git clone [https://github.com/YOUR_USERNAME/ft8-monitor.git](https://github.com/YOUR_USERNAME/ft8-monitor.git)
cd ft8-monitor

Set up web templates:
Create a templates directory in the project root and place your index.html file inside. The Flask application serves this file as the main web interface:
Plaintext

    ft8-monitor/
    ├── templates/
    │   └── index.html
    ├── main.py
    ├── need_prefs.txt
    └── ...

📂 Required Databases & Files

To enable full tracking and identification features, place the following files in the project root directory:
File	Description
lotwreport.adi	ADIF export of confirmed contacts from LoTW
wsjtx_log.adi	Local log file from WSJT-X / JTDX
wanted_QTH.txt	List of target 4-digit / 6-digit Grid Locators (one per line)
need_prefs.txt	List of needed Japanese prefectures grouped by band
lotw-user-activity.csv / lotw.csv	List of active LoTW users
ja_dtb_big.csv	Database mapping Japanese callsigns to prefecture codes/names
🚀 Usage & Web Interface

    Run the application from your terminal:
    Bash

python main.py

Open your web browser and navigate to the local address to access the index.html dashboard:
Plaintext

    [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

📡 Port Reference

    8000 – Flask Web Dashboard (HTTP) – Connect here to view index.html

    8001 – WebSocket server for low-latency WSJT-X commands

    2333 / 2342 – Inbound UDP listening ports for WSJT-X / JTDX decodes

    2237 – Outbound UDP Relay port (forwards decodes to other apps like GridTracker)
