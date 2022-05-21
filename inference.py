import torch
from PIL import Image
import io


model = torch.hub.load("ultralytics/yolov5", "custom", path='./best.pt', force_reload=True, autoshape=True)  # force_reload = recache latest code
model.eval()
print("Model in evaluation mode")

def get_prediction(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    results = model(img, size=640)
    return results
