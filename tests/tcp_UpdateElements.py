from tcp import send_tcp_data

# 定义更新元素参数的测试数据
elements_update_data = [
    {"elementId": 212781, "parameterName": "注释", "parameterValue": "100"},
    {"elementId": 212792, "parameterName": "注释", "parameterValue": "200"}
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "UpdateElements",
    "params": elements_update_data,
    "id": 1
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
