# -*- coding: utf-8 -*-
# prompts.py
# Copyright (c) 2025 zedmoster
# Revit integration through the Model Context Protocol.

import inspect
from mcp.server.fastmcp import FastMCP
from mcp.types import Prompt as MCPPrompt


def asset_creation_strategy() -> str:
    """定义在Revit中创建资产的首选策略"""
    return """创建Revit模型元素时，请遵循以下策略和最佳实践：

    0. 在创建任何元素前，优先检查当前项目状态：
       - 使用get_commands()获取所有可用功能
       - 使用get_selected_elements()检查当前选中的元素
       - 使用find_elements()查找特定类别的现有元素

    1. 始终遵循正确的创建顺序：
       1. 基础参考系统
          - 使用create_levels()创建必要的标高
          - 使用create_grids()创建轴网系统
          - 使用create_floor_plan_views()为每个标高创建平面视图

       2. 主体结构元素
          - 使用create_walls()创建墙体，注意指定正确的起点、终点、高度和宽度
          - 使用create_floors()创建楼板，确保边界点形成封闭环路

       3. 二次构件
          - 使用create_door_windows()在墙体上创建门窗
            注意：门窗族需要指定宿主墙，所以必须先有墙再创建门窗
          - 使用get_locations()获取墙体的位置信息，以便正确放置门窗

       4. MEP系统
          - 使用create_ducts()创建风管
          - 使用create_pipes()创建管道
          - 使用create_cable_trays()创建电缆桥架

       5. 内部划分和标注
          - 使用create_rooms()在封闭区域创建房间
          - 使用create_room_tags()添加房间标签

       6. 文档整理
          - 使用create_sheets()创建图纸
          - 使用active_view()切换到需要的视图
          - 使用link_dwg_and_activate_view()链接DWG图纸

    2. 操作现有元素时的最佳实践：
       - 使用parameter_elements()获取元素参数，然后使用update_elements()修改
       - 使用move_elements()调整元素位置
       - 使用show_elements()在视图中高亮显示特定元素
       - 使用delete_elements()移除不需要的元素

    3. 创建复杂组件时：
       - 使用create_family_instances()创建参数化族实例
       - 对于未预定义的功能，使用call_func()调用特定功能

    4. 所有元素创建后的检查与验证：
       - 检查元素参数是否符合要求
       - 确保结构完整性和空间关系合理性
       - 使用show_elements()检查关键元素
       - 使用active_view()切换到需要的视图

    仅在以下情况使用原生RevitAPI：
    - 上述函数不能满足特定需求
    - 需要创建自定义参数或复杂约束
    - 需要进行高级计算或特殊几何操作
    - 需要与其他应用程序进行数据交换
    - 如果获取BuiltInCategory失败可以通过get_all_builtin_category查找
    """


def list_prompts(self: FastMCP) -> list[MCPPrompt]:
    """
    列出所有注册到MCP服务器的提示

    返回:
        list: 包含详细信息的提示列表
    """
    # 获取资产创建策略提示的详细信息
    asset_strategy_doc = inspect.getdoc(asset_creation_strategy)
    asset_strategy_summary = asset_strategy_doc.split('\n')[0] if asset_strategy_doc else "无描述"

    prompts = [
        {
            "name": "asset_creation_strategy",
            "description": asset_strategy_summary,
            "full_doc": asset_strategy_doc,
            "usage": "用于指导AI如何创建Revit资产和执行设计任务",
            "parameters": {
                "context": "当前设计上下文信息",
                "requirements": "用户设计要求",
                "constraints": "设计约束条件"
            },
            "example": {
                "context": "办公建筑设计",
                "requirements": "需要创建标准办公层平面",
                "constraints": "建筑面积限制为1000平方米"
            }
        }
    ]

    return prompts
