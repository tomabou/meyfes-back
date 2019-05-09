from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
import urllib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import networkx as nx
import os
from werkzeug import secure_filename
import matplotlib.pyplot as plt
import datetime
import subprocess

app = Flask(__name__)

if not os.path.exists("uploads/"):
    os.makedirs("uploads/")

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


global distance
color_1 = (0, 0, 0)
color_2 = (255, 255, 255)
color_3 = (255, 0, 0)
color_4 = (0, 255, 0)

global diss
diss = []


def clear_maze(sx, sy, gx, gy, maze):

    # debug_print(maze)
    INF = 100000000

    field_x_length = len(maze)
    field_y_length = len(maze[0])
    distance = [[INF for i in range(field_y_length)]
                for j in range(field_x_length)]
    #    distance = [[None]*field_x_length]*field_y_length
    # diss=[]

    def bfs():
        queue = []

        queue.insert(0, (sx, sy))

        distance[sx][sy] = 0

        while len(queue):
            x, y = queue.pop()
            # print(x,y)

            if x == gx and y == gy:
                break

            for i in range(0, 4):
                nx, ny = x + [1, 0, -1, 0][i], y + [0, 1, 0, -1][i]
                # print(nx,ny)
                # print(len(distance[0]))
                if (0 <= nx and nx < field_x_length and 0 <= ny and ny <
                        field_y_length and maze[nx][ny] != 1 and distance[nx][ny] == INF):
                    queue.insert(0, (nx, ny))
                    distance[nx][ny] = distance[x][y] + 1

        return distance[gx][gy]

    return bfs(), distance


def makeroot(sx, sy, gx, gy, maze, distance):
    # ルートを画像として保存していく
    tile_size = 10
    field_x_length = len(maze)
    field_y_length = len(maze[0])
    x, y = gx, gy
    rootlist = [[x, y]]
    # ルートが入っている
    count = 0
    while x != sx or y != sy:
        for i in range(0, 4):
            if count % 50 == 0:
                im = Image.open(
                    os.path.join(
                        'static',
                        'img_maze',
                        'pillow_imagedraw.jpg'))
                draw = ImageDraw.Draw(im)
                for root in rootlist:
                    r0 = root[0] * tile_size
                    r1 = root[1] * tile_size
                    draw.rectangle(
                        (r1, r0, r1 + tile_size, r0 + tile_size), fill=color_3, outline=color_1)
                diss.append(im)
                # dissは動画用
                nx, ny = x + [1, 0, -1, 0][i], y + [0, 1, 0, -1][i]
                # print(distance[nx][ny])
                if(0 <= nx and nx < field_x_length and 0 <= ny and ny < field_y_length and maze[nx][ny] != 1 and distance[nx][ny] == distance[x][y] - 1):
                    rootlist.append([nx, ny])
                    x, y = nx, ny
                    # print(rootlist)
            else:
                for root in rootlist:
                    r0 = root[0] * tile_size
                    r1 = root[1] * tile_size
                    #draw.rectangle((r1,r0, r1+tile_size, r0+tile_size), fill=color_3,outline=color_1)
                diss.append(im)
                nx, ny = x + [1, 0, -1, 0][i], y + [0, 1, 0, -1][i]
                # print(distance[nx][ny])
                if(0 <= nx and nx < field_x_length and 0 <= ny and ny < field_y_length and maze[nx][ny] != 1 and distance[nx][ny] == distance[x][y] - 1):
                    rootlist.append([nx, ny])
                    x, y = nx, ny
                    # print(rootlist)
        count = count + 1
    return rootlist


def create_graph(im_bin_50):
    I, J = im_bin_50.shape
    G = nx.Graph()
    for i in range(I):
        for j in range(J):
            if im_bin_50[i][j] == 0:
                G.add_node((i, j))

    for i in range(I):
        for j in range(J - 1):
            if im_bin_50[i][j] == 0 and im_bin_50[i][j + 1] == 0:
                G.add_edge((i, j), (i, j + 1))

    for i in range(size - 1):
        for j in range(size):
            if im_bin_50[i][j] == 0 and im_bin_50[i + 1][j] == 0:
                G.add_edge((i, j), (i + 1, j))
    return G


def create_graph_string(G):
    str1 = list(G.nodes)
    str2 = list(G.edges)
    graph_str = str(len(G.nodes)) + "\n"
    for i in range(len(str1)):
        graph_str += str(list(G.nodes)[i][0]) + \
            " " + str(list(G.nodes)[i][1]) + "\n"

    graph_str += str(len(G.edges)) + "\n"

    for i in range(len(str2)):
        graph_str += str(list(G.edges)[i][0][0]) + " " + str(list(G.edges)[i][0][1]) + " " + str(
            list(G.edges)[i][1][0]) + " " + str(list(G.edges)[i][1][1]) + "\n"

    return graph_str


