from lib.transform import transform_main, show_img
from lib.server import get_image_file, create_raw_file
import numpy as np
import cv2

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", methods=['POST'])
def post():
    img = get_image_file(request)
    img = transform_main(img)
    data = create_raw_file(img)
    return jsonify({'image_url': 'http://localhost:5000'})


@app.route("/", methods=['GET'])
def get():
    return send_file("./image/test.jpg", mimetype='image/jpeg')


def main():
    app.run(host="127.0.0.1", port=3000)


if __name__ == '__main__':
    main()
