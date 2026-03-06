import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import librosa  # You need this for resampling

# Load YAMNet model
yamnet_model_handle = "https://tfhub.dev/google/yamnet/1"
model = hub.load(yamnet_model_handle)

# Load class labels
class_map_path = "data/yamnet_class_map.csv"

with open(class_map_path, 'r') as f:
    lines = f.read().splitlines()
    if lines[0].startswith("index,mid,display_name"):
        lines = lines[1:]
    class_names = [line.split(',')[2] for line in lines]

def predict_sound(audio_data, sr):
    # 1. Normalize and Resample to 16000Hz
    if sr != 16000:
        audio_data = librosa.resample(audio_data.astype(float), orig_sr=sr, target_sr=16000)
        sr = 16000

    # 2. Ensure waveform is float32 between [-1.0, 1.0]
    waveform = audio_data / np.max(np.abs(audio_data))
    waveform = tf.convert_to_tensor(waveform, dtype=tf.float32)

    # 3. Run through YAMNet model
    scores, embeddings, spectrogram = model(waveform)

    # 4. Average scores across time frames
    mean_scores = tf.reduce_mean(scores, axis=0)

    # 5. Get top 3 predictions
    top_indices = tf.argsort(mean_scores, direction='DESCENDING')[:3]
    top_labels = [class_names[i] for i in top_indices.numpy()]
    top_confidences = [mean_scores.numpy()[i] for i in top_indices.numpy()]

    return list(zip(top_labels, top_confidences))  # Return [(label, confidence), ...]
