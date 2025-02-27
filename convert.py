import tensorflow as tf

# Create & save a dummy model for testing
model = tf.keras.Sequential([tf.keras.layers.Dense(1, input_shape=(1,))])
model.save(r"C:\Users\kunku\OneDrive\Desktop\HUMAN BLACKBOX\sound_detection.h5")

print("Model saved successfully!")
