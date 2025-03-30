# -*- coding: utf-8 -*-
# server.py
# Copyright (c) 2025 zedmoster

from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from .revit_connection import RevitConnection
from .tools import *
import logging

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
_Revit_connection: Optional[RevitConnection] = None
_polyhaven_enabled: bool = False
_port: int = 8080

# 工具分类
ARCHITECTURAL_TOOLS = [
    create_levels, create_grids, create_walls, create_floors,
    create_door_windows, create_rooms, create_room_tags
]

MEP_TOOLS = [
    create_ducts, create_pipes, create_cable_trays
]

GENERAL_TOOLS = [
    create_family_instances, find_elements, update_elements,
    delete_elements, parameter_elements, get_location,
    show_elements, active_view, call_func
]


def get_Revit_connection() -> RevitConnection:
    """
    获取或创建持久的Revit连接

    返回:
        RevitConnection: 与Revit的连接对象

    异常:
        Exception: 连接失败时抛出
    """
    global _Revit_connection, _polyhaven_enabled

    if _Revit_connection is not None:
        try:
            # 测试连接是否有效
            result = _Revit_connection.send_command("get_polyhaven_status")
            _polyhaven_enabled = result.get("enabled", False)
            return _Revit_connection
        except Exception as e:
            logger.warning(f"现有连接已失效: {str(e)}")
            try:
                _Revit_connection.disconnect()
            except:
                pass
            _Revit_connection = None

    # 创建新连接
    if _Revit_connection is None:
        _Revit_connection = RevitConnection(host="localhost", port=_port)
        if not _Revit_connection.connect():
            logger.error("无法连接到Revit")
            _Revit_connection = None
            raise Exception(
                "无法连接到Revit。请确保Revit插件正在运行。")
        logger.info("已创建新的持久连接到Revit")

    return _Revit_connection


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
            Revit = get_Revit_connection()
            logger.info("服务器启动时成功连接到Revit")
        except Exception as e:
            logger.warning(f"服务器启动时无法连接到Revit: {str(e)}")
            logger.warning(
                "在使用Revit资源或工具前，请确保Revit插件正在运行")

        yield {}
    finally:
        global _Revit_connection
        if _Revit_connection:
            logger.info("服务器关闭时断开与Revit的连接")
            _Revit_connection.disconnect()
            _Revit_connection = None
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


# 注册所有工具
register_tools(mcp)


@mcp.prompt()
def asset_creation_strategy() -> str:
    """
    基于现有工具集定义Revit资源(图元、族等)创建和管理的优化策略

    返回:
        str: 包含以下内容的综合策略文档:
            - 图元创建最佳实践
            - 性能优化技术
            - 错误处理方法
            - 批处理建议
            - 资源管理

    策略要点:
        1. 批处理:
           - 利用API工具的批量创建功能
           - 分组相似操作以减少事务
           - 使用已验证参数模式确保一致性

        2. 错误处理:
           - 失败操作的事务回滚
           - 使用标准JSON-RPC错误响应格式
           - 包含详细日志记录

        3. 性能优化:
           - 通过批处理减少Revit API调用
           - 使用字符串格式的元素ID
           - 缓存常用元素引用

        4. 创建工作流:
           - 遵循层级创建顺序(标高→轴网→墙→楼板→门窗→族实例)
           - 放置依赖图元前验证宿主存在
           - 使用毫米单位确保一致性

        5. 资源管理:
           - 尽可能重用元素
           - 批量操作使用轻量级表示
           - 操作后清理临时元素

        6. 类型选择逻辑:
           - 在创建前检查是否提供了CategoryName和Name参数
           - 如果未提供，使用find_elements查询对应类别下的所有类型
           - 返回类型列表供用户选择
           - 确认选择后再执行创建逻辑
           - 确保创建的类型在项目中存在
    """

    strategy = """
    # Revit资源创建综合策略

    ## I. 图元创建原则
    1. **层级优先**: 先创建宿主元素再创建依赖元素
    2. **批处理**: 尽可能使用批量操作
    3. **验证**: API调用前验证参数
    4. **事务管理**: 分组相关操作

    ## II. 性能优化
    1. **最小化视图切换**: 使用元素ID而非激活视图
    2. **缓存引用**: 存储常用元素集合
    3. **延迟加载**: 仅当需要时查询元素详情
    4. **批量处理**: 使用工具中的批量创建函数

    ## III. 错误处理
    1. **标准化错误**: 使用标准JSON-RPC错误代码
    2. **事务回滚**: 实现事务回滚点
    3. **详细日志**: 包含元素引用的详细日志
    4. **参数验证**: 执行前验证参数

    ## IV. 类型选择逻辑(必须严格执行的逻辑,不然一些Name项目中不存在一定不会运行成功)
    1. **参数检查**: 在执行创建操作前，检查CategoryName和Name参数是否存在。
    2. **类型查找**: 如果未提供参数，使用find_elements函数查找对应类别下的所有类型。
    3. **用户选择**: 将查找到的类型以列表形式返回，让用户进行选择。
    4. **确认执行**: 用户选择后，验证类型的有效性，并确保项目中存在。
    5. **执行创建**: 使用用户确认的类型进行创建操作。

    ## V. 推荐工作流

    ### 1. 建筑工作流
    - 标高(create_levels) → 轴网(create_grids) → 墙(create_walls) → 楼板(create_floors) → 
      门窗(create_door_windows) → 其他族实例(create_family_instances)

    ### 2. 标注工作流
    - 创建房间(create_rooms) → 添加标签(create_room_tags)

    ### 3. 创建族工作流
    - 查找族类型(find_elements) → 创建族实例(create_family_instances)

    ### 4. MEP工作流
    - 标高(create_levels) → 墙(create_walls) → 风管(create_ducts) → 管道(create_pipes) → 设备(create_family_instances)

    ### 5. 电气工作流
    - 标高(create_levels) → 墙(create_walls) → 电缆桥架(create_cable_trays) → 电气设备(create_family_instances)

    ## VI. 最佳实践

    ### 1. 工具使用
    - **创建类**: create_levels/create_grids/create_walls/create_door_windows等
    - **查询类**: find_elements/parameter_elements
    - **修改类**: update_elements
    - **删除类**: delete_elements

    ### 2. 参数验证
    - 使用字典列表格式参数(确保参数中不要包含注释内容)
    - 元素ID统一转为字符串
    - 坐标单位使用毫米

    ### 3. 元素管理
    - 创建后使用show_elements验证
    - 使用get_location获取定位信息
    - 批量更新使用update_elements

    ## VII. 实施说明
    - 所有坐标参数必须使用毫米单位
    - 元素ID优先使用字符串格式
    - 放置族实例前用find_elements验证宿主存在
    - 相关操作使用同一事务组
    - 使用active_view管理视图切换
    - 门窗族实例创建使用专用create_door_windows函数
    - MEP元素使用专用的create_ducts/create_pipes/create_cable_trays函数
    """

    return strategy


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
