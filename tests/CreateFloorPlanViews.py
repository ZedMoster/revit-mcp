#
# -*- coding: utf-8 -*-

from _tcp import send_tcp_data

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "CreateFloorPlanViews",
    "params":
        [
            {"levelId": "355", "viewName": "Level 1 - Floor Plan"},
            {"levelId": "2607", "viewName": "Level 2 - Floor Plan"}
        ]
    ,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)