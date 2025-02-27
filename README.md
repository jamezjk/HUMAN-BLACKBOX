# HUMAN-BLACKBOX
Human Black Box – AI-Powered Life Logger &amp; Crash Recorder

# 🚀 Human Black Box – AI-Powered Life Logger & Crash Recorder

## 📌 Overview
The **Human Black Box** is an AI-driven wearable device designed to record critical real-time data, detect emergencies, and notify emergency contacts. It works like a black box for humans, ensuring safety in accidents, attacks, and medical crises.

## 🌟 Features
- **🔴 Continuous Monitoring:** Captures **audio, video, location, and biometrics**.
- **⚠️ AI-Powered Emergency Detection:** Uses deep learning models (YAMNet, GRU, and CNN) to detect accidents, falls, or distress situations.
- **📡 Auto-Save & Alert System:** Stores last 60s of data and alerts emergency contacts.
- **🔊 YAMNet for Audio Analysis:** Detects dangerous sounds like **screams, explosions, sirens, and crashes**.
- **📶 ONNX/TFLite Deployment:** Optimized AI models for real-time processing.
- **📱 Mobile App (React Native):** Users can configure alerts, check logs, and access recordings.
- **🔗 FastAPI Backend & Firebase:** Secure, real-time data transmission with multi-channel alerts.

## 🎯 System Architecture
1. **Wearable Device** – Captures video, audio, location, and biometric data.
2. **AI Model (YAMNet + CNN/GRU)** – Detects emergencies and triggers alerts.
3. **FastAPI Backend** – Handles event processing and data storage.
4. **Firebase + Twilio Integration** – Sends **real-time alerts via call, SMS, WhatsApp, and email**.
5. **Mobile App (React Native)** – Allows users to view logs, configure alerts, and access emergency data.

## 🛠️ Tech Stack
- **AI Models:** YAMNet, GRU, CNN, ONNX/TFLite
- **Backend:** FastAPI, Firebase, PostgreSQL
- **Frontend:** React Native (Mobile), Spline (3D UI)
- **Communication:** Twilio (Call/SMS), WhatsApp API, Firebase Push Notifications

## 🚀 Setup Instructions
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourrepo/human-blackbox.git
cd human-blackbox
