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
JSON_FILE_PATH = r"C:\Program Files\Mosquitto\on4iqx_rx.json"  # Adjust Windows path accordingly - it is created automatically!
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
```bash
ft8-monitor/
├── templates/
│   └── index.html
├── flask_map16.py
├── need_prefs.txt
├── wanted_QTH.txt
├── lotwreport.adi
├── wsjtx_log.adi
├── lotw.csv
├── ja_dtb_big.csv
└── requirements.txt
```


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

## 8000 – Flask Web Interface (HTTP) – Connect here to view index.html

8001 – WebSocket server for low-latency communication with WSJT-X

2333 / 2342 – Inbound UDP listening ports for WSJT-X / JTDX decodes

## 2237 – Outbound UDP Relay port (forwards decodes to secondary apps like GridTracker or your Main Logger - using Winlog32 for UDP logging)


### 🔗 Advanced Setup: Sharing wsjtx_log.adi Across Multiple Applications

If you are running both WSJT-X and JTDX simultaneously or want this script to instantly read logs from another directory without duplicating files, you can create an NTFS Hardlink.

This allows multiple programs to read and write to the exact same log file in real time.
Using Link Shell Extension https://schinagl.priv.at/nt/hardlinkshellext/linkshellextension.html (GUI Method - Windows):

    Download and install Link Shell Extension.

    Navigate to your primary log directory (e.g., %LOCALAPPDATA%\WSJT-X).

    Right-click your original wsjtx_log.adi file and select Pick Link Source.

    Open your ft8-monitor project directory (or JTDX directory).

    Right-click on an empty space, select Drop As... -> Hardlink.

Using Windows Command Prompt (CLI Method):

Alternatively, you can create a hardlink natively via cmd (run as Administrator):

mklink /H "C:\path\to\ft8-monitor\wsjtx_log.adi" "%LOCALAPPDATA%\WSJT-X\wsjtx_log.adi"

# 🌐 Web Dashboard Frontend (`index.html`)

The frontend component of the FT8 Real-Time Monitor is a single-page interactive web application powered by **HTML5**, **Bootstrap 5**, **Leaflet.js**, and **Socket.IO**. It presents real-time digital mode spots, live maps, geodesic propagation paths, and instant alert notifications for targeted awards.

---

## ✨ Web Interface Highlights

- **Dark Theme Interface:** Optimized for high-contrast viewing with a low-light UI suited for amateur radio operation environments.
- **Interactive Leaflet Map:**
  - Dynamic map rendering using OpenStreetMap tiles.
  - Automatic station location pinpointing based on Maidenhead Grid Locators (supports 4-digit and 6-digit precision).
  - Great-circle geodesic line drawing (`Leaflet.Geodesic`) showing true propagation paths between your home station and remote spots.
- **Audio & Visual Alerts:**
  - Pop-up alert banners with auto-dismiss timers for high-priority targets (e.g., needed Japanese Prefectures).
  - Integrated HTML5 Audio Synthesizer (`AudioContext`) triggering real-time sound notifications.
- **Dynamic Mode Switching:**
  - **⚡ FT8 Monitor:** Real-time stream of incoming decodes from WSJT-X / JTDX. Highlights missing Japanese prefectures with action buttons linking to QRZ.com profiles.
  - **📥 RX (PSK) & 📤 TX (PSK):** Displays spots reported directly to/from PSKReporter.
- **Filtering & Controls:**
  - Multi-band selector (`160m` through `6m`) for quick frequency filtering.
  - One-click canvas reset (`Clear` button) to clean markers and history tables.

---

## 💻 Tech Stack & Dependencies (CDN)

The HTML template imports all required frontend libraries directly via public CDNs:

| Library | Version | Purpose |
| :--- | :--- | :--- |
| **Bootstrap** | 5.3.0 | Structural layout, responsive grid, and dark theme components |
| **Leaflet.js** | 1.9.4 | Interactive map rendering and marker layer management |
| **Leaflet.Geodesic** | 2.7.2 | Great-circle propagation line drawing |
| **Socket.IO Client** | 4.7.2 | Real-time WebSocket event handling with the Flask backend |

---

## 🧩 Template Architecture

The file is structured to be rendered seamlessly by Flask's Jinja2 template engine:

- **Jinja2 Variables:**
  - `{{ moj_pozivni }}` – Injected station callsign (e.g., `ON4IQX`).
  - `{{ moj_lokator }}` – Injected QTH Maidenhead Grid Locator (e.g., `JO20AR`).
- **Real-Time Data Flow:**
  - Listens for `novi_spot` (PSKReporter MQTT streams).
  - Listens for `novi_ft8_decode` (WSJT-X UDP streams).
  - Auto-cleans expired map markers and old entries (>5 minutes) to conserve memory.

---

## 📄 License & Copyright

This web dashboard template is released under the **MIT License**.
This script, UI layout and frontend code software are free to use, modify, share, and redistribute for both personal and non-commercial amateur radio operations.
---
Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## MQTT command prompt examples:
mosquitto_sub -h mqtt.pskreporter.info -t "pskr/filter/v2/+/+/9A5CW/+/+/+/+/+" > 9a5cw.json

mosquitto_sub -h mqtt.pskreporter.info -t "pskr/filter/v2/6m/+/+/+/+/+/+/+"

Scripts details: RX/TX MQTT from Pskreporter /FT8 my decodes + Maps

```

<img width="1907" height="944" alt="ft8" src="https://github.com/user-attachments/assets/c5f467bd-7d5d-403e-a3d4-1ffd2af8fa26" />

<img width="1899" height="935" alt="rx" src="https://github.com/user-attachments/assets/94c25baf-36dc-49b6-8be7-2f43b3edef90" />

<img width="1891" height="959" alt="tx" src="https://github.com/user-attachments/assets/a1f3e2c9-bd6e-45a3-b9ff-e32d98920680" />

<img width="942" height="628" alt="yamaguchi" src="https://github.com/user-attachments/assets/815300bd-1a2c-40b2-b9c9-21fe3a6ba652" />

<img width="1875" height="937" alt="new_prefekture_alert" src="https://github.com/user-attachments/assets/ce1eae2f-6773-43b2-b337-e63888b799ed" />

<img width="936" height="642" alt="prefs" src="https://github.com/user-attachments/assets/2eef359b-2ecf-4287-8653-f72e73c6e5d1" />

<img width="1910" height="998" alt="jtdx_in_action" src="https://github.com/user-attachments/assets/af8a255d-5a3c-4d8b-9365-065d9c3cd3aa" />












   






