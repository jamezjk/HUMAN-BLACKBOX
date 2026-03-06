import sounddevice as sd
import scipy.io.wavfile as wav
import cv2
import smtplib
import time
import geocoder
from geopy.geocoders import Nominatim
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def get_current_location():
    try:
        g = geocoder.ip('me')  # Get public IP-based location
        lat, lng = g.latlng
        return lat, lng
    except Exception as e:
        print(f"Failed to get GPS coordinates: {e}")
        return None, None

def get_address(lat, lng):
    try:
        geolocator = Nominatim(user_agent="human_blackbox_ai")
        location = geolocator.reverse((lat, lng), exactly_one=True)
        return location.address
    except Exception as e:
        print(f"Failed to reverse geocode: {e}")
        return "Unknown Address"

def trigger_emergency(sound_label, confidence):
    # Step 1: Record 30s Audio
    print("🔴 Recording 30-second emergency audio...")
    fs = 16000
    duration = 30
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write("emergency_audio.wav", fs, recording)
    print("✅ Audio recorded and saved.")

    # Step 2: Capture Photo
    print("📸 Capturing emergency photo...")
    cam = cv2.VideoCapture(0)
    time.sleep(2)  # Warm-up camera
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("emergency_photo.jpg", frame)
    cam.release()
    print("✅ Photo captured and saved.")

    # Step 3: Get GPS Coordinates and Address
    print("🌍 Fetching GPS location and address...")
    lat, lng = get_current_location()
    address = get_address(lat, lng)
    location_info = f"📍 Location Coordinates: {lat}, {lng}\n📍 Address: {address}"
    print("✅ Location fetched.")

    # Step 4: Send Email with Attachments
    print("✉️ Sending emergency email with attachments...")
    sender_email = "jkclickzzz@gmail.com"
    receiver_email = "jamesjk1403@gmail.com"
    password = "nfld utwa bbuw vnar"  # <<< App Password (no spaces)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚨 EMERGENCY DETECTED: {sound_label} at {lat}, {lng}"

    # Compose the body with location info
    body = f"Emergency sound '{sound_label}' detected with confidence {confidence:.2f}.\n\n{location_info}"
    msg.attach(MIMEText(body, 'plain'))

    # Attach audio
    with open("emergency_audio.wav", "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= emergency_audio.wav")
        msg.attach(part)

    # Attach photo
    with open("emergency_photo.jpg", "rb") as photo:
        photo_part = MIMEBase('application', 'octet-stream')
        photo_part.set_payload(photo.read())
        encoders.encode_base64(photo_part)
        photo_part.add_header('Content-Disposition', f"attachment; filename= emergency_photo.jpg")
        msg.attach(photo_part)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("✅ Emergency email sent successfully with attachments and location!")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")
