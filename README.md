# Yolov5 object detection model deployment using flask
This repo contains example apps for exposing the [yolo5](https://github.com/ultralytics/yolov5) object detection model from [pytorch hub](https://pytorch.org/hub/ultralytics_yolov5/) via a [flask](https://flask.palletsprojects.com/en/1.1.x/) api/app.

## Web app
Simple app consisting of a form where you can upload an image, and see the inference result of the model in the browser. Run:

`$ python3 app.py --port 5000`

then visit http://localhost:5000/ in your browser:

<p align="center">
<img src="https://raw.githubusercontent.com/sokhunter/face_mask_detection_app/YOLOv5FlaskApi/static/imgs/webapp.png" width="450">
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/sokhunter/face_mask_detection_app/YOLOv5FlaskApi/static/imgs/detection.png" width="450">
</p>

## Run & Develop locally
Run locally and dev:
* `python3 -m venv venv`
* `source venv/bin/activate`
* `(venv) $ pip install -r requirements.txt`
* `(venv) $ python3 app.py --port 5000`

## Docker
The example dockerfile shows how to expose the rest API:
```
# Build
docker build -t yolov5-flask .
# Run
docker run -p 5000:5000 yolov5-flask:latest
```

## reference
- https://github.com/ultralytics/yolov5
- https://github.com/jzhang533/yolov5-flask (this repo was forked from here)
- https://github.com/avinassh/pytorch-flask-api-heroku
