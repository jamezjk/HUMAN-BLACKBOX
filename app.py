import tkinter as tk
from tkinter import messagebox
import threading
import os
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import time
from models.yamnet_model import predict_sound
from utils.alert import trigger_emergency

class HumanBlackboxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Human Blackbox Emergency AI")
        self.root.geometry("600x600")

        self.is_monitoring = False
        self.false_positive_cancelled = False

        title = tk.Label(root, text="Human Blackbox Emergency AI", font=("Helvetica", 20, "bold"))
        title.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Idle", font=("Helvetica", 16))
        self.status_label.pack(pady=10)

        buttons_frame = tk.Frame(root)
        buttons_frame.pack(pady=10)

        self.start_button = tk.Button(buttons_frame, text="Start Monitoring", font=("Helvetica", 14), command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = tk.Button(buttons_frame, text="Stop Monitoring", font=("Helvetica", 14), command=self.stop_monitoring, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=10)

        history_label = tk.Label(root, text="--- Detection History ---", font=("Helvetica", 14))
        history_label.pack(pady=10)

        self.history_text = tk.Text(root, height=15, width=70)
        self.history_text.pack(pady=10)
        self.history_text.config(state="disabled")

        open_logs_button = tk.Button(root, text="Open Logs Folder", font=("Helvetica", 14), command=self.open_logs_folder)
        open_logs_button.pack(pady=10)
        # Manual emergency button for simulation/testing
        simulate_button = tk.Button(root, text="Simulate Emergency", font=("Helvetica", 14),
                            command=lambda: self.show_emergency_popup("Gunshot", 0.95))
        simulate_button.pack(pady=10)


    def start_monitoring(self):
        self.is_monitoring = True
        self.status_label.config(text="Status: Listening...")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        threading.Thread(target=self.monitoring_loop, daemon=True).start()

    def stop_monitoring(self):
        self.is_monitoring = False
        self.status_label.config(text="Status: Idle")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def monitoring_loop(self):
        fs = 16000
        duration = 5
        emergency_sounds = {
            "gunshot", "Explosion", "Scream", "Screaming", "Bang", "Whoop", "Glass breaking",
            "Car crash", "Tires screeching", "Police siren", "Ambulance siren",
            "Fire alarm", "Dog barking", "Fistfight", "Crowd panic", "Thunder",
            "Crying", "Distress whistle", "Building collapse"
        }
        cooldown_period = 10
        last_alert_time = 0

        while self.is_monitoring:
            try:
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
                if not os.path.exists("logs"):
                    os.makedirs("logs")
                temp_file = "logs/temp_listen.wav"
                wav.write(temp_file, fs, recording)

                sr, audio = wav.read(temp_file)
                if len(audio.shape) > 1:
                    audio = np.mean(audio, axis=1)

                top_sounds = predict_sound(audio, sr)

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
                            last_alert_time = current_time
                self.history_text.config(state="disabled")
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error in Monitoring: {e}")

    def open_logs_folder(self):
        try:
            logs_path = os.path.abspath("logs")
            os.startfile(logs_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open logs folder:\n{e}")

    def show_emergency_popup(self, sound_label, confidence):
        self.false_positive_cancelled = False
        popup = tk.Toplevel()
        popup.title("🚨 Emergency Detected!")
        popup.geometry("400x250")

        label = tk.Label(popup, text=f"Sound: {sound_label}\nConfidence: {confidence:.2f}\n\nSend SOS Alert?", font=("Helvetica", 14))
        label.pack(pady=20)

        cancel_button = tk.Button(popup, text="False Positive - Cancel Emergency", font=("Helvetica", 12), command=lambda: self.cancel_emergency(popup))
        cancel_button.pack(pady=10)

        popup.after(30000, lambda: self.check_and_send_emergency(sound_label, confidence, popup))

    def cancel_emergency(self, popup):
        self.false_positive_cancelled = True
        popup.destroy()
        self.status_label.config(text="Status: Monitoring (Cancelled Emergency)")
        messagebox.showinfo("Cancelled", "Emergency Cancelled Successfully!")

    def check_and_send_emergency(self, sound_label, confidence, popup):
        popup.destroy()
        if not self.false_positive_cancelled:
            self.status_label.config(text=f"Status: 🚨 Emergency Sent: {sound_label}")
            trigger_emergency(sound_label, confidence)
            messagebox.showinfo("✅ Email Sent", "Emergency Email Sent Successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = HumanBlackboxApp(root)
    root.mainloop()
