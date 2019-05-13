from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
import urllib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import networkx as nx
import os
from werkzeug.utils import secure_filename
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


def clear_maze(sx, sy, gx, gy, maze):
    INF = 100000000

    field_x_length = len(maze)
    field_y_length = len(maze[0])
    distance = [[INF for i in range(field_y_length)]
                for j in range(field_x_length)]

    def bfs():
        queue = []

        queue.insert(0, (sx, sy))

        distance[sx][sy] = 0

        while len(queue):
            x, y = queue.pop()
            if x == gx and y == gy:
                break

            for i in range(0, 4):
                nx, ny = x + [1, 0, -1, 0][i], y + [0, 1, 0, -1][i]
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
    color_1 = (0, 0, 0)
    color_2 = (255, 255, 255)
    color_3 = (255, 0, 0)
    color_4 = (0, 255, 0)
    diss = []

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
                nx, ny = x + [1, 0, -1, 0][i], y + [0, 1, 0, -1][i]
                if(0 <= nx and nx < field_x_length and 0 <= ny and ny < field_y_length and maze[nx][ny] != 1 and distance[nx][ny] == distance[x][y] - 1):
                    rootlist.append([nx, ny])
                    x, y = nx, ny
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

    for i in range(I - 1):
        for j in range(J):
            if im_bin_50[i][j] == 0 and im_bin_50[i + 1][j] == 0:
                G.add_edge((i, j), (i + 1, j))
    return G


def create_graph_from_list(data):
    I = len(data)
    J = len(data[0])
    G = nx.Graph()
    for i in range(I):
        for j in range(J):
            if data[i][j] == 0:
                G.add_node((i, j))

    for i in range(I):
        for j in range(J - 1):
            if data[i][j] == 0 and data[i][j + 1] == 0:
                G.add_edge((i, j), (i, j + 1))

    for i in range(I - 1):
        for j in range(J):
            if data[i][j] == 0 and data[i + 1][j] == 0:
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


def save_graph_string(graph_string, file_name):
    with open(file_name, "w") as f:
        f.write(graph_string)


def create_graph_image(G, filename):
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

    img_path = os.path.join('image', filename)
    if os.path.exists(img_path):
        os.remove(img_path)
    plt.savefig(img_path)
    return img_path


def get_maze_list(input_file_name):
    command = './bin/maze_creator < ' + input_file_name + ' > ./tmp/mazelist'
    proc = subprocess.run(
        [command],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    ans = np.loadtxt("./tmp/mazelist", dtype=int)
    ans = np.transpose(ans)
    ans = ans[:, ::-1]
    return ans


def create_maze_image(maze_list):
    rows = len(maze_list)
    cols = len(maze_list[0])
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
            if maze_list[i][j] == 0:
                colorthis = color_2
            if maze_list[i][j] == 1:
                colorthis = color_1
            if maze_list[i][j] == 2:
                colorthis = color_3
                sx, sy = i, j
                # スタート
            if maze_list[i][j] == 3:
                colorthis = color_4
                gx, gy = i, j
                # ゴール
            draw.rectangle((x, y, x1, y1), fill=colorthis, outline=color_1)
    img_url2 = os.path.join('image', 'pillow_imagedraw.jpg')
    im.save(img_url2)
    return img_url2, sx, sy, gx, gy


def create_maze_route_image(maze_list, sx, sy, gx, gy):
    bf, distance = clear_maze(sx, sy, gx, gy, maze_list)
    rootlist = makeroot(sx, sy, gx, gy, maze_list, distance)
    diss = []
    diss[-1].save(os.path.join('static', 'img_maze', 'pil2.jpg'))
    img_url3 = os.path.join('static', 'img_maze', 'pil2.jpg')
    print(img_url3)
    a = os.listdir(os.path.join('static', 'img_maze'))[::-1]
    mazes_in_list = sorted(a, reverse=True)
    print(mazes_in_list)
    # 4/26 17:30
    return mazes_in_list
