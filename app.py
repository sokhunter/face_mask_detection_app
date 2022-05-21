"""
Simple app to upload an image via a web form
and view the inference results on the image in the browser.
"""
import argparse
import base64
import random
import string

from flask import Flask, redirect, render_template, request
from PIL import Image

from inference import get_prediction

app = Flask(__name__)

DETECTION_URL = "/detect"


@app.route("/", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if not file:
            return

        img_bytes = file.read()
        letters = string.ascii_lowercase

        results = get_prediction(img_bytes)
        results.render()  # updates results.imgs with boxes and labels
        for img in results.imgs:
            img_base64 = Image.fromarray(img)
            img_name = 'static/prediction_' + \
                ''.join(random.choice(letters) for i in range(10)) + '.jpg'
            img_base64.save(img_name, format="JPEG")
        #img = Image.open(io.BytesIO(img_bytes))
        #results = model(img, size=640)

        # for debugging
        # data = results.pandas().xyxy[0].to_json(orient="records")
        # return data

        return redirect(img_name)

    return render_template("index.html")


# @app.route(DETECTION_URL, methods=["POST"])
# def predictREST():
#     if not request.method == "POST":
#         return

#     if request.files.get("image"):
#         image_file = request.files["image"]
#         image_bytes = image_file.read()

#         results = get_prediction(image_bytes)
#         data = results.pandas().xyxy[0].to_json(orient="records")
#         return data

@app.route(DETECTION_URL, methods=["POST"])
def predictREST():
    if not request.method == "POST":
        return

    if request.json.get("base64String"):
        base64_string = request.json["base64String"]
        base64_data = base64_string.split(',')
        img_data = base64.b64decode(base64_data[1])
        results = get_prediction(img_data)
        data = results.pandas().xyxy[0].to_json(orient="records")
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flask app exposing yolov5 models")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    args = parser.parse_args()
    print("modelo cargado")
    # debug=True causes Restarting with stat
    app.run(host="0.0.0.0", port=args.port)
