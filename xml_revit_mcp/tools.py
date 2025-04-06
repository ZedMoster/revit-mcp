# -*- coding: utf-8 -*-
# tools.py
# Copyright (c) 2025 zedmoster
# Revit integration through the Model Context Protocol.

from typing import List
from mcp.server.fastmcp import Context


def get_commands(ctx: Context, method: str = "GetCommands") -> dict:
    """
    获取所有功能商店里的功能，每个功能包含名称、描述和提示信息，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 获取Revit插件中所有可用功能的完整列表
    - 返回每个功能的名称、描述和提示信息
    - 无需额外参数，直接获取所有功能
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"GetCommands"

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "name": "功能名称",
                        "description": "功能描述",
                        "tooltip": "功能提示"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        # 获取所有功能
        response = get_commands(ctx)

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": [
                {
                    "name": "创建墙",
                    "description": "创建基本墙元素",
                    "tooltip": "点击创建标准墙"
                },
                {
                    "name": "创建门",
                    "description": "在墙上创建门",
                    "tooltip": "选择墙后点击创建门"
                },
                ...
            ],
            "id": 1
        }
    """
    try:
        # 此函数不需要参数，直接发送请求
        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, {})
        return result

    except Exception as e:
        ctx.log("error", f"获取功能列表时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"获取功能列表时发生错误: {str(e)}",
                "data": None
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def execute_commands(ctx: Context, method: str = "ExecuteCommands", params: List[dict[str, any]] = None) -> dict:
    """
    执行指定的功能命令，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量执行多个功能命令
    - 可以指定是添加还是移除功能面板
    - 自动查找并执行匹配名称的功能
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"ExecuteCommands"
        params (List[Dict]): 命令参数列表，每个字典包含:
            - name (str): 要执行的功能名称
            - add (bool): True表示添加功能面板，False表示移除功能面板

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "name": "AI助手",
                        "description": "使用DeepSeek直接操作Revit,会员用户抢先体验",
                        "tooltip": "关注公众号获取最新功能消息(F1获取帮助)"
                    },
                    {
                        "name": "AI代码转换",
                        "description": "AI生成的代码功能尝试转换为Revit可用功能,会员用户抢先体验~",
                        "tooltip": "关注公众号获取最新功能消息(F1获取帮助)"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        # 添加功能面板
        response = execute_command(ctx, params=[
            {"name": "AI助手", "add": True},
            {"name": "AI代码转换", "add": True}
        ])

        # 移除功能面板
        response = execute_command(ctx, params=[
            {"name": "AI助手", "add": False}
        ])
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "name" not in param:
                raise ValueError("每个参数字典必须包含'name'")

            if "add" not in param:
                raise ValueError("每个参数字典必须包含'add'")

            if not isinstance(param["name"], str):
                raise ValueError("'name'必须是字符串")

            if not isinstance(param["add"], bool):
                raise ValueError("'add'必须是布尔值")

            validated_param = {
                "name": param["name"],
                "add": param["add"]
            }
            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"执行功能命令时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"执行功能命令时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def call_func(ctx: Context, method: str = "CallFunc", params: List[dict[str, any]] = []) -> dict:
    """
    调用 Revit 函数服务，支持直接传递功能名称及其参数，遵循 JSON-RPC 2.0 规范。

    特性:
    - 支持批量调用多个功能
    - 支持传递参数给每个功能
    - 自动验证参数有效性
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CallFunc"
        params (List[Dict]): 功能参数列表，必须提供至少一个函数名，每个字典包含:
            - name (str): 要调用的功能名称
            - params (dict, optional): 功能对应的参数,可为空

    返回:
        dict: JSON-RPC 2.0格式的响应

    示例:
        # 调用不需要参数的函数
        response = call_func(ctx, params=[
            {"name": "ClearDuplicates"},
            {"name": "DimensionViewPlanGrids"},
            {"name": "DeleteZeroRooms"}
        ])

        # 调用带参数的函数
        response = call_func(ctx, params=[
            {"name": "新增标高", "params": {"offset": 3000}}
        ])

        # 混合调用
        response = call_func(ctx, params=[
            {"name": "ClearDuplicates"},
            {"name": "新增标高", "params": {"offset": 3000}}
        ])
    """
    try:
        # 参数验证 - 确保提供了至少一个函数调用
        if not params or len(params) == 0:
            raise ValueError("必须提供至少一个函数调用，params不能为空列表")

        validated_params = []
        for param in params:
            if not isinstance(param, dict):
                raise ValueError("每个参数必须是字典")

            if not param.get("name") or not isinstance(param["name"], str):
                raise ValueError("'name'字段必须是字符串且不能为空")

            validated_params.append({
                "name": param["name"],
                "params": param.get("params", {})  # 如果未提供参数，则默认为空字典
            })

        from .server import get_revit_connection
        revit = get_revit_connection()

        response = revit.send_command(method, validated_params)
        return response

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": f"无效参数: {str(ve)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"执行函数时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"执行函数时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def get_view_data(ctx: Context, method: str = "GetViewData", params: List[dict[str, any]] = None) -> dict:
    """
    读取当前视图中所有信息，包括文本和图形实体数据，遵循JSON-RPC 2.0规范。

    特性:
    - 提取所有文本内容及其位置信息
    - 提取所有图形对象（线、弧、圆等）的几何信息
    - 按图层组织返回的数据
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"GetViewData"
        params (List[dict], optional): 可选参数，默认为None

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "name": "图层名称",
                        "type": "Text",
                        "text": "文本内容",
                        "point": {"X": x值, "Y": y值, "Z": z值}
                    },
                    {
                        "name": "图层名称",
                        "type": "Line",
                        "startPoint": {"X": x1, "Y": y1, "Z": z1},
                        "endPoint": {"X": x2, "Y": y2, "Z": z2}
                    },
                    {
                        "name": "图层名称",
                        "type": "Arc",
                        "startAngle": 起始角度,
                        "endAngle": 结束角度,
                        "centerPoint": {"X": x, "Y": y, "Z": z},
                        "radius": 半径值
                    },
                    {
                        "name": "图层名称",
                        "type": "Circle",
                        "centerPoint": {"X": x, "Y": y, "Z": z},
                        "radius": 半径值
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    错误代码:
        -32600: 无效请求
        -32603: 内部错误（导出或解析时）
        -32700: 解析错误

    示例:
        # 获取当前视图所有图形数据
        response = get_view_data(ctx)

        # 处理文本数据
        texts = [item for item in response.get("result", []) if item.get("type") == "Text"]

        # 处理线段数据
        lines = [item for item in response.get("result", []) if item.get("type") == "Line"]

        # 处理圆弧数据
        arcs = [item for item in response.get("result", []) if item.get("type") == "Arc"]
    """
    try:
        # 构造请求参数，本方法不需要特定参数
        request_params = params or []

        from .server import get_revit_connection
        revit = get_revit_connection()

        # 发送请求并获取响应
        response = revit.send_command(method, request_params)
        return response

    except Exception as e:
        ctx.log("error", f"获取视图数据时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"获取视图数据时发生错误: {str(e)}",
                "data": None
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def get_selected_elements(ctx: Context, method: str = "GetSelectedElements") -> dict:
    """
    获取当前Revit UI中选择的元素，遵循JSON-RPC 2.0规范。

    特性:
    - 获取当前用户在Revit界面中选择的所有元素
    - 返回元素的完整信息，包括ID、类别和名称
    - 无需额外参数，直接反映当前UI状态
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"GetSelectedElements"

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "元素ID",
                        "name": "元素名称",
                        "familyName": "类别名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        # 获取当前选择的元素
        response = get_selected_elements(ctx)

        # 输出示例
        {
            "jsonrpc":"2.0","id":"a39934f6-0ee9-4319-b820-1eba95a82c51",
            "result":
            [
                {"elementId":"355","familyName":"标高","name":"标高 1"},
                {"elementId":"2607","familyName":"标高","name":"标高 2"},
                {"elementId":"5855","familyName":"标高","name":"T.O. Fnd. 墙"}
            ],
            "error":[]
        }
    """
    try:
        # 此函数不需要参数，直接发送请求
        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, {})
        return result

    except Exception as e:
        ctx.log("error", f"获取选中元素时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"获取选中元素时发生错误: {str(e)}",
                "data": None
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def find_elements(ctx: Context, method: str = "FindElements", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中按类别查找元素，返回匹配的元素信息列表，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持按类别BuiltInCategory或者Category.Name查找
    - 和视图相关的请使用OST_Views类别作为categoryName参数,获取然后通过参数来过滤出如楼层平面,三维视图,剖面,图纸等
    - 可指定查找实例或类型元素
    - 支持批量多个查询条件
    - 严格遵循JSON-RPC 2.0规范
    - 详细的错误处理和日志记录

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"FindElements"
        params (List[Dict[str, Union[str, bool]]]): 查询条件列表，每个字典包含:
            - categoryName (str): BuiltInCategory或者Category.Name
                （如"OST_Views","OST_Walls","OST_Doors", "视图", "墙", "门"等）
            - isInstance (bool): True查找实例,False查找类型

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "元素ID",
                        "name": "元素名称",
                        "familyName": "族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": 错误代码,
                    "message": 错误描述,
                    "data": 错误详情
                },
                "id": request_id
            }

    错误代码:
        -32600: 无效请求（参数验证失败）
        -32602: 类别未找到（无效的BuiltInCategory或Category.Name）
        -32603: 内部错误
        -32700: 解析错误（参数格式错误）

    示例:
        > response = find_elements(ctx, params=[
            {"categoryName": "OST_Views", "isInstance": True},
            {"categoryName": "OST_Doors", "isInstance": False},
            {"categoryName": "门", "isInstance": True}
        ])
        > print(response)
        {
            "jsonrpc": "2.0",
            "result": [
                {"elementId": "123456", "name": "单扇门", "familyName": "M_单扇门"},
                {"elementId": "789012", "name": "双扇门", "familyName": "M_双扇门"}
            ],
            "id": 1
        }
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        if not isinstance(params, list) or not all(isinstance(param, dict) for param in params):
            raise ValueError("参数必须为字典列表")

        validated_params = []
        for param in params:
            # 验证categoryName
            if "categoryName" not in param or not isinstance(param["categoryName"], str):
                raise ValueError("categoryName为必填项且必须是字符串,必须是BuiltInCategory枚举值或Category.Name")

            # 验证isInstance
            if "isInstance" not in param or not isinstance(param["isInstance"], bool):
                raise ValueError("isInstance为必填项且必须是布尔值")

            validated_params.append({
                "categoryName": param["categoryName"],
                "isInstance": param["isInstance"]
            })

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": str(ve)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"查找元素时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"查找元素时发生错误: {str(e)}"},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def update_elements(ctx: Context, method: str = "UpdateElements", params: list[dict[str, any]] = None) -> dict:
    """
    批量更新Revit元素参数值，遵循JSON-RPC 2.0规范，支持事务处理。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持混合格式元素ID（整数/字符串）
    - 自动参数值类型转换
    - 详细的错误报告和元素级状态跟踪
    - 严格遵循JSON-RPC 2.0规范

    参数:
    ctx (Context): FastMCP上下文对象
    method (str): JSON-RPC方法名，默认为"UpdateElements"
    params (List[Dict[str, Union[str, int]]]): 更新参数列表，每个字典必须包含:
        - elementId (Union[str, int]): 要更新的元素ID
        - parameterName (str): 参数名称（区分大小写）
        - parameterValue (str): 参数新值

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "元素ID",
                        "name": "元素名称",
                        "familyName": "族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": 错误代码,
                    "message": 错误描述,
                    "data": 错误详情
                },
                "id": request_id
            }

    错误代码:
        -32600 (Invalid Request): 参数验证失败
        -32602 (Invalid Params): 无效参数（元素不存在/参数不存在等）
        -32603 (Internal Error): 内部处理错误
        -32700 (Parse Error): 参数解析错误

    示例:
        > # 批量更新元素参数
        > response = update_elements(ctx, params=[
        ...     {"elementId": 123456, "parameterName": "Comments", "parameterValue": "Test"},
        ...     {"elementId": "789012", "parameterName": "Height", "parameterValue": "3000"}
        ... ])
        > print(response)
        {
            "jsonrpc": "2.0",
            "result": [
                {"elementId": "123456", "name": "基本墙", "familyName": "基本墙"},
                {"elementId": "789012", "name": "单扇门", "familyName": "M_单扇门"}
            ],
            "id": 1
        }

        # 错误情况示例
        > response = update_elements(ctx, params=[
        ...     {"elementId":112,"parameterName":"InvalidParam","parameterValue":"X"} ])
        > print(response)
        > {"jsonrpc":"2.0","error":{"code":-32602,"message":"参数无效","data":"参数'InvalidParam'不存在"},"id":1}

    事务说明:
        所有更新操作在Revit事务组中执行，任一更新失败自动跳过。
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数列表不能为空")

        validated_params = []
        for param in params:
            if not all(key in param for key in ['elementId', 'parameterName', 'parameterValue']):
                raise ValueError("每个参数字典必须包含elementId、parameterName和parameterValue")

            # 构造验证后的参数（保持原始格式）
            validated_param = {
                "elementId": str(param["elementId"]),  # 统一转为字符串以匹配服务器处理
                "parameterName": str(param["parameterName"]),
                "parameterValue": str(param["parameterValue"])
            }
            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"更新元素失败: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"更新元素失败: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def delete_elements(ctx: Context, method: str = "DeleteElements", params: List[dict[str, any]] = None) -> dict:
    """
    批量删除Revit元素，支持字典格式参数，支持批量操作并遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 完全匹配服务器参数处理逻辑
    - 支持字典列表格式参数，每个字典包含elementId键
    - 自动处理整数和字符串格式的elementId
    - 事务化操作确保数据一致性
    - 详细的错误处理和日志记录

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"DeleteElements"
        params (List[Dict[str, Union[int, str]]]): 删除参数列表，每个字典必须包含:
            - elementId (Union[int, str]): 要删除的元素ID

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "删除的元素ID",
                        "name": "元素名称",
                        "familyName": "族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        >>> # 删除多个元素（混合格式）
        >>> response = delete_elements(ctx, params=[
        ...     {"elementId": 5943},
        ...     {"elementId": "5913"},
        ...     {"elementId": 212831}
        ... ])
        >>> print(response)
        {
            "jsonrpc": "2.0",
            "result": [
                {"elementId": "5943", "name": "Wall 1", "familyName": "Basic Wall"},
                {"elementId": "5913", "name": "Door 1", "familyName": "Single-Flush"},
                {"elementId": "212831", "name": "Window 1", "familyName": "Fixed"}
            ],
            "id": 1
        }
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "elementId" not in param:
                raise ValueError("每个参数字典必须包含'elementId'")

            validated_params.append({
                "elementId": str(param["elementId"])
            })

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"删除元素时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"删除元素时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def show_elements(ctx: Context, method: str = "ShowElements", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit视图中高亮显示指定元素，支持批量操作并遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量显示多个元素
    - 自动处理整数和字符串格式的元素ID
    - 元素自动缩放至视图中心并高亮显示
    - 严格的参数验证和错误处理
    - 完全匹配服务器端实现逻辑

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"ShowElements"
        params (List[Dict[str, Union[int, str]]]): 元素参数列表，每个字典必须包含:
            - elementId (Union[int, str]): 要显示的元素ID

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [成功显示的元素ID列表],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": 错误代码,
                    "message": 错误描述,
                    "data": 错误详情
                },
                "id": request_id
            }

    错误代码:
        -32600 (Invalid Request): 参数验证失败
        -32602 (Invalid Params): 无效元素ID或元素不存在
        -32603 (Internal Error): 内部处理错误
        -32700 (Parse Error): 参数解析错误

    示例:
        >>> # 显示多个元素
        >>> response = show_elements(ctx, params=[
        ...     {"elementId": 212781},
        ...     {"elementId": "212792"}
        ... ])
        >>> print(response)
        {"jsonrpc":"2.0","result":[212781,212792],"id":1}

    视图操作:
        成功调用后，元素将在当前视图中:
        1. 自动缩放至视图中心
        2. 高亮显示
        3. 被添加到当前选择集
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数列表不能为空")

        validated_params = []
        for param in params:
            if "elementId" not in param:
                raise ValueError("每个参数必须包含elementId字段")

            # 转换elementId为字符串（匹配服务器处理逻辑）
            element_id = str(param["elementId"])
            validated_params.append({"elementId": element_id})

        # 执行显示操作
        from .server import get_revit_connection
        revit = get_revit_connection()
        result_data = revit.send_command(method, validated_params)
        return result_data

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,  # Invalid Request
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"显示元素时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"显示元素时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def move_elements(ctx: Context, method: str = "MoveElements", params: List[dict[str, any]] = None) -> dict:
    """
    移动Revit元素，支持批量操作，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量移动多个Revit元素
    - 自动处理单位转换（毫米转英尺）
    - 返回移动后的元素详细信息（使用ElementModelRequest格式）
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"MoveElements"
        params (List[Dict]): 移动参数列表，每个字典包含:
            - elementId (str): 要移动的元素ID
            - x (float): X方向移动距离（毫米）
            - y (float): Y方向移动距离（毫米）
            - z (float): Z方向移动距离（毫米）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "移动后的元素ID",
                        "name": "元素名称",
                        "familyName": "族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        response = move_elements(ctx, params=[
            {"elementId": "123456", "x": 100, "y": 200, "z": 0},
            {"elementId": "789012", "x": -50, "y": 0, "z": 300}
        ])
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            required_params = ["elementId", "x", "y", "z"]
            for p in required_params:
                if p not in param:
                    raise ValueError(f"缺少必需参数: '{p}'")

            if not isinstance(param["elementId"], str):
                raise ValueError("'elementId'必须是字符串")

            for coord in ["x", "y", "z"]:
                if not isinstance(param[coord], (int, float)):
                    raise ValueError(f"'{coord}'必须是数字")

            validated_param = {
                "elementId": param["elementId"],
                "x": float(param["x"]),
                "y": float(param["y"]),
                "z": float(param["z"])
            }
            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"移动元素时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"移动元素时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def active_view(ctx: Context, method: str = "ActiveView", params: List[dict[str, any]] = None) -> dict:
    """
    激活并打开Revit中的视图，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持打开单个或多个视图
    - 自动验证视图元素有效性
    - 过滤模板视图
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"ActiveView"
        params (List[Dict]): 视图参数列表，每个字典包含:
            - elementId (Union[int, str]): 视图元素ID

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "视图元素ID",
                        "name": "视图名称",
                        "familyName": "视图族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    错误代码:
        -32600: 无效请求
        -32602: 无效参数（元素不是视图/是模板视图/无效元素）
        -32603: 内部错误
        -32700: 解析错误

    示例:
        # 激活单个视图
        response = active_view(ctx, params=[{"elementId": 123456}])

        # 激活多个视图（最后一个成功激活的视图将成为当前视图）
        response = active_view(ctx, params=[
            {"elementId": 123456},
            {"elementId": "789012"}
        ])

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": [123456, 789012],
            "id": 1
        }

    注意:
        1. 无法激活模板视图（会返回错误）
        2. 如果传入多个视图ID，会依次尝试激活，最后一个成功的视图将成为当前视图
        3. 返回的列表包含所有成功激活的视图ID
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "elementId" not in param:
                raise ValueError("每个参数字典必须包含'elementId'")
            if not isinstance(param["elementId"], (int, str)):
                raise ValueError("'elementId'必须是整数或字符串")

            validated_params.append({
                "elementId": str(param["elementId"])  # 统一转为字符串以匹配服务器处理
            })
        from .server import get_revit_connection
        revit = get_revit_connection()

        # 发送请求并获取响应
        response = revit.send_command(method, validated_params)
        return response

    except ValueError as ve:
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": f"无效参数: {str(ve)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else 1
        }
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return error_response

    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"内部错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else 1
        }
        ctx.log("error", f"激活视图时发生错误: {str(e)}")
        return error_response


def parameter_elements(ctx: Context, method: str = "ParameterElements", params: List[dict[str, any]] = None) -> dict:
    """
    获取Revit元素的参数信息，支持批量查询和特定参数查询，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量查询多个元素的参数
    - 可查询特定参数或元素所有参数
    - 返回参数哈希码、名称和值的完整信息
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"ParameterElements"
        params (List[Dict]): 查询参数列表，每个字典包含:
            - elementId (Union[int, str]): 要查询的元素ID
            - parameterName (str, optional): 要查询的特定参数名称

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": {
                    "elementId1": [
                        {
                            "hashCode": int,
                            "parameterName": str,
                            "parameterValue": str,
                        }
                    ],
                    ...
                },
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        # 查询多个元素的参数
        response = parameter_elements(ctx, params=[
            {"elementId": 212792, "parameterName": "注释"},  # 获取特定参数
            {"elementId": 212781}  # 获取所有参数
        ])

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": {
                "212792": [
                    {
                        "hashCode": 12345,
                        "parameterName": "注释",
                        "parameterValue": "示例注释",
                    }
                ],
                "212781": [
                    {
                        "hashCode": 23456,
                        "parameterName": "长度",
                        "parameterValue": "5000",
                    },
                    ...
                ]
            },
            "id": 1
        }
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "elementId" not in param:
                raise ValueError("每个参数字典必须包含'elementId'")

            # 统一转换elementId为字符串
            element_id = str(param["elementId"])
            validated_param = {"elementId": element_id}

            # 处理可选的parameterName参数
            if "parameterName" in param:
                if not isinstance(param["parameterName"], str):
                    raise ValueError("'parameterName'必须是字符串")
                validated_param["parameterName"] = param["parameterName"]

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"获取元素参数时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"获取元素参数时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def get_locations(ctx: Context, method: str = "GetLocations", params: List[dict[str, any]] = None) -> dict:
    """
    获取Revit元素的位置信息，支持点和曲线元素，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量查询多个元素的位置
    - 自动处理单位转换（英尺转毫米）
    - 支持点位置和曲线位置（直线和圆弧）
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"GetLocations"
        params (List[Dict]): 查询参数列表，每个字典包含:
            - elementId (Union[str, int]): 要查询的元素ID,优先使用str类型Id

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": {
                    "elementId1": [
                        {
                            "X": float,  # X坐标（毫米）
                            "Y": float,  # Y坐标（毫米）
                            "Z": float   # Z坐标（毫米）
                        },
                        ...
                    ],
                    ...
                },
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    错误代码:
        -32600: 无效请求
        -32602: 无效参数（元素不存在等）
        -32603: 内部错误
        -32700: 解析错误

    示例:
        # 查询多个元素的位置
        response = get_location(ctx, params=[
            {"elementId": 123456},
            {"elementId": "789012"}
        ])

        # 输出示例（XYZ元素）
        {
            "jsonrpc": "2.0",
            "result": {
                "123456": [
                    {"X": 1000.0, "Y": 2000.0, "Z": 0.0}
                ]
            },
            "id": 1
        }

        # 输出示例（Line元素）
        {
            "jsonrpc": "2.0",
            "result": {
                "789012": [
                    {"X": 0.0, "Y": 0.0, "Z": 0.0},
                    {"X": 5000.0, "Y": 0.0, "Z": 0.0}
                ]
            },
            "id": 1
        }
        # 输出示例（Arc元素）
        {
            "jsonrpc": "2.0",
            "result": {
                "789012": [
                    {"X": 0.0, "Y": 0.0, "Z": 0.0},
                    {"X": 5000.0, "Y": 0.0, "Z": 0.0}
                    {"X": 2500.0, "Y": 1200, "Z": 0.0}
                ]
            },
            "id": 1
        }

        用途:找到定位后可用于创建门窗这种带有主体的族,族插入点就可以通过这个计算出来

    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "elementId" not in param:
                raise ValueError("每个参数字典必须包含'elementId'")

            if isinstance(param, list):
                for item in param:
                    element_id = str(item.get("elementId"))
                    validated_params.append({"elementId": element_id})
            else:
                element_id = str(param.get("elementId"))
                validated_params.append({"elementId": element_id})

        from .server import get_revit_connection
        revit = get_revit_connection()

        # 发送请求并获取响应
        response = revit.send_command(method, validated_params)
        return response

    except ValueError as ve:
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": f"无效参数: {str(ve)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else 1
        }
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return error_response

    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"内部错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else 1
        }
        ctx.log("error", f"获取元素位置时发生错误: {str(e)}")
        return error_response


def create_levels(ctx: Context, method: str = "CreateLevels", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建标高，支持批量创建，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个标高
    - 自动处理单位转换（毫米转英尺）
    - 自动处理标高名称冲突
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateLevels"
        params (List[Dict]): 标高参数列表，每个字典包含:
            - elevation (float): 标高高度（毫米）
            - name (str, optional): 标高名称（可选，默认为"Level_{elevation}"）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "创建的标高元素ID",
                        "name": "标高名称",
                        "familyName": "标高族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        # 创建多个标高
        response = create_levels(ctx, params=[
            {"elevation": 8000, "name": "Level_3"},
            {"elevation": 12000}  # 自动生成名称"Level_12000"
        ])
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "elevation" not in param:
                raise ValueError("每个参数字典必须包含'elevation'")

            if not isinstance(param["elevation"], (int, float)):
                raise ValueError("'elevation'必须是数字")

            # 构建标准化参数
            validated_param = {
                "elevation": float(param["elevation"])
            }

            # 可选参数处理
            if "name" in param:
                if not isinstance(param["name"], str):
                    raise ValueError("'name'必须是字符串")
                validated_param["name"] = param["name"]

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建标高时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"创建标高时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_floor_plan_views(ctx: Context, method: str = "CreateFloorPlanViews",
                            params: List[dict[str, any]] = None) -> dict:
    """
    根据给定标高创建楼层平面视图，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个楼层平面视图
    - 自动跳过已存在的视图，避免重复创建
    - 完善的错误处理机制

    参数:
    ctx (Context): FastMCP上下文对象
    method (str): JSON-RPC方法名，默认为 CreateFloorPlanViews
    params (List[Dict]): 视图参数列表，每个字典包含:
        - levelId (str): 标高的ElementId
        - viewName (str): 要创建的视图名称

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "视图元素ID",
                        "name": "视图名称",
                        "familyName": "视图族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        response = create_floor_plan_views(ctx, params=[
            {"levelId": "123456", "viewName": "Level 1 - Floor Plan"},
            {"levelId": "789012", "viewName": "Level 2 - Floor Plan"}
        ])

        # 返回示例
        {
            "jsonrpc": "2.0",
            "result": [
                {
                    "elementId": "123789",
                    "name": "Level 1 - Floor Plan",
                    "familyName": "Floor Plan"
                },
                {
                    "elementId": "123790",
                    "name": "Level 2 - Floor Plan",
                    "familyName": "Floor Plan"
                }
            ],
            "id": 1
        }
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "levelId" not in param or "viewName" not in param:
                raise ValueError("每个参数字典必须包含'levelId'和'viewName'")

            validated_param = {
                "levelId": str(param["levelId"]),
                "viewName": str(param["viewName"])
            }
            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建楼层平面视图时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"创建楼层平面视图时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_grids(ctx: Context, method: str = "CreateGrids", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建轴网，支持直线轴网和弧线轴网，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个轴网
    - 支持直线轴网和弧线轴网创建
    - 自动处理单位转换（毫米转英尺）
    - 自动处理轴网名称冲突
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateGrids"
        params (List[Dict]): 轴网参数列表，每个字典包含:
            - startX (float): 起点X坐标（毫米）
            - startY (float): 起点Y坐标（毫米）
            - endX (float): 终点X坐标（毫米）
            - endY (float): 终点Y坐标（毫米）
            - name (str, optional): 轴网名称（可选）
            - centerX (float, optional): 弧线轴网的圆心X坐标（毫米）
            - centerY (float, optional): 弧线轴网的圆心Y坐标（毫米）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "轴网元素ID",
                        "name": "轴网名称",
                        "familyName": "轴网族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        # 创建直线轴网和弧线轴网
        response = create_grids(ctx, params=[
            {
                "name": "Grid_A",
                "startX": 0,
                "startY": 0,
                "endX": 10000,
                "endY": 0
            },
            {
                "name": "Grid_B",
                "startX": 5000,
                "startY": 0,
                "endX": 5000,
                "endY": 10000,
                "centerX": 5000,
                "centerY": 5000
            }
        ])

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": [
                {
                    "elementId": "212801",
                    "name": "Grid_A",
                    "familyName": "轴网"
                },
                {
                    "elementId": "212802",
                    "name": "Grid_B",
                    "familyName": "轴网"
                }
            ],
            "id": 1
        }
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            # 必需参数检查
            required_params = ["startX", "startY", "endX", "endY"]
            for p in required_params:
                if p not in param:
                    raise ValueError(f"缺少必需参数: '{p}'")
                if not isinstance(param[p], (int, float)):
                    raise ValueError(f"'{p}'必须是数字")

            # 构建标准化参数
            validated_param = {
                "startX": float(param["startX"]),
                "startY": float(param["startY"]),
                "endX": float(param["endX"]),
                "endY": float(param["endY"])
            }

            # 可选参数处理
            if "name" in param:
                if not isinstance(param["name"], str):
                    raise ValueError("'name'必须是字符串")
                validated_param["name"] = param["name"]

            # 弧线参数检查（必须同时存在或不存在）
            has_center_x: bool = "centerX" in param
            has_center_y: bool = "centerY" in param
            if has_center_x != has_center_y:
                raise ValueError("centerX和centerY必须同时提供或同时省略")

            if has_center_x:
                if not isinstance(param["centerX"], (int, float)) or not isinstance(param["centerY"], (int, float)):
                    raise ValueError("centerX和centerY必须是数字")
                validated_param["centerX"] = float(param["centerX"])
                validated_param["centerY"] = float(param["centerY"])

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建轴网时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"创建轴网时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_walls(ctx: Context, method: str = "CreateWalls", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建墙体，支持批量创建，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个墙体
    - 自动处理单位转换（毫米转英尺）
    - 自动创建或匹配符合厚度的墙类型
    - 支持指定标高或使用默认标高
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateWalls"
        params (List[Dict]): 墙体参数列表，每个字典包含:
            - startX (float): 起点X坐标（毫米）
            - startY (float): 起点Y坐标（毫米）
            - endX (float): 终点X坐标（毫米）
            - endY (float): 终点Y坐标（毫米）
            - height (float): 墙体高度（毫米）
            - width (float): 墙体厚度（毫米）
            - elevation (float, optional): 墙体底部标高（毫米，默认为0）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "墙体元素ID",
                        "name": "墙体名称",
                        "familyName": "墙体族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        response = create_walls(ctx, params=[
            {"startX": 0, "startY": 0, "endX": 5000, "endY": 0, "height": 3000, "width": 200},
            {"startX": 5000, "startY": 0, "endX": 5000, "endY": 5000, "height": 3000, "width": 200, "elevation": 1000}
        ])

        # 返回示例
        {
            "jsonrpc": "2.0",
            "result": [
                {
                    "elementId": "123456",
                    "name": "基本墙",
                    "familyName": "基本墙"
                },
                {
                    "elementId": "123457",
                    "name": "基本墙",
                    "familyName": "基本墙"
                }
            ],
            "id": 1
        }
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            required_params = ["startX", "startY", "endX", "endY", "height", "width"]
            for p in required_params:
                if p not in param:
                    raise ValueError(f"缺少必需参数: '{p}'")
                if not isinstance(param[p], (int, float)):
                    raise ValueError(f"'{p}'必须是数字")

            validated_param = {
                "startX": float(param["startX"]),
                "startY": float(param["startY"]),
                "endX": float(param["endX"]),
                "endY": float(param["endY"]),
                "height": float(param["height"]),
                "width": float(param["width"])
            }

            if "elevation" in param:
                if not isinstance(param["elevation"], (int, float)):
                    raise ValueError("'elevation'必须是数字")
                validated_param["elevation"] = float(param["elevation"])

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        return revit.send_command(method, validated_params)

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": str(ve)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建墙体时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_rooms(ctx: Context, method: str = "CreateRooms", params: List[dict[str, any]] = None) -> dict:
    """
    在指定标高上创建房间，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量在多个标高上创建房间
    - 自动验证标高元素有效性
    - 事务化操作确保数据一致性
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateRooms"
        params (List[Dict]): 标高参数列表，每个字典包含:
            - elementId (Union[int, str]): 元素ID

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "房间元素ID",
                        "name": "房间名称",
                        "familyName": "房间族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    错误代码:
        -32600: 无效请求
        -32602: 无效参数（元素不是标高或无效）
        -32603: 内部错误
        -32700: 解析错误

    示例:
        # 在多个标高上创建房间
        response = create_rooms(ctx, params=[
            {"elementId": 123456},
            {"elementId": "789012"}
        ])

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": [
                {
                    "elementId": "212801",
                    "name": "房间 1",
                    "familyName": "房间"
                },
                {
                    "elementId": "212802",
                    "name": "房间 2",
                    "familyName": "房间"
                }
            ],
            "id": 1
        }

    注意:
        1. 会在指定标高的所有封闭区域创建房间
        2. 返回的房间信息列表顺序与创建顺序一致
        3. 如果标高没有封闭区域，则不会创建房间但也不会报错
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "elementId" not in param:
                raise ValueError("每个参数字典必须包含'elementId'")

            # 统一转为字符串以匹配服务器处理
            validated_params.append({
                "elementId": str(param["elementId"])
            })

        from .server import get_revit_connection
        revit = get_revit_connection()

        # 发送请求并获取响应
        response = revit.send_command(method, validated_params)
        return response

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建房间时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"创建房间时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_room_tags(ctx: Context, method: str = "CreateRoomTags", params: List[dict[str, any]] = None) -> dict:
    """
    给定平面视图ID，获取当前视图中所有房间，并为其创建房间标签，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持在指定平面视图中为所有房间创建标签
    - 自动跳过已有标签的房间
    - 返回已创建的房间标签信息
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateRoomTags"
        params (List[Dict]): 视图参数列表，每个字典包含:
            - elementId (Union[int, str]): 平面视图元素ID

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "房间标签元素ID",
                        "name": "房间标签名称",
                        "familyName": "房间标签族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        # 为单个视图中的所有房间创建标签
        response = create_room_tags(ctx, params=[{"elementId": 123456}])

        # 为多个视图中的所有房间创建标签
        response = create_room_tags(ctx, params=[
            {"elementId": 123456},
            {"elementId": "789012"}
        ])

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": [
                {
                    "elementId": "212801",
                    "name": "房间标签 1",
                    "familyName": "房间标签"
                },
                {
                    "elementId": "212802",
                    "name": "房间标签 2",
                    "familyName": "房间标签"
                }
            ],
            "id": 1
        }

    注意:
        1. 如果视图不是平面视图，则会返回错误。
        2. 如果一个房间已经有标签，则不会重复创建。
        3. 返回的结果包含所有成功创建的房间标签信息。
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if "elementId" not in param:
                raise ValueError("每个参数字典必须包含'elementId'")
            validated_params.append({
                "elementId": str(param["elementId"])  # 转为字符串以匹配服务器处理逻辑
            })

        from .server import get_revit_connection
        revit = get_revit_connection()

        # 发送请求并获取响应
        response = revit.send_command(method, validated_params)
        return response

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建房间标签时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"创建房间标签时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_floors(ctx: Context, method: str = "CreateFloors", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建楼板，支持批量创建，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个楼板
    - 自动处理单位转换（毫米转英尺）
    - 自动匹配楼板类型或使用默认类型
    - 支持结构楼板和非结构楼板
    - 自动根据z值标高确定楼层
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateFloors"
        params (List[Dict]): 楼板参数列表，每个字典包含:
            - boundaryPoints (List[Dict]): 楼板边界点列表，每个点包含:
                - x (float): X坐标（毫米）
                - y (float): Y坐标（毫米）
                - z (float): Z坐标（毫米）
            - floorTypeName (str, optional): 楼板类型名称（可选）
            - structural (bool, optional): 是否为结构楼板（默认为False）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
        成功时: {
            "jsonrpc": "2.0",
            "result": [
                {
                    "elementId": "楼板元素ID",
                    "name": "楼板名称",
                    "familyName": "楼板族名称"
                },
                ...
            ],
            "id": request_id
        }
        失败时: {
            "jsonrpc": "2.0",
            "error": {
                "code": int,
                "message": str,
                "data": any
            },
            "id": request_id
        }

    示例:
        # 创建多个楼板
        response = create_floors(ctx, params=[
            {
                "boundaryPoints": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 5000, "y": 0, "z": 0},
                    {"x": 5000, "y": 5000, "z": 0},
                    {"x": 0, "y": 5000, "z": 0},
                    {"x": 0, "y": 0, "z": 0}
                ],
                "floorTypeName": "常规 - 150mm",
                "structural": True
            },
            {
                "boundaryPoints": [
                    {"x": 0, "y": 0, "z": 3000},
                    {"x": 5000, "y": 0, "z": 3000},
                    {"x": 5000, "y": 5000, "z": 3000},
                    {"x": 0, "y": 5000, "z": 3000},
                    {"x": 0, "y": 0, "z": 3000}
                ],
                "floorTypeName": "常规 - 200mm"
            }
        ])

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": [213001, 213002],
            "id": 1
        }
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            # 必需参数检查
            if "boundaryPoints" not in param:
                raise ValueError("缺少必需参数: 'boundaryPoints'")

            if not isinstance(param["boundaryPoints"], list) or len(param["boundaryPoints"]) < 3:
                raise ValueError("'boundaryPoints'必须包含至少3个点的列表")

            # 验证每个边界点
            validated_points = []
            for point in param["boundaryPoints"]:
                if not isinstance(point, dict):
                    raise ValueError("边界点必须是字典格式")

                for coord in ["x", "y", "z"]:
                    if coord not in point:
                        raise ValueError(f"边界点缺少坐标: '{coord}'")
                    if not isinstance(point[coord], (int, float)):
                        raise ValueError(f"坐标'{coord}'必须是数字")

                validated_points.append({
                    "x": float(point["x"]),
                    "y": float(point["y"]),
                    "z": float(point["z"])
                })

            # 构建标准化参数
            validated_param = {
                "boundaryPoints": validated_points
            }

            # 可选参数处理
            if "floorTypeName" in param:
                if not isinstance(param["floorTypeName"], str):
                    raise ValueError("'floorTypeName'必须是字符串")
                validated_param["floorTypeName"] = param["floorTypeName"]

            if "structural" in param:
                if not isinstance(param["structural"], bool):
                    raise ValueError("'structural'必须是布尔值")
                validated_param["structural"] = param["structural"]

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        result = revit.send_command(method, validated_params)
        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建楼板时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"创建楼板时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_door_windows(ctx: Context, method: str = "CreateDoorWindows", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建门窗族实例，支持批量创建，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个门窗族实例
    - 自动处理单位转换（毫米转英尺）
    - 支持指定族类型和类别
    - 支持指定主体墙ElementId
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateDoorWindows"
        params (List[Dict]): 门窗参数列表，每个字典包含:
            - categoryName (str): 类别名称（门或窗）
            - familyName (str): 族名称
            - name (str): 类型名称
            - startX (float): 放置点X坐标（毫米）
            - startY (float): 放置点Y坐标（毫米）
            - startZ (float): 放置点Z坐标（毫米）
            - hostId (str): 主体墙的ElementId
            - offset (str, optional): 底高度偏移值

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "门窗元素ID",
                        "name": "门窗名称",
                        "familyName": "门窗族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        response = create_door_windows(ctx, params=[
            {
                "categoryName": "门",
                "familyName": "单扇门",
                "name": "915 x 2134mm",
                "startX": 5000,
                "startY": 2500,
                "startZ": 0,
                "hostId": "123456",
                "offset": "0"
            },
            {
                "categoryName": "窗",
                "familyName": "固定窗",
                "name": "0915 x 1220mm",
                "startX": 8000,
                "startY": 2500,
                "startZ": 1000,
                "hostId": "123456",
                "offset": "900"
            }
        ])
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            required_params = ["categoryName", "name", "startX", "startY", "startZ", "hostId"]
            for p in required_params:
                if p not in param:
                    raise ValueError(f"缺少必需参数: '{p}'")

            # 验证数值类型参数
            numeric_params = ["startX", "startY", "startZ"]
            for p in numeric_params:
                if not isinstance(param[p], (int, float)):
                    raise ValueError(f"'{p}'必须是数字")

            validated_param = {
                "categoryName": str(param["categoryName"]),
                "name": str(param["name"]),
                "startX": float(param["startX"]),
                "startY": float(param["startY"]),
                "startZ": float(param["startZ"]),
                "hostId": str(param["hostId"])
            }

            # 可选参数
            if "familyName" in param:
                validated_param["familyName"] = str(param["familyName"])

            if "offset" in param:
                validated_param["offset"] = str(param["offset"])
            else:
                validated_param["offset"] = "0"  # 默认偏移值为0

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        return revit.send_command(method, validated_params)

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": str(ve)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建门窗族实例时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_ducts(ctx: Context, method: str = "CreateDucts", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建风管，支持批量创建，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个风管
    - 自动处理单位转换（毫米转英尺）
    - 自动匹配风管类型和系统类型
    - 支持指定风管尺寸
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateDucts"
        params (List[Dict]): 风管参数列表，每个字典包含:
            - ductTypeName (str): 风管类型名称
            - systemTypeName (str): 风管系统类型名称
            - startX (float): 起点X坐标（毫米）
            - startY (float): 起点Y坐标（毫米）
            - startZ (float): 起点Z坐标（毫米）
            - endX (float): 终点X坐标（毫米）
            - endY (float): 终点Y坐标（毫米）
            - endZ (float): 终点Z坐标（毫米）
            - width (float): 风管宽度（毫米）
            - height (float): 风管高度（毫米）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "元素ID",
                        "name": "名称",
                        "familyName": "族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        response = create_ducts(ctx, params=[
            {
                "ductTypeName": "默认",
                "systemTypeName": "送风",
                "startX": 0,
                "startY": 0,
                "startZ": 3000,
                "endX": 5000,
                "endY": 0,
                "endZ": 3000,
                "width": 300,
                "height": 200
            },
            {
                "ductTypeName": "矩形风管",
                "systemTypeName": "送风",
                "startX": 5000,
                "startY": 0,
                "startZ": 3000,
                "endX": 5000,
                "endY": 5000,
                "endZ": 3000,
                "width": 300,
                "height": 200
            }
        ])
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            required_params = [
                "ductTypeName", "systemTypeName",
                "startX", "startY", "startZ",
                "endX", "endY", "endZ",
                "width", "height"
            ]
            for p in required_params:
                if p not in param:
                    raise ValueError(f"缺少必需参数: '{p}'")

            # 验证数值类型参数
            numeric_params = [
                "startX", "startY", "startZ",
                "endX", "endY", "endZ",
                "width", "height"
            ]
            for p in numeric_params:
                if not isinstance(param[p], (int, float)):
                    raise ValueError(f"'{p}'必须是数字")

            validated_param = {
                "ductTypeName": str(param["ductTypeName"]),
                "systemTypeName": str(param["systemTypeName"]),
                "startX": float(param["startX"]),
                "startY": float(param["startY"]),
                "startZ": float(param["startZ"]),
                "endX": float(param["endX"]),
                "endY": float(param["endY"]),
                "endZ": float(param["endZ"]),
                "width": float(param["width"]),
                "height": float(param["height"])
            }

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        return revit.send_command(method, validated_params)

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": str(ve)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建风管时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_pipes(ctx: Context, method: str = "CreatePipes", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建管道，支持批量创建，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个管道
    - 自动处理单位转换（毫米转英尺）
    - 自动匹配管道类型和系统类型
    - 支持指定管道直径
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreatePipes"
        params (List[Dict]): 管道参数列表，每个字典包含:
            - pipeTypeName (str): 管道类型名称
            - systemTypeName (str): 管道系统类型名称
            - startX (float): 起点X坐标（毫米）
            - startY (float): 起点Y坐标（毫米）
            - startZ (float): 起点Z坐标（毫米）
            - endX (float): 终点X坐标（毫米）
            - endY (float): 终点Y坐标（毫米）
            - endZ (float): 终点Z坐标（毫米）
            - diameter (float): 管道直径（毫米）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "元素ID",
                        "name": "名称",
                        "familyName": "族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        response = create_pipes(ctx, params=[
            {
                "pipeTypeName": "默认",
                "systemTypeName": "循环供水",
                "startX": 0,
                "startY": 0,
                "startZ": 3000,
                "endX": 5000,
                "endY": 0,
                "endZ": 3000,
                "diameter": 50
            },
            {
                "pipeTypeName": "标准",
                "systemTypeName": "生活热水",
                "startX": 5000,
                "startY": 0,
                "startZ": 3000,
                "endX": 5000,
                "endY": 5000,
                "endZ": 3000,
                "diameter": 40
            }
        ])
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            required_params = [
                "pipeTypeName", "systemTypeName",
                "startX", "startY", "startZ",
                "endX", "endY", "endZ",
                "diameter"
            ]
            for p in required_params:
                if p not in param:
                    raise ValueError(f"缺少必需参数: '{p}'")

            # 验证数值类型参数
            numeric_params = [
                "startX", "startY", "startZ",
                "endX", "endY", "endZ",
                "diameter"
            ]
            for p in numeric_params:
                if not isinstance(param[p], (int, float)):
                    raise ValueError(f"'{p}'必须是数字")

            validated_param = {
                "pipeTypeName": str(param["pipeTypeName"]),
                "systemTypeName": str(param["systemTypeName"]),
                "startX": float(param["startX"]),
                "startY": float(param["startY"]),
                "startZ": float(param["startZ"]),
                "endX": float(param["endX"]),
                "endY": float(param["endY"]),
                "endZ": float(param["endZ"]),
                "diameter": float(param["diameter"])
            }

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        return revit.send_command(method, validated_params)

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": str(ve)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建管道时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_cable_trays(ctx: Context, method: str = "CreateCableTrays", params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建电缆桥架，支持批量创建，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个电缆桥架
    - 自动处理单位转换（毫米转英尺）
    - 自动匹配桥架类型
    - 支持指定桥架宽度和高度
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateCableTrays"
        params (List[Dict]): 桥架参数列表，每个字典包含:
            - cableTrayTypeName (str): 桥架类型名称
            - startX (float): 起点X坐标（毫米）
            - startY (float): 起点Y坐标（毫米）
            - startZ (float): 起点Z坐标（毫米）
            - endX (float): 终点X坐标（毫米）
            - endY (float): 终点Y坐标（毫米）
            - endZ (float): 终点Z坐标（毫米）
            - width (float): 桥架宽度（毫米）
            - height (float): 桥架高度（毫米）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "元素ID",
                        "name": "名称",
                        "familyName": "族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        response = create_cable_trays(ctx, params=[
            {
                "cableTrayTypeName": "梯级式电缆桥架",
                "startX": 0,
                "startY": 0,
                "startZ": 3000,
                "endX": 5000,
                "endY": 0,
                "endZ": 3000,
                "width": 200,
                "height": 100
            },
            {
                "cableTrayTypeName": "标准",
                "startX": 5000,
                "startY": 0,
                "startZ": 3000,
                "endX": 5000,
                "endY": 5000,
                "endZ": 3000,
                "width": 200,
                "height": 100
            }
        ])
    """
    try:
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            required_params = [
                "cableTrayTypeName",
                "startX", "startY", "startZ",
                "endX", "endY", "endZ",
                "width", "height"
            ]
            for p in required_params:
                if p not in param:
                    raise ValueError(f"缺少必需参数: '{p}'")

            # 验证数值类型参数
            numeric_params = [
                "startX", "startY", "startZ",
                "endX", "endY", "endZ",
                "width", "height"
            ]
            for p in numeric_params:
                if not isinstance(param[p], (int, float)):
                    raise ValueError(f"'{p}'必须是数字")

            validated_param = {
                "cableTrayTypeName": str(param["cableTrayTypeName"]),
                "startX": float(param["startX"]),
                "startY": float(param["startY"]),
                "startZ": float(param["startZ"]),
                "endX": float(param["endX"]),
                "endY": float(param["endY"]),
                "endZ": float(param["endZ"]),
                "width": float(param["width"]),
                "height": float(param["height"])
            }

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        return revit.send_command(method, validated_params)

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": str(ve)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建电缆桥架时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_family_instances(ctx: Context, method: str = "CreateFamilyInstances",
                            params: List[dict[str, any]] = None) -> dict:
    """
    在Revit中创建族实例，支持多种放置方式，遵循JSON-RPC 2.0规范。
    mcp_tool使用时params不要有任何注释信息

    特性:
    - 支持批量创建多个族实例
    - 自动处理单位转换（毫米转英尺）
    - 支持多种放置类型：
        - 基于标高放置
        - 基于视图放置
        - 基于工作平面放置
        - 基于宿主放置
        - 基于曲线放置
    - 支持旋转和偏移
    - 自动匹配族类型和类别
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateFamilyInstances"
        params (List[Dict]): 族实例参数列表，每个字典包含:
            - categoryName (str): 支持按类别BuiltInCategory或者Category.Name查找（如"OST_Walls","OST_Doors", "墙", "门", "结构框架"等）
            - name (str): 族类型名称
            - startX (float): 起点X坐标（毫米）
            - startY (float): 起点Y坐标（毫米）
            - startZ (float): 起点Z坐标（毫米）
            - familyName (str, optional): 族名称（可选，用于更精确匹配）
            - endX (float, optional): 终点X坐标（毫米，默认等于startX）
            - endY (float, optional): 终点Y坐标（毫米，默认等于startY）
            - endZ (float, optional): 终点Z坐标（毫米，默认等于startZ）
            - hostId (str, optional): 宿主元素ID（可选）
            - viewName (str, optional): 视图名称（可选）
            - rotationAngle (float, optional): 旋转角度（度，默认0）
            - offset (float, optional): 偏移距离（毫米，默认0）

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "elementId": "元素ID",
                        "name": "名称",
                        "familyName": "族名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        # 创建多个族实例
        response = create_family_instances(ctx, params=[
            # 基于标高的门
            {
                "categoryName": "窗",
                "name": "0406 x 0610mm",
                "startX": 1000,
                "startY": 2000,
                "startZ": 0,
                "hostId": 225535,
                "level": "标高 1",
            },
            # 基于视图的家具
            {
                "categoryName": "OST_Furniture",
                "name": "办公桌",
                "startX": 3000,
                "startY": 4000,
                "startZ": 0,
                "viewName": "标高 1",
                "rotationAngle": 90
            },
            # 基于曲线的梁
            {
                "categoryName": "OST_StructuralFraming",
                "name": "H型钢梁",
                "startX": 0,
                "startY": 0,
                "startZ": 3000,
                "endX": 5000,
                "endY": 0,
                "endZ": 3000
            }
        ])

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": [213101, 213102, 213103],
            "id": 1
        }
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            # 必需参数检查
            required_params = ["categoryName", "name", "startX", "startY", "startZ"]
            for p in required_params:
                if p not in param:
                    raise ValueError(f"缺少必需参数: '{p}'")
                if p in ["startX", "startY", "startZ"] and not isinstance(param[p], (int, float)):
                    raise ValueError(f"'{p}'必须是数字")
                if p in ["categoryName", "name"] and not isinstance(param[p], str):
                    raise ValueError(f"'{p}'必须是字符串")

            # 构建标准化参数
            validated_param = {
                "categoryName": param["categoryName"],
                "name": param["name"],
                "startX": float(param["startX"]),
                "startY": float(param["startY"]),
                "startZ": float(param["startZ"])
            }

            # 可选参数处理
            optional_params = {
                "familyName": str,
                "endX": (int, float),
                "endY": (int, float),
                "endZ": (int, float),
                "hostId": (str, int),
                "viewName": str,
                "rotationAngle": (int, float),
                "offset": (int, float)
            }

            for param_name, param_type in optional_params.items():
                if param_name in param:
                    if not isinstance(param[param_name], param_type):
                        raise ValueError(f"'{param_name}'必须是{param_type.__name__}")
                    validated_param[param_name] = param[param_name]

            # 设置默认值
            if "endX" not in validated_param:
                validated_param["endX"] = validated_param["startX"]
            if "endY" not in validated_param:
                validated_param["endY"] = validated_param["startY"]
            if "endZ" not in validated_param:
                validated_param["endZ"] = validated_param["startZ"]
            if "rotationAngle" not in validated_param:
                validated_param["rotationAngle"] = 0

            validated_params.append(validated_param)
        from .server import get_revit_connection
        revit = get_revit_connection()

        # 构建调用方法的参数
        result = revit.send_command(method, validated_params)

        return result

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": str(ve),
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"创建族实例时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"创建族实例时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def link_dwg_and_activate_view(ctx: Context, method: str = "LinkDWGAndActivateView",
                               params: List[dict[str, any]] = None) -> dict:
    """
    链接本地 DWG 图纸并激活指定视图，遵循JSON-RPC 2.0规范。

    特性:
    - 支持链接本地 DWG 图纸到当前项目
    - 支持激活指定视图
    - 自动验证参数有效性
    - 完善的错误处理机制

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"LinkDWGAndActivateView"
        params (List[Dict]): 参数列表，每个字典包含:
            - filePath (str): 本地 DWG 图纸路径
            - viewName (str): 要激活的视图名称

    返回:
        dict: JSON-RPC 2.0格式的响应，结构为:
            成功时: {
                "jsonrpc": "2.0",
                "result": [
                    {
                        "filePath": "链接的文件路径",
                        "viewId": "视图ID",
                        "viewName": "视图名称"
                    },
                    ...
                ],
                "id": request_id
            }
            失败时: {
                "jsonrpc": "2.0",
                "error": {
                    "code": int,
                    "message": str,
                    "data": any
                },
                "id": request_id
            }

    示例:
        response = link_and_activate_view(ctx, params=[
            {"filePath": "C:\\Projects\\SampleDrawing.dwg", "viewName": "Level 1"}
        ])

        # 输出示例
        {
            "jsonrpc": "2.0",
            "result": [
                {
                    "filePath": "C:\\Projects\\SampleDrawing.dwg",
                    "viewId": 123456,
                    "viewName": "Level 1"
                }
            ],
            "id": 1
        }
    """
    try:
        # 参数验证
        if not params:
            raise ValueError("参数错误：'params'不能为空")

        validated_params = []
        for param in params:
            if not isinstance(param, dict):
                raise ValueError("每个参数必须是字典")

            if not param.get("filePath") or not isinstance(param["filePath"], str):
                raise ValueError("'filePath'字段必须是字符串且不能为空")

            validated_params.append({
                "filePath": param["filePath"],
                "viewName": param["viewName"]
            })

        from .server import get_revit_connection
        revit = get_revit_connection()

        # 发送请求并获取响应
        response = revit.send_command(method, validated_params)
        return response

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": f"无效参数: {str(ve)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }
    except Exception as e:
        ctx.log("error", f"链接和激活视图时发生错误: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"链接和激活视图时发生错误: {str(e)}",
                "data": params
            },
            "id": ctx.request_id if hasattr(ctx, "request_id") else None
        }


