import numpy as np
import cv2
import io

from flask import request


def get_image_file(request):
    if request.files['image']:
        stream = request.files['image'].stream
        img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, 1)
        return img
    return None


def create_raw_file(img):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, encimg = cv2.imencode('.png', img, encode_param)
    raw = encimg.tobytes()
    return io.BytesIO(raw)
