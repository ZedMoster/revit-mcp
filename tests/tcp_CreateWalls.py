# -*- coding: utf-8 -*-

from tcp import send_tcp_data

# 定义墙数据
data_walls = [
    {"startX": 0, "startY": 0, "endX": 12000, "endY": 0, "height": 3000, "width": 200},
    {"startX": 12000, "startY": 0, "endX": 12000, "endY": 10000, "height": 3000, "width": 200},
    {"startX": 12000, "startY": 10000, "endX": 0, "endY": 10000, "height": 3000, "width": 200},
    {"startX": 0, "startY": 10000, "endX": 0, "endY": 0, "height": 3000, "width": 200},
    {"startX": 6000, "startY": 0, "endX": 6000, "endY": 5000, "height": 3000, "width": 200},
    {"startX": 6000, "startY": 5000, "endX": 12000, "endY": 5000, "height": 3000, "width": 200},
    {"startX": 12000, "startY": 5000, "endX": 12000, "endY": 8000, "height": 3000, "width": 200},
    {"startX": 0, "startY": 5000, "endX": 6000, "endY": 5000, "height": 3000, "width": 200},
    {"startX": 6000, "startY": 5000, "endX": 6000, "endY": 8000, "height": 3000, "width": 200},
    {"startX": 6000, "startY": 8000, "endX": 12000, "endY": 8000, "height": 3000, "width": 200},

    {"startX": 0, "startY": 0, "endX": 12000, "endY": 0, "height": 3000, "width": 200, "elevation": 4000.0},
    {"startX": 12000, "startY": 0, "endX": 12000, "endY": 10000, "height": 3000, "width": 200, "elevation": 4000.0},
    {"startX": 12000, "startY": 10000, "endX": 0, "endY": 10000, "height": 3000, "width": 200, "elevation": 4000.0},
    {"startX": 0, "startY": 10000, "endX": 0, "endY": 0, "height": 3000, "width": 200, "elevation": 4000.0},
]

# 构造JSON-RPC请求
json_rpc_request = {
    "Id": "2.0",
    "Method": "CreateWalls",
    "Params": data_walls
}

# 发送墙数据
send_tcp_data(json_rpc_request)
