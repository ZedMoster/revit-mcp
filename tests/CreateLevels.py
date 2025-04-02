# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

data = [
    {
        "name": "Level_3",  # 标高名称
        "elevation": 8000,  # 标高的高度（单位：mm）
    },
    {
        "name": "Level_4",  # 标高名称
        "elevation": 12000,  # 标高的高度（单位：mm）
    },
    {
        "name": "Level_5",  # 标高名称
        "elevation": 16000,  # 标高的高度（单位：mm）
    },
    {
        "name": "Level_6",  # 标高名称
        "elevation": 20000,  # 标高的高度（单位：mm）
    },
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "CreateLevels",
    "params": data,
}

# 发送数据
send_tcp_data(json_rpc_request)
