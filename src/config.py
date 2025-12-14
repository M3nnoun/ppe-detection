import torch

MODEL_PATH = "models/best.pt"
CONF_THRESHOLD = 0.25
IMG_SIZE = 640
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
UPLOAD_FOLDER = "static/uploads"
