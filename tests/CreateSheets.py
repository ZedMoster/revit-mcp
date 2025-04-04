# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

# 定义更新元素参数的测试数据
data = [
    {
        "number": "101",
        "name": "首层平面图",
        "titleBlockType": "A0 公制",
        "viewName": "标高 1"
    },
    {
        "number": "102",
        "name": "二层平面图",
        "titleBlockType": "A0 公制"
    }
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "CreateSheets",
    "params": data,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
