import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sounddevice as sd
import librosa
import os

# Load YAMNet model
yamnet_model_handle = "https://tfhub.dev/google/yamnet/1"
model = hub.load(yamnet_model_handle)

# Load class labels
class_map_path = "yamnet_class_map.csv"  # Ensure this file is in the same directory

if not os.path.exists(class_map_path):
    raise FileNotFoundError(f"Class map file not found at {class_map_path}. Please download it manually.")

# Read class labels (handling header)
with open(class_map_path, 'r') as f:
    lines = f.read().splitlines()
    
    if lines[0].startswith("index,mid,display_name"):  # Skip header if present
        lines = lines[1:]

    class_names = [line.split(',')[2] for line in lines]

# Emergency sounds to detect
emergency_sounds = {
    "gunshot", "Explosion", "Scream", "Glass breaking",
    "Car crash", "Tires screeching", "Police siren", "Ambulance siren",
    "Fire alarm", "Dog barking", "Fistfight", "Crowd panic", "Thunder",
    "Crying", "Distress whistle", "Building collapse"
}

# Function to record live audio (ensure correct format)
def record_audio(duration=3, sr=16000):
    print("\n🎤 Listening for emergency sounds...")
    audio_data = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype='float32')
    sd.wait()

    # Convert to mono and resample if needed
    audio_data = np.squeeze(audio_data)  # Remove extra dimensions

    # Normalize the audio
    audio_data = audio_data / np.max(np.abs(audio_data))  # Scale between -1 and 1

    return audio_data, sr

# Function to process sound and predict top 3 sounds
def predict_sound(audio_data, sr):
    waveform = np.squeeze(audio_data)  # Remove extra dimensions
    scores, embeddings, spectrogram = model(waveform)

    # Get top 3 predictions
    top_indices = np.argsort(scores.numpy()[0])[-3:][::-1]
    top_labels = [class_names[i] for i in top_indices]
    top_confidences = [scores.numpy()[0][i] for i in top_indices]

    return list(zip(top_labels, top_confidences))  # Return top 3

# Run detection in a loop
while True:
    audio, sr = record_audio()
    top_sounds = predict_sound(audio, sr)

    print("\n🔊 Detected Sounds:")
    for sound_label, confidence in top_sounds:
        print(f"- {sound_label} (Confidence: {confidence:.2f})")

        if sound_label in emergency_sounds and confidence > 0.6:
            print("\n🚨 EMERGENCY DETECTED! ALERTING SYSTEM 🚨")

model.save("sound_detection.h5")
model.save("sound_detection.h5")
