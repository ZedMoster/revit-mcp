# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

data = [
    {"name": "ClearDuplicates"},
    {"name": "DeleteZeroRooms"},
    {"name": "DimensionViewPlanGrids"},
    {"name": "新增标高", "params": {"offset": 3000}}
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "CallFunc",
    "params": data,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