def save_graph_string(graph_string):
    with open("graph2.txt", "w") as f:
        f.write(graph_string)


def create_graph_image(G):
    pos = {n: (n[0], n[1]) for n in G.nodes()}
    nx.draw_networkx_nodes(G, pos, node_size=10, alpha=1, node_color='red')
    nx.draw_networkx_edges(
        G,
        pos,
        font_size=10,
        label=1,
        edge_color="black",
        width=2)
    pos = {n: (n[0], n[1]) for n in G.nodes()}

    img_path = os.path.join('static', 'img_graph', filename)
    if os.path.exists(img_path):
        os.remove(img_path)
    plt.savefig(img_path)
    return image_path


def makenewmaze(input_file_name):
    command = './bin/maze_creator < ' + input_file_name + ' > bin/mazelist'
    proc = subprocess.run(
        [command],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    from mazelist3 import mazelist
    images = []
    data = mazelist
    rows = len(data)
    cols = len(data[0])
    width = 200
    center = width // 2
    color_1 = (0, 0, 0)
    color_2 = (255, 255, 255)
    color_3 = (255, 0, 0)
    color_4 = (0, 255, 0)
    max_radius = int(center * 1.5)
    step = 8
    tile_size = 10
    im = Image.new('RGB', (cols * tile_size, rows * tile_size), color_2)
    draw = ImageDraw.Draw(im)
    x = 0
    y = 0
    k = 0
    for i in range(0, rows):
        y = i * tile_size
        y1 = y + tile_size
        for j in range(0, cols):
            x = j * tile_size
            x1 = x + tile_size
            if data[i][j] == 0:
                colorthis = color_2
            if data[i][j] == 1:
                colorthis = color_1
            if data[i][j] == 2:
                colorthis = color_3
                sx, sy = i, j
                # スタート
            if data[i][j] == 3:
                colorthis = color_4
                gx, gy = i, j
                # ゴール
            draw.rectangle((x, y, x1, y1), fill=colorthis, outline=color_1)
    #im.save('pillow_imagedraw.jpg', quality=95)
    im.save(os.path.join('static', 'img_maze', 'pillow_imagedraw.jpg'))
    # makemaze(mazelist)
    # img_url2='pillow_imagedraw.jpg'
    img_url2 = os.path.join('static', 'img_maze', 'pillow_imagedraw.jpg')
    # ここまで迷路を作成するプロセスで、ここからは、その迷路の答えを書くやつ。
    data = mazelist
    bf, distance = clear_maze(sx, sy, gx, gy, data)
    rootlist = makeroot(sx, sy, gx, gy, data, distance)
    print(len(diss))
    diss[-1].save(os.path.join('static', 'img_maze', 'pil2.jpg'))
    img_url3 = os.path.join('static', 'img_maze', 'pil2.jpg')
    print(img_url3)
    a = os.listdir(os.path.join('static', 'img_maze'))[::-1]
    mazes_in_list = sorted(a, reverse=True)
    print(mazes_in_list)
    # 4/26 17:30
    return mazes_in_list


@app.route('/')
def index():
    name = "yoko"
    pic1 = "/images/fig2.png"
    return render_template('form0.html', title="Maze", name=name, pic=pic1)


@app.route('/form', methods=['POST', 'GET'])
def index2():
    if request.method == 'POST':
        name = "yoko"
        pic1 = "/images/fig2.png"
        value = request.form["action"]
        if value == "1":
            # to confirm
            return render_template(
                'form.html', title="Maze", name=name, pic=pic1)
        elif value == "2":
            # to confirm2
            return render_template(
                'form2.html', title="Maze", name=name, pic=pic1)


@app.route('/confirm', methods=['POST', 'GET'])
def show_img():
    if request.method == 'POST':
        if 'img_data' not in request.files:
            flash('No file part')
            return redirect(request.url)
        img_data = request.files['img_data']
        value = request.form["size"]
        img_url22, filename, sss = imgmake(img_data, value)
        #fname, ext = os.path.splitext(filename)
        return render_template(
            "confirm.html",
            title="Maze",
            img_url=img_url22,
            filename=filename,
            sss=sss)


@app.route('/confirm2', methods=['POST', 'GET'])
def show_img2():
    if request.method == 'POST':
        # consider smoji
        sizemoji = request.form["sizemoji"]
        value = request.form["size"]
        words = request.form["sent"]
        img_url22, filename, sss = imgmake_moji(sizemoji, value, words)
        return render_template(
            "confirm.html",
            title="Maze",
            img_url=img_url22,
            filename=filename,
            sss=sss)


@app.route('/show', methods=['POST', 'GET'])
def show():
    images = makenewmaze()
    return render_template("showmaze.html", title="Maze", images=images)
