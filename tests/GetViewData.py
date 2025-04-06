# -*- coding: UTF-8 -*-
"""
@Project ：xml.Revit.MCP 
@File    ：GetViewData.py
@IDE     ：PyCharm 
@Author  ：zedmoster
@Date    ：2025/4/6 13:11 
"""

from _tcp import send_tcp_data

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "GetViewData",
    "params": {},
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)