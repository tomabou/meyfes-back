import time
import numpy as np
import cv2

from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument('file')

    args = parser.parse_args()
    print(args.file)
    if args.file == "all":
        test_all()
        return

    read_and_transform(args.file)


def read_and_transform(file_path):
    try:
        img = cv2.imread(file_path)
    except BaseException:
        print("no such file")
        exit()

    show_img(img)

    start = time.time()
    img = transform_main(img, (282, 200))
    end = time.time()
    print("time: {}".format(end - start))
    show_img(img)


def test_all():
    for i in range(1570, 1592):
        file_path = "./image/DSC_" + str(i) + ".jpg"
        try:
            read_and_transform(file_path)
        except Exception as e:
            print(e)


def show_img(img):
    y = img.shape[0]
    x = img.shape[1]
    scale = 600 / max(x, y)
    img = cv2.resize(img, (int(x * scale), int(y * scale)))
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def simple_otsh(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
    return binary


def HSV_otsh(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    _, binary = cv2.threshold(img[:, :, 0], 0, 255, cv2.THRESH_OTSU)
    return binary


def first_binarize(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([0, 10, 10])
    upper_blue = np.array([60, 250, 250])
    binary = cv2.inRange(hsv_img, lower_blue, upper_blue)
    return binary


def get_image_area(img):
    y = img.shape[0]
    x = img.shape[1]
    return x * y


def get_square_contours(binary):
    contours, _ = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    squares = []
    for c in contours:
        area = get_image_area(binary)
        if area * 0.01 < cv2.contourArea(c) < get_image_area(binary) * 0.95:
            epsilon = 0.07 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, epsilon, True)
            if len(approx) == 4:
                squares.append(approx)
    squares = sortSquares(squares, binary)
    return squares


def sortSquares(squares, img):
    if not squares:
        return None
    distances = []
    my = img.shape[0] / 2
    mx = img.shape[1] / 2
    for c in squares:
        M = cv2.moments(c)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        dist = (mx - cx)**2 + (my - cy)**2
        area = cv2.contourArea(c)
        metric = dist + area
        distances.append(metric)
    return list(zip(*sorted(zip(distances, squares))))[1]


def transform(img, contour, size):
    pts1 = np.float32(contour)
    pts1 = np.transpose(pts1, (1, 0, 2))[0]
    pts2 = np.float32([[0, 0], [size[0], 0], [size[0], size[1]], [0, size[1]]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(img, M, size)
    return dst


def second_binarize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    cv2.GaussianBlur(gray, (5, 5), 0)
    _,th2 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    #_, th2 = cv2.threshold(
    #    gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th2


def erode_dilate(img):
    img = 255 - img
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    kernel = np.ones((6, 6), dtype=np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = 255 - img
    return img


def clean_edge(img):
    hight, width = img.shape
    mask = np.zeros(img.shape, dtype=np.uint8)
    ratio = 0.03
    eh = int(hight * ratio)
    ew = int(width * ratio)
    mask[eh:-eh, ew:-ew] = 255
    img = 255 - img
    img = cv2.bitwise_and(img, img, mask=mask)
    img = 255 - img
    return img


def transform_main(img, shape):
    img = cv2.resize(img, (280, 200))
    binary = first_binarize(img)
    #binary = sinple_otsh(img)
    #binary = HSV_otsh(img)
    squares = get_square_contours(binary)
    if not squares:
        img = simple_otsh(img)
        img = clean_edge(img)
        img = erode_dilate(img)
        return cv2.resize(img, shape)
    img = transform(img, squares[0], (280, 200))
    img = second_binarize(img)
    img = clean_edge(img)
    img = erode_dilate(img)
    img = cv2.resize(img, shape)
    return img


if __name__ == '__main__':
    main()
