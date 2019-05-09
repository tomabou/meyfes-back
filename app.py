from lib import transform
from lib import server
import numpy as np
import cv2
import os
import random

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

import ssl

app = Flask(__name__)
CORS(app)
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain("../tomabou.com/cert1.pem",
                        "../tomabou.com/privkey1.pem")


def get_file_path(image_id):
    return "./image/" + str(image_id) + ".png"


@app.route("/", methods=['POST'])
def post():
    img = server.get_image_file(request)
    img = transform.transform_main(img)
    image_id = random.randint(1, 1e20)
    cv2.imwrite(get_file_path(image_id), img)

    return jsonify(
        {'image_url': 'https://tomabou.com:5000?id={}'.format(image_id)})


@app.route("/", methods=['GET'])
def get():
    image_id = request.args.get("id", default=0, type=int)
    file_path = get_file_path(image_id)
    if not os.path.exists(file_path):
        file_path = "./image/test.jpg"

    return send_file(file_path)


@app.route(
    "/.well-known/acme-challenge/aSXLbUsQyS-wBgqH8PSn3jrq0gSaoQpJ5f6eJ2MFU7I")
def acme():
    return send_file("./acme")


def main():
    app.run(host="0.0.0.0", port=443, ssl_context=context)


if __name__ == '__main__':
    main()
