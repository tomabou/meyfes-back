import numpy as np
import cv2

from flask import request


def get_image_file(request):
    if request.files['image']:
        stream = request.files['image'].stream
        img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, 1)
        return img
    return None
