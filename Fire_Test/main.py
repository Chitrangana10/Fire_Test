import cv2
import os
import time
import asyncio
import torch
import numpy as np
import sys

from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse

# ------------------ RTSP FIX ------------------
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

RTSP_URL = "rtsp://admin:admin123@10.101.0.2:554/avstream/channel=1/stream=1.sdp"

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ADD THIS PART:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
clients = []

latest_frame = None

# ------------------ GLOBAL ALERT ------------------
latest_alert = {
    "event": "none",
    "confidence": 0.0,
    "timestamp": 0
}

# ------------------ PATH SETUP (NESTED FIX) ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

YOLO_PATH = os.path.join(BASE_DIR, "yolov5")
MODEL_PATH = os.path.join(YOLO_PATH, "fire_best.pt")

# 🔥 CRITICAL: Make yolov5 root
sys.path.insert(0, YOLO_PATH)

# ------------------ YOLO IMPORTS ------------------
from models.common import DetectMultiBackend
from utils.general import non_max_suppression
from utils.torch_utils import select_device

device = select_device('0' if torch.cuda.is_available() else 'cpu')

model = DetectMultiBackend(MODEL_PATH, device=device)
model.eval()

print("🔥 YOLOv5 model loaded successfully")

# ------------------ WEBSOCKET ------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        if websocket in clients:
            clients.remove(websocket)

async def broadcast(data):
    for client in clients.copy():
        try:
            await client.send_json(data)
        except:
            clients.remove(client)

# ------------------ DETECTION FUNCTION ------------------
def run_detection(frame):
    try:
        img = cv2.resize(frame, (640, 640))
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(device)
        img = img.float() / 255.0
        img = img.unsqueeze(0)

        pred = model(img)
        pred = non_max_suppression(pred, 0.5, 0.45)

        fire_detected = False
        confidence = 0.0

        for det in pred:
            if len(det):
                for *xyxy, conf, cls in det:
                    label = model.names[int(cls)]
                    if label.lower() == "fire":
                        fire_detected = True
                        confidence = float(conf)
                        break

        return fire_detected, confidence

    except Exception as e:
        print(f"❌ Detection error: {e}")
        return False, 0.0

# ------------------ DETECTION LOOP ------------------
async def detect_loop():
    global latest_frame, latest_alert

    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    last_sent = 0

    while True:
        for _ in range(2):
            cap.grab()

        ret, frame = cap.read()

        if not ret:
            print("⚠️ Stream failed, reconnecting...")
            cap.release()
            await asyncio.sleep(1)
            cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            continue

        frame = cv2.resize(frame, (640, 480))
        latest_frame = frame

        fire_detected, confidence = run_detection(frame)

        if fire_detected and time.time() - last_sent > 2:
            latest_alert = {
                "event": "fire",
                "confidence": confidence,
                "timestamp": time.time()
            }

            await broadcast(latest_alert)

            print(f"🔥 Fire detected: {confidence:.2f}")
            last_sent = time.time()

        await asyncio.sleep(0.01)

# ------------------ VIDEO STREAM ------------------
def generate_frames():
    global latest_frame

    while True:
        if latest_frame is None:
            continue

        _, buffer = cv2.imencode('.jpg', latest_frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# ------------------ REST API ------------------
@app.get("/")
def get_alert():
    return latest_alert

# ------------------ STARTUP ------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(detect_loop())
