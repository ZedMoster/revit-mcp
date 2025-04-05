# -*- coding: utf-8 -*-
# server.py
# Copyright (c) 2025 zedmoster
# Revit integration through the Model Context Protocol.

import logging
import types
import inspect
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool as MCPTool
from .revit_connection import RevitConnection
from .resources import get_all_builtin_category, get_greeting, list_resource_templates
from .prompts import asset_creation_strategy, list_prompts
from .tools import *

# 创建日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

# 创建日志器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 防止日志重复输出
if not logger.handlers:
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.propagate = False

# 全局资源连接
_connection: Optional[RevitConnection] = None
_enabled: bool = False
_port: int = 8080

# 工具分类
ARCHITECTURAL_TOOLS = [
    create_levels, create_floor_plan_views, create_grids, create_walls, create_floors,
    create_door_windows, create_rooms, create_room_tags, create_family_instances, create_sheets
]

MEP_TOOLS = [
    create_ducts, create_pipes, create_cable_trays
]

GENERAL_TOOLS = [
    get_commands, execute_commands, call_func,
    find_elements, update_elements, delete_elements, parameter_elements, get_locations, move_elements,
    show_elements, active_view, get_selected_elements,
    link_dwg_and_activate_view,
]


def get_revit_connection() -> RevitConnection:
    """
    获取或创建持久的Revit连接

    返回:
        RevitConnection: 与Revit的连接对象

    异常:
        Exception: 连接失败时抛出
    """
    global _connection, _enabled

    if _connection is not None:
        try:
            # 测试连接是否有效
            result = _connection.send_command("get_polyhaven_status")
            _enabled = result.get("enabled", False)
            return _connection
        except Exception as e:
            logger.warning(f"现有连接已失效: {str(e)}")
            try:
                _connection.disconnect()
            except:
                pass
            _connection = None

    # 创建新连接
    if _connection is None:
        _connection = RevitConnection(host="localhost", port=_port)
        if not _connection.connect():
            logger.error("无法连接到Revit")
            _connection = None
            raise Exception(
                "无法连接到Revit。请确保Revit插件正在运行。")
        logger.info("已创建新的持久连接到Revit")

    return _connection


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """
    管理服务器启动和关闭生命周期

    参数:
        server: FastMCP服务器实例
    """
    try:
        logger.info("RevitMCP服务器正在启动")
        try:
            get_revit_connection()
            logger.info("服务器启动时成功连接到Revit")
        except Exception as e:
            logger.warning(f"服务器启动时无法连接到Revit: {str(e)}")
            logger.warning(
                "在使用Revit资源或工具前，请确保Revit插件正在运行")

        yield {}
    finally:
        global _connection
        if _connection:
            logger.info("服务器关闭时断开与Revit的连接")
            _connection.disconnect()
            _connection = None
        logger.info("RevitMCP服务器已关闭")


# 创建带有生命周期支持的MCP服务器
mcp = FastMCP(
    "RevitMCP",
    description="通过模型上下文协议(MCP)集成Revit",
    lifespan=server_lifespan
)


# 注册工具函数
def register_tools(server: FastMCP) -> None:
    """注册所有工具到MCP服务器"""
    # 注册建筑工具
    for tool in ARCHITECTURAL_TOOLS:
        server.tool()(tool)

    # 注册MEP工具
    for tool in MEP_TOOLS:
        server.tool()(tool)

    # 注册通用工具
    for tool in GENERAL_TOOLS:
        server.tool()(tool)


def list_tools(self: FastMCP) -> list[MCPTool]:
    """
    列出所有注册到MCP服务器的工具，并按类别分组

    返回:
        dict: 分类的工具字典，包含名称、描述和参数信息
    """
    tools_info = {
        "architectural": [],
        "mep": [],
        "general": []
    }

    # 获取建筑工具信息
    for tool in ARCHITECTURAL_TOOLS:
        # 获取函数签名
        sig = inspect.signature(tool)
        params = []
        for param_name, param in sig.parameters.items():
            if param_name != 'ctx':  # 排除上下文参数
                param_info = {
                    "name": param_name,
                    "required": param.default == inspect.Parameter.empty,
                    "default": None if param.default == inspect.Parameter.empty else param.default
                }
                params.append(param_info)

        # 获取函数文档
        doc = inspect.getdoc(tool)
        description = doc.split('\n')[0] if doc else "无描述"

        tool_info = {
            "name": tool.__name__,
            "description": description,
            "full_doc": doc,
            "parameters": params
        }
        tools_info["architectural"].append(tool_info)

    # 获取MEP工具信息
    for tool in MEP_TOOLS:
        sig = inspect.signature(tool)
        params = []
        for param_name, param in sig.parameters.items():
            if param_name != 'ctx':
                param_info = {
                    "name": param_name,
                    "required": param.default == inspect.Parameter.empty,
                    "default": None if param.default == inspect.Parameter.empty else param.default
                }
                params.append(param_info)

        doc = inspect.getdoc(tool)
        description = doc.split('\n')[0] if doc else "无描述"

        tool_info = {
            "name": tool.__name__,
            "description": description,
            "full_doc": doc,
            "parameters": params
        }
        tools_info["mep"].append(tool_info)

    # 获取通用工具信息
    for tool in GENERAL_TOOLS:
        sig = inspect.signature(tool)
        params = []
        for param_name, param in sig.parameters.items():
            if param_name != 'ctx':
                param_info = {
                    "name": param_name,
                    "required": param.default == inspect.Parameter.empty,
                    "default": None if param.default == inspect.Parameter.empty else param.default
                }
                params.append(param_info)

        doc = inspect.getdoc(tool)
        description = doc.split('\n')[0] if doc else "无描述"

        tool_info = {
            "name": tool.__name__,
            "description": description,
            "full_doc": doc,
            "parameters": params
        }
        tools_info["general"].append(tool_info)

    # 添加所有工具的汇总列表
    all_tools = []
    all_tools.extend(tools_info["architectural"])
    all_tools.extend(tools_info["mep"])
    all_tools.extend(tools_info["general"])
    tools_info["all"] = all_tools

    logger.info(f"获取到 {len(all_tools)} 个工具函数")
    return tools_info


# 注册所有工具
register_tools(mcp)
mcp.list_tools = types.MethodType(list_tools, mcp)
mcp.prompt()(asset_creation_strategy)
mcp.list_prompts = types.MethodType(list_prompts, mcp)
mcp.resource("config://BuiltInCategory")(get_all_builtin_category)
mcp.resource("greeting://{name}")(get_greeting)
mcp.list_resource_templates = types.MethodType(list_resource_templates, mcp)
mcp.list_resources()

def main():
    """运行MCP服务器"""
    logger.info("启动RevitMCP服务器...")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"服务器运行时发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    main()
