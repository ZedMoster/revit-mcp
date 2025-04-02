# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

# 定义更新元素参数的测试数据
data = [
    {"categoryName": "OST_Doors", "isInstance": False},
    {"categoryName": "墙", "isInstance": True},
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "FindElements",
    "params": data,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
