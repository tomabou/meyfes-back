from lib.transform import transform_main, show_img
from lib.server import get_image_file
import numpy as np
import cv2

from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=['POST'])
def post():
    img = get_image_file(request)
    return "Hello World!"


@app.route("/", methods=['GET'])
def get():
    return "Hello World!!"


def main():
    app.run(host="127.0.0.1", port=3000)


if __name__ == '__main__':
    main()
