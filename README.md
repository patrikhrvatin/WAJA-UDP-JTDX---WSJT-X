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

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/ft8-monitor.git](https://github.com/YOUR_USERNAME/ft8-monitor.git)
   cd ft8-monitor
