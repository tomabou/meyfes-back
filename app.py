from lib import transform
from lib import server
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
    img = server.get_image_file(request)
    img = transform.transform_main(img)
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


@app.route("/.well-known/acme-challenge/hdkSYOSCG9sYOfINYJSyFqindc6k6ixi76g1ANcYY7M")
def acme():
    return send_file("./acme")


def main():
    app.run(host="0.0.0.0", port=80)


if __name__ == '__main__':
    main()
