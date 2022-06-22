import io

import torch
from PIL import Image

md_model = torch.hub.load("ultralytics/yolov5", "custom", path='./mdyolo.pt',
                          force_reload=True, autoshape=True)  # force_reload = recache latest code
md_model.eval()
print("Model in evaluation mode")


def get_prediction_mdyolo(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    results = md_model(img, size=640)
    return results


mt_model = torch.hub.load("ultralytics/yolov5", "custom", path='./mtyolo.pt',
                          force_reload=True, autoshape=True)  # force_reload = recache latest code
mt_model.eval()
print("Model in evaluation mode")


def get_prediction_mtyolo(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    results = mt_model(img, size=640)
    return results


def get_max_area_pred(results):
    predictions = results.pandas().xyxy[0]
    d_x = predictions['xmax'] - predictions['xmin']
    d_y = predictions['ymax'] - predictions['ymin']
    area = d_x * d_y
    predictions['area'] = area
    max_area_pred = predictions.iloc[predictions['area'].idxmax()]
    return max_area_pred
