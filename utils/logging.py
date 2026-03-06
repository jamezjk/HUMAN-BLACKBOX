import logging
import datetime

logging.basicConfig(filename="logs/emergency_detection.log", level=logging.INFO)

def log_detection(sound_label, confidence):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] Detected: {sound_label} (Confidence: {confidence:.2f})"
    logging.info(log_message)