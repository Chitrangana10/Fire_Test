# 🔥 Fire Detection System (Edge AI + 5G Camera)

This project implements a real-time **fire detection system** using a YOLOv5 model deployed on a NiralOS Edge Server VM. The system processes live RTSP video from a 5G camera and sends results to the **Pulse5G dashboard application**.

---

## 🚀 Features

* 🔴 Real-time fire detection using YOLOv5
* 📡 Live RTSP stream from 5G camera
* ⚡ Edge inference on NiralOS VM
* 🎥 Live video streaming
* 🔔 Real-time alert updates
* 📱 Integrated with Pulse5G dashboard app

---

## 🏗️ System Architecture

5G Camera (RTSP)
↓
Edge Server VM (NiralOS)
↓
YOLOv5 Fire Model
↓
FastAPI Backend
↓
Pulse5G Dashboard

---

## 📦 Requirements

* Python 3.10+
* NiralOS Edge Server VM
* 5G Camera
* Router access

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd Fire_Test
```

---

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install fastapi "uvicorn[standard]"
pip install torch torchvision opencv-python numpy
pip install -r yolov5/requirements.txt
```

---

### 4. 🔍 Get Camera IP (IMPORTANT)

Open router dashboard:

```text
https://192.168.128.1/
```

Steps:

* Login to router
* Go to **Connected Devices / DHCP Clients**
* Find:

  * IP Camera / IPC / Unknown device
* Copy IP (example: `10.101.0.7`)

---

### 5. Configure RTSP Stream

```python
RTSP_URL = "rtsp://admin:admin123@<CAMERA_IP>:554/avstream/channel=1/stream=1.sdp"
```

---

### 6. Run the System

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📱 Pulse5G Mobile App

Download the dashboard application:

👉 https://drive.google.com/file/d/1kFMsG4k8FUv-SZJrVW9TY7537LxXbxvN/view?usp=drive_link

The app provides:

* 🎥 Live camera feed
* 🔔 Real-time fire alerts
* 📊 Detection confidence and timestamps

---

## 🧪 Testing

```text
http://127.0.0.1:8000/video
```

---

## ⚠️ Notes

* Ensure camera & VM are on same network
* Use VM IP (172.16.0.x) in dashboard
* Do not use 127.0.0.1 externally

---

## 🚀 Outcome

Real-time fire detection with instant alerts displayed on Pulse5G mobile dashboard.
