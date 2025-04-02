# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

# 定义创建楼板的测试数据
data = [
    {
        "boundaryPoints": [
            {"x": 0.0, "y": 0.0, "z": 0.0},
            {"x": 3000.0, "y": 0.0, "z": 0.0},
            {"x": 3000.0, "y": 3000.0, "z": 0.0},
            {"x": 0.0, "y": 3000.0, "z": 0.0},
            {"x": 0.0, "y": 0.0, "z": 0.0}  # 闭合边界
        ],
        "floorTypeName": "常规 - 150mm",  # 楼板类型名称
        "structural": True  # 表示该楼板为结构楼板
    },
    {
        "boundaryPoints": [
            {"x": 0.0, "y": 0.0, "z": 0.0},
            {"x": -5000.0, "y": 0.0, "z": 0.0},
            {"x": -5000.0, "y": -5000.0, "z": 0.0},
            {"x": 0.0, "y": 0.0, "z": 0.0}  # 闭合边界
        ],
        "floorTypeName": "常规 - 150mm",  # 另一个楼板类型
        "structural": False  # 非结构楼板
    }
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "CreateFloors",
    "params": data,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
