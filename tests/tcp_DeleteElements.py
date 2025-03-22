from tcp import send_tcp_data

# 定义更新元素参数的测试数据
elements_data = [
    {"elementId": 5943, },
    {"elementId": "5913", },
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "DeleteElements",
    "params": elements_data,
    "id": 1
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