def create_sheets(ctx: Context, method: str = "CreateSheets", params: List[dict] = None,
                  request_id: int = None) -> dict:
    """
    批量创建Revit图纸并添加指定视图，遵循JSON-RPC 2.0规范。

    特性:
    - 支持批量创建带编号和名称的图纸
    - 可指定标题块类型
    - 支持在图纸上添加视图
    - 完善的参数验证和错误处理

    参数:
        ctx (Context): FastMCP上下文对象
        method (str): JSON-RPC方法名，默认为"CreateSheets"
        params (List[Dict]): 参数列表，每个字典包含:
            - number (str): 图纸编号（必填）
            - name (str): 图纸名称（必填）
            - titleBlockType (str): 标题块类型名称（必填）
            - viewName (str, optional): 要添加到图纸的视图名称（可选）
        request_id (int, optional): 请求ID，默认自动生成

    返回:
        dict: JSON-RPC 2.0格式的响应

    示例:
        response = create_sheets(ctx, params=[
            {
                "number": "A101",
                "name": "首层平面图",
                "titleBlockType": "A0 公制",
                "viewName": "标高 1"
            },
            {
                "number": "A102",
                "name": "二层平面图",
                "titleBlockType": "A0 公制"
            }
        ])
    """
    try:
        # 参数验证
        if not params or not isinstance(params, list):
            raise ValueError("参数错误：'params'必须是非空列表")

        validated_params = []
        for i, param in enumerate(params):
            if not isinstance(param, dict):
                raise ValueError(f"参数[{i}]必须是字典类型")

            # 必填字段检查
            for field in ["number", "name", "titleBlockType"]:
                if field not in param or not param[field]:
                    raise ValueError(f"参数[{i}]中的'{field}'字段不能为空")

            validated_param = {
                "number": str(param["number"]),
                "name": str(param["name"]),
                "titleBlockType": str(param["titleBlockType"])
            }

            # 可选参数处理
            if "viewName" in param and param["viewName"]:
                validated_param["viewName"] = str(param["viewName"])

            validated_params.append(validated_param)

        from .server import get_revit_connection
        revit = get_revit_connection()
        response = revit.send_command(method, validated_params)

        return response

    except ValueError as ve:
        ctx.log("error", f"参数验证失败: {str(ve)}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,  # Invalid params
                "message": f"无效参数: {str(ve)}",
                "data": params
            },
            "id": request_id
        }
    except Exception as e:
        import traceback
        ctx.log("error", f"创建图纸时发生错误: {str(e)}\n{traceback.format_exc()}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": f"创建图纸时发生错误: {str(e)}",
                "data": params
            },
            "id": request_id
        }
