# src/detector.py
from ultralytics import YOLO
from src.config import MODEL_PATH, DEVICE

model = YOLO(MODEL_PATH).to(DEVICE)

def detect(source):
    return model(source, conf=0.25, imgsz=640)
