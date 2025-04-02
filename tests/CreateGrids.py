# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

data = [
    # 直线轴网
    {
        "name": "Grid_Line_1",
        "startX": 0,
        "startY": 0,
        "endX": 10000,
        "endY": 0,
    },
    {
        "name": "Grid_Line_2",
        "startX": 0,
        "startY": 5000,
        "endX": 10000,
        "endY": 5000,
    },
    {
        "categoryName": "轴网",
        "name": "Grid_Line_3",
        "startX": 0,
        "startY": 10000,
        "endX": 10000,
        "endY": 10000,
    },

    # 弧线轴网
    {
        "name": "Grid_Arc_1",
        "startX": 5000,
        "startY": 5000,
        "endX": 15000,
        "endY": 0,
        "centerX": 7000,
        "centerY": 2000,
    },
    {
        "name": "Grid_Arc_2",
        "startX": 10000,
        "startY": 5000,
        "endX": 20000,
        "endY": 5000,
        "centerX": 15000,
        "centerY": 7000,
    }
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "CreateGrids",
    "params": data,
}

# 发送数据
send_tcp_data(json_rpc_request)
