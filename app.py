from lib.transform import transform_main, show_img
import numpy as np
import cv2

from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=['POST'])
def hello():
    print("hello")
    print(request.files)
    if request.files['image']:
        print("world")
        stream = request.files['image'].stream
        img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, 1)
        show_img(img)
    return "Hello World!"


def main():
    app.run(host="127.0.0.1", port=3000)


if __name__ == '__main__':
    main()
