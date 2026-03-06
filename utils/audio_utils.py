import sounddevice as sd
import scipy.io.wavfile as wav

def record_audio(filename="emergency_audio.wav", duration=5, fs=16000):
    print("Recording emergency audio...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, fs, recording)
    print("Audio recording saved.")
