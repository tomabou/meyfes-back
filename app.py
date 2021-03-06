from lib import transform, maze
from lib import server
import numpy as np
import cv2
import os
import random
import sys

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

import ssl
import time


app = Flask(__name__)
CORS(app)
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain("../tomabou.com/cert1.pem",
                        "../tomabou.com/privkey1.pem")


def get_file_path(image_id):
    return "./image/" + str(image_id) + ".png"


@app.route("/", methods=['POST'])
def create_grid_graph():
    img = server.get_image_file(request)
    img = transform.transform_main(img, (45, 30))
    img = np.transpose(img)
    vertex = maze.create_vertex_list(img)
    edgeR, edgeC = maze.create_edge_list(vertex)
    return jsonify(
        {"vertex": vertex.tolist(), "edgeR": edgeR, "edgeC": edgeC}
    )


def create_image():
    start = time.time()
    img = server.get_image_file(request)
    img = transform.transform_main(img, (45, 30))
    graph = maze.create_graph(img)
    img_path = maze.create_graph_image(graph, 'test.png')
    graph_string = maze.create_graph_string(graph, 1, 2)
    maze.save_graph_string(graph_string, "./tmp/graph.txt")
    maze_list = maze.get_maze_list("./tmp/graph.txt")
    img_path, _, _, _, _ = maze.create_maze_image(maze_list)
    image_id = random.randint(1, 1e20)
    cv2.imwrite(get_file_path(image_id), img)
    end = time.time()
    print("time: {}".format(end - start))
    return jsonify(
        {'image_url': '?id={}'.format(image_id)})


@app.route("/maze", methods=['POST'])
def graph2maze():
    data = request.json
    graph = maze.create_graph_from_list(data)
    graph_string = maze.create_graph_string(graph, 3, 4)
    maze_list = maze.get_maze_list_usepipe(graph_string)
    start_goal = maze.get_maze_start_end(maze_list)
    path_length, distance = maze.clear_maze(*start_goal, maze_list)
    maze_list = maze.make_maze_with_route(
        *start_goal, maze_list, distance, path_length + 1)
    np.savetxt("tmp/maze", maze_list, fmt='%.03d')
    return jsonify({'mazelist': maze_list.tolist()})


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
