import time
from utils.alert import trigger_emergency
from utils.logging import log_detection
from utils.audio_utils import record_audio
from models.yamnet_model import predict_sound
import scipy.io.wavfile as wav

# Emergency sounds to detect
emergency_sounds = {
    "gunshot", "Explosion", "Scream", "Glass breaking",
    "Car crash", "Tires screeching", "Police siren", "Ambulance siren",
    "Fire alarm", "Dog barking", "Fistfight", "Crowd panic", "Thunder",
    "Crying", "Distress whistle", "Building collapse"
}

# Main loop
last_alert_time = 0
cooldown_period = 5  # 60 seconds

while True:
    # 1. Record Audio
    record_audio()

    # 2. Load recorded audio
    sr, audio = wav.read("emergency_audio.wav")

    # 3. Predict Sounds
    top_sounds = predict_sound(audio, sr)

    print("\n🔊 Detected Sounds:")
    for sound_label, confidence in top_sounds:
        print(f"- {sound_label} (Confidence: {confidence:.2f})")

        if sound_label in emergency_sounds and confidence > 0.1:
            current_time = time.time()
            if current_time - last_alert_time > cooldown_period:
                print("\n🚨 EMERGENCY DETECTED! ALERTING SYSTEM 🚨")
                trigger_emergency(sound_label, confidence)  # <-- FIXED HERE
                log_detection(sound_label, confidence)
                last_alert_time = current_time
