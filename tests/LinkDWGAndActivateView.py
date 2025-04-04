# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

# 定义更新元素参数的测试数据
data = [
    {
        "filePath": r"C:\Users\zed\AppData\Local\Autodesk\zedmoster\xmlRevitCopy\db991824-5d43-4a9a-9f2e-824e37abb87f.dwg",
    },
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "LinkDWGAndActivateView",
    "params": data,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
