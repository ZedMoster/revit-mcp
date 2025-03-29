# -*- coding: utf-8 -*-

from tcp import send_tcp_data

data = [
    {
        "categoryName": "场地",  # 族实例的类别
        "name": "12000 x 2400mm",  # 族类型名称
        "familyName": "建筑拖车",  # 族名称（可选）
        "startX": 1000,  # 起始位置X（单位：mm）
        "startY": 2000,  # 起始位置Y（单位：mm）
        "startZ": 0,  # 起始位置Z（单位：mm）
        "viewName": "标高 1",  # 视图名称（可选）
        "rotationAngle": 0  # 旋转角度（单位：度，可选）
    },
    {
        "categoryName": "场地",  # 族实例的类别
        "name": "12000 x 2400mm",  # 族类型名称
        "familyName": "建筑拖车",  # 族名称（可选）
        "startX": 5000,  # 起始位置X（单位：mm）
        "startY": 2000,  # 起始位置Y（单位：mm）
        "startZ": 3300,  # 起始位置Z（单位：mm）
        "rotationAngle": 45  # 旋转角度（单位：度，可选）
    },
    {
        "categoryName": "窗",
        "name": "0406 x 0610mm",
        "startX": -10500,
        "startY": 5000,
        "startZ": 0, 
        "hostid": 225535,
        "level": "标高 1",
    },
    {
        "categoryName": "柱",
        "name": "610 x 610mm",
        "startX": -10500,
        "startY": 5000,
        "startZ": 4000,
        "level": "标高 1",
        "rotationAngle": 45
    },
    {
        "categoryName": "柱",
        "name": "610 x 610mm",
        "startX": -10500,
        "startY": 5000,
        "startZ": 0,
        "level": "标高 2",
        "rotationAngle": 0
    },
    {
        "categoryName": "结构框架",
        "name": "HW400x400x13x21",
        "startX": -10500,
        "startY": -5000,
        "startZ": 4000,
        "endX": -4500,
        "endY": 4500,
        "endZ": 5500,
        "rotationAngle": 0
    }
]

# 构造 JSON-RPC 请求
json_rpc_request = {
    "jsonrpc": "2.0",
    "method": "CreateFamilyInstances",
    "params": data,
}

# 发送更新元素数据
send_tcp_data(json_rpc_request)
