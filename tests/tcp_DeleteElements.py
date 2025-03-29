# -*- coding: utf-8 -*-

from tcp import send_tcp_data

# 定义更新元素参数的测试数据
data = [
    {"elementId": 5943, },
    {"elementId": "5913", },
    {"elementId": 212831}
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "DeleteElements",
    "params": data,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
