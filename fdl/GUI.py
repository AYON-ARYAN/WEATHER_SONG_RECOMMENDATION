import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import io, urllib.parse, random, requests, webbrowser, re, time, serial
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ------------------ Setup ------------------
df = pd.read_csv("spotify_weather_data.csv")

preprocessor = ColumnTransformer([
    ("weather", OneHotEncoder(handle_unknown="ignore"), ["Weather"]),
    ("popularity", StandardScaler(), ["Popularity"])
])

model = NearestNeighbors(n_neighbors=10, metric="euclidean")

knn_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

knn_pipeline.fit(df[["Weather", "Popularity"]])

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="e589066a795c4e59b1f6cd5596fe2a17",
    client_secret="525f39dd24ad4bfeaef7656b7a2d4008",
    redirect_uri="http://127.0.0.1:8889/callback",
    scope="user-modify-playback-state,user-read-playback-state,user-read-currently-playing"
))

# ------------------ ESP32 Serial Function ------------------
def get_weather_from_esp32(port="/dev/cu.usbserial-0001", baud=115200, timeout=10):
    weather_keywords = ["Fog", "Mist", "Rain", "Snow", "Drizzle", "Thunderstorm", "Clouds", "Clear"]
    ser = serial.Serial(port, baudrate=baud, timeout=1)
    start_time = time.time()
    detected_weather = None
    weather_data_line = ""

    while time.time() - start_time < timeout:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            continue
        if any(keyword in line for keyword in ["Temperature", "Humidity", "Pressure"]):
            weather_data_line = line
        for w in weather_keywords:
            if re.search(rf"\b{w}\b", line, re.IGNORECASE):
                detected_weather = w
                break
        if detected_weather:
            break

    ser.close()
    return detected_weather or "Clear", weather_data_line

# ------------------ Recommendation Function ------------------
def ml_recommend_song(weather_input, popularity_score):
    input_df = pd.DataFrame({"Weather": [weather_input], "Popularity": [popularity_score]})
    preprocessor = knn_pipeline.named_steps["preprocessor"]
    model = knn_pipeline.named_steps["model"]
    transformed_input = preprocessor.transform(input_df)
    distances, indices = model.kneighbors(transformed_input)
    random_index = random.choice(indices[0])
    rec = df.iloc[random_index]

    image_url = None
    for col in df.columns:
        if df[col].astype(str).str.startswith("http").any():
            image_url = rec[col]
            break

    query = f"{rec['Track Name']} {rec['Artist']}"
    results = sp.search(q=query, type='track', limit=1)

    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[track_uri])
    else:
        webbrowser.open(f"https://open.spotify.com/search/{urllib.parse.quote(query)}")

    return rec, image_url

# ------------------ GUI ------------------
root = tk.Tk()
root.title("Moodify: Weather-Based Song Recommender")

# --- Window setup ---
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
window_w = int(screen_w / 2)
window_h = int(screen_h / 2)
pos_x = int((screen_w - window_w) / 2)
pos_y = int((screen_h - window_h) / 2)

root.geometry(f"{window_w}x{window_h}+{pos_x}+{pos_y}")
root.configure(bg="#EDE7F6")
root.resizable(True, True)

# --- Logo ---
try:
    logo_img = Image.open("logo-spotify-icone-png-violet.png").resize((80, 80))
    logo_tk = ImageTk.PhotoImage(logo_img)
    tk.Label(root, image=logo_tk, bg="#EDE7F6").pack(pady=(10, 5))
except:
    pass

# --- Title ---
app_title = tk.Label(
    root,
    text="🎧 Moodify 🎶\nWeather-Based Song Recommender",
    font=("Impact", 26, "bold"),
    bg="#EDE7F6",
    fg="#2E1A47",
    justify="center"
)
app_title.pack(pady=(0, 8))

# --- Weather Info Frame ---
weather_frame = tk.Frame(root, bg="#D1C4E9", bd=2, relief="flat", highlightbackground="#7E57C2", highlightthickness=2)
weather_frame.pack(pady=6, padx=30, fill="x")

weather_title = tk.Label(weather_frame, text="🌤 Current Weather Details 🌤", font=("Helvetica", 13, "bold"), bg="#D1C4E9", fg="#311B92")
weather_title.pack(pady=3)

weather_details_label = tk.Label(weather_frame, text="", font=("Helvetica", 11, "bold"), bg="#D1C4E9", fg="#1A237E", justify="left")
weather_details_label.pack(pady=2)

weather_type_label = tk.Label(weather_frame, text="", font=("Helvetica", 12, "bold"), bg="#D1C4E9", fg="#4A148C")
weather_type_label.pack(pady=3)

# --- Output Display ---
output_frame = tk.Frame(root, bg="#EDE7F6")
output_frame.pack(pady=5)

album_art_label = tk.Label(output_frame, bg="#EDE7F6")
album_art_label.pack(pady=5)

song_info_label = tk.Label(output_frame, text="", font=("Arial Black", 16, "bold"), bg="#EDE7F6", fg="#111111", justify="center")
song_info_label.pack(pady=8)

# --- Main function ---
def detect_weather_and_play():
    messagebox.showinfo("ESP32", "Reading live weather data from ESP32...")
    weather, data_line = get_weather_from_esp32()
    weather_details_label.config(text=f"{data_line}")
    weather_type_label.config(text=f"Detected Weather: {weather}")

    try:
        popularity = float(simpledialog.askstring("Popularity", "Enter desired popularity score (0–100):"))
    except:
        messagebox.showwarning("Invalid Input", "Popularity score must be a number.")
        return

    rec, img_url = ml_recommend_song(weather, popularity)
    song_info_label.config(
        text=f"🎵 {rec['Track Name']}\n👤 {rec['Artist']}\n🌤 Weather: {rec['Weather']}\n🔥 Popularity: {rec['Popularity']:.1f}"
    )

    if img_url:
        try:
            img = Image.open(io.BytesIO(requests.get(img_url).content))
            img = img.resize((350, 350))
            img_tk = ImageTk.PhotoImage(img)
            album_art_label.config(image=img_tk)
            album_art_label.image = img_tk
        except:
            song_info_label.config(text="(Could not load album art.)")

# --- Button Style ---
style = ttk.Style()
style.theme_use('clam')
style.configure("Dark.TButton", font=("Helvetica", 14, "bold"), padding=10, foreground="white", background="#1A237E", borderwidth=0, relief="flat")
style.map("Dark.TButton", background=[("active", "#311B92")])

detect_btn = ttk.Button(root, text="Recommend me a song, Moodify!!", style="Dark.TButton", command=detect_weather_and_play)
detect_btn.pack(pady=10)

root.mainloop()
