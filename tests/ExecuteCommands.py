# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "ExecuteCommands",
    "params":
        [
            {"name": "F1关闭启用", "add": True},
            {"name": "F1关闭启用", "add": False}
        ]
    ,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
