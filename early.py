import tkinter as tk
from tkinter import messagebox
import threading
import os
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import time
from models.yamnet_model import predict_sound  # Your sound prediction model
from utils.alert import trigger_emergency  # Your emergency email/audio/photo trigger

class HumanBlackboxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Human Blackbox Emergency AI")
        self.root.geometry("600x600")
        
        self.is_monitoring = False
        
        # Title
        title = tk.Label(root, text="Human Blackbox Emergency AI", font=("Helvetica", 20, "bold"))
        title.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(root, text="Status: Idle", font=("Helvetica", 16))
        self.status_label.pack(pady=10)
        
        # Buttons Frame
        buttons_frame = tk.Frame(root)
        buttons_frame.pack(pady=10)
        
        self.start_button = tk.Button(buttons_frame, text="Start Monitoring", font=("Helvetica", 14), command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.stop_button = tk.Button(buttons_frame, text="Stop Monitoring", font=("Helvetica", 14), command=self.stop_monitoring, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=10)
        
        # Detection History Label
        history_label = tk.Label(root, text="--- Detection History ---", font=("Helvetica", 14))
        history_label.pack(pady=10)
        
        # History Text Box
        self.history_text = tk.Text(root, height=15, width=70)
        self.history_text.pack(pady=10)
        self.history_text.config(state="disabled")
        
        # Open Logs Button
        open_logs_button = tk.Button(root, text="Open Logs Folder", font=("Helvetica", 14), command=self.open_logs_folder)
        open_logs_button.pack(pady=10)

    def start_monitoring(self):
        self.is_monitoring = True
        self.status_label.config(text="Status: Listening...")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start Monitoring Thread
        threading.Thread(target=self.monitoring_loop, daemon=True).start()

    def stop_monitoring(self):
        self.is_monitoring = False
        self.status_label.config(text="Status: Idle")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def monitoring_loop(self):
        fs = 16000  # Sampling rate
        duration = 5  # Seconds per listening window
        emergency_sounds = {
            "gunshot", "Explosion", "Scream", "Screaming", "Bang", "Whoop", "Glass breaking",
            "Car crash", "Tires screeching", "Police siren", "Ambulance siren",
            "Fire alarm", "Dog barking", "Fistfight", "Crowd panic", "Thunder",
            "Crying", "Distress whistle", "Building collapse"
        }
        cooldown_period = 10  # 1 minute cooldown between emergencies
        last_alert_time = 0

        while self.is_monitoring:
            try:
                # Step 1: Record audio
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
                if not os.path.exists("logs"):
                    os.makedirs("logs")
                temp_file = "logs/temp_listen.wav"
                wav.write(temp_file, fs, recording)

                # Step 2: Predict sound
                sr, audio = wav.read(temp_file)
                if len(audio.shape) > 1:
                    audio = np.mean(audio, axis=1)  # Convert stereo to mono if needed

                top_sounds = predict_sound(audio, sr)

                # Step 3: Check detections
                self.history_text.config(state="normal")
                for sound_label, confidence in top_sounds:
                    now = time.strftime("%H:%M:%S")
                    log_line = f"{sound_label} ({confidence:.2f}) at {now}\n"
                    self.history_text.insert(tk.END, log_line)
                    self.history_text.see(tk.END)

                    if sound_label in emergency_sounds and confidence > 0.1:
                        current_time = time.time()
                        if current_time - last_alert_time > cooldown_period:
                            print(f"🚨 Emergency Detected: {sound_label} ({confidence:.2f})")
                            self.status_label.config(text=f"Status: 🚨 Emergency: {sound_label}")
                            self.show_emergency_popup(sound_label, confidence)
                            trigger_emergency(sound_label, confidence)
                            last_alert_time = current_time
                self.history_text.config(state="disabled")
                time.sleep(2)  # Small delay before next listening window

            except Exception as e:
                print(f"❌ Error in Monitoring: {e}")

    def open_logs_folder(self):
        try:
            logs_path = os.path.abspath("logs")
            os.startfile(logs_path)  # For Windows
        except Exception as e:
            messagebox.showerror("Error", f"Could not open logs folder:\n{e}")

    def show_emergency_popup(self, sound_label, confidence):
        messagebox.showwarning(
            "🚨 Emergency Detected!",
            f"Sound: {sound_label}\nConfidence: {confidence:.2f}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = HumanBlackboxApp(root)
    root.mainloop()
