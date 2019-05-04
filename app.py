from lib.transform import transform_main, show_img
from lib.server import get_image_file, create_raw_file
import numpy as np
import cv2
import os
import random

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def get_file_path(image_id):
    return "./image/"+str(image_id)+".png"


@app.route("/", methods=['POST'])
def post():
    img = get_image_file(request)
    img = transform_main(img)
    image_id = random.randint(1, 1e20)
    cv2.imwrite(get_file_path(image_id), img)

    return jsonify({'image_url': 'https://tomabou.com:5000?id={}'.format(image_id)})


@app.route("/", methods=['GET'])
def get():
    image_id = request.args.get("id", default=0, type=int)
    file_path = get_file_path(image_id)
    if not os.path.exists(file_path):
        file_path = "./image/test.jpg"

    return send_file(file_path)


def acme():
    return send_file("./acme")


def main():
    app.run(host="127.0.0.1", port=3000)


if __name__ == '__main__':
    main()
