# 🌦️ IoT Weather-Based Music Recommendation System 🎶  
**Real-Time Weather Sensing + Machine Learning + Spotify Integration**

This project connects a **physical IoT weather station** to a **music recommendation system**.  
Based on live environmental conditions, the system selects and plays music that matches the **mood of the weather**.

---

## ⭐ Overview

The ESP32 collects live sensor data (temperature, humidity, rain intensity, pressure, UV, gas levels), determines the current **weather condition**, and sends it to a Python program over serial.  
A **KNN-based machine learning model**, trained on a dataset of songs with associated moods, picks a suitable song.  
The system then uses the **Spotify Web API** to automatically play the song.

---

## 🧠 System Architecture

```
            ┌──────────────┐
            │   Sensors     │  (DHT, BMP180, Rain, MQ Gas, UV)
            └──────┬───────┘
                   │  Live Readings
            ┌──────▼───────┐
            │    ESP32     │  → Weather Label (Clear / Rain / Storm etc.)
            └──────┬───────┘
                   │ Serial USB
            ┌──────▼─────────────────────┐
            │     Python Program         │
            │  ML Model + Feature Map    │
            └──────┬─────────────────────┘
                   │ Spotify API
            ┌──────▼───────┐
            │  Playback     │
            └──────────────┘
```

---

## 🛠️ Hardware Requirements

| Component | Purpose |
|----------|---------|
| ESP32 Dev Module | Main Controller |
| DHT11 / DHT22 | Temperature & Humidity |
| BMP180 / BMP085 | Pressure & Altitude |
| Rain Sensor | Rain Intensity Detection |
| MQ-135 / MQ-series | Gas / Air Quality |
| UV Sensor | UV Index Measurement |
| Jumper Wires + Breadboard | Prototyping setup |

---

## 🧰 Software Requirements

| Tool / Library | Use |
|----------------|-----|
| Arduino IDE | Flash ESP32 firmware |
| Python 3.x | Runtime environment |
| `pyserial` | Read sensor data over USB |
| `pandas` / `scikit-learn` | ML Model + Data Processing |
| `spotipy` | Spotify Web API playback |
| Jupyter Notebook | Model Training & Testing |

---

## 🔧 Setup Instructions

### 1. Flash ESP32 Firmware
Ensure these libraries are installed in Arduino IDE:

```
Adafruit BMP085 Library
DHT Sensor Library (by Adafruit)
Adafruit Unified Sensor
```

Upload the provided `.ino` code.

---

### 2. Connect to the Correct Serial Port (MacOS Example)

```
/dev/tty.usbserial-0001
```

Confirm by running:
```bash
ls /dev/tty.*
```

---

### 3. Install Python Dependencies

```bash
pip install pyserial spotipy pandas scikit-learn
```

---

### 4. Run the Program

```bash
jupyter notebook
```

Open the `.ipynb` file and run the main execution cell.

---

## 🎯 Weather Classification Logic

| Sensor Input | Interpreted Result |
|-------------|------------------|
| Low rain + High UV | Clear / Sunny |
| Medium rain | Light / Moderate Rain |
| High rain + Gas Spike | Thunderstorm |
| Low UV + No rain | Cloudy |

---

## 🎶 Music Recommendation Logic

The ML model considers:
- **Weather Condition (Label)**
- **User Popularity Preference (0–100)**

The system selects songs matching:
- Mood alignment
- Tempo & genre consistency
- Desired popularity / trend score

---

## 📡 Example Data Output (from ESP32)

```
28.8,59.0,924.8,763.1,85.0,4029,1356,Light Rain
```

Format:
```
Temperature, Humidity, Pressure, Altitude, Rain%, Gas, UV, Weather
```

---

## 🚀 Features

- Real-time weather interpretation
- Automatic mood-based song selection
- Smooth Spotify playback integration
- Fully customizable thresholds & ML tuning

---

## 🔮 Future Enhancements

- Bluetooth mode (no cable needed)
- Mobile App UI for remote control
- Neural Network-based music emotional mapping
- Local playlist integration

---

## 👤 Author

**Ayon Aryan**  
IoT Engineer • ML Developer • Android Developer
ayonaryan5@gmail.com

---

## 📝 License

This project is released under the **MIT License** — free for modification and contribution.

---

## ⭐ If You Like This Project
Consider starring ⭐ the repository to support ongoing improvements!
