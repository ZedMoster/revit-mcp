from mcp.server import Server
import mcp.types as types

# 定义可用的提示
PROMPTS = {
    "create-walls": types.Prompt(
        name="create-walls",
        description="在 Revit 中创建墙体",
        arguments=[
            types.PromptArgument(
                name="startX",
                description="墙体起点 X 坐标（毫米）",
                required=True
            ),
            types.PromptArgument(
                name="startY",
                description="墙体起点 Y 坐标（毫米）",
                required=True
            ),
            types.PromptArgument(
                name="endX",
                description="墙体终点 X 坐标（毫米）",
                required=True
            ),
            types.PromptArgument(
                name="endY",
                description="墙体终点 Y 坐标（毫米）",
                required=True
            ),
            types.PromptArgument(
                name="height",
                description="墙体高度（毫米），必须为正数",
                required=True
            ),
            types.PromptArgument(
                name="width",
                description="墙体宽度（毫米），必须为正数",
                required=True
            )
        ],
    ),
    "update-elements": types.Prompt(
        name="update-elements",
        description="更新 Revit 元素的参数",
        arguments=[
            types.PromptArgument(
                name="elementId",
                description="要更新的元素 ID",
                required=True
            ),
            types.PromptArgument(
                name="parameterName",
                description="要更新的参数名称",
                required=True
            ),
            types.PromptArgument(
                name="parameterValue",
                description="参数的新值",
                required=True
            )
        ],
    )
}

# 初始化服务器
app = Server("revit-tools-server")

@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return list(PROMPTS.values())

@app.get_prompt()
async def get_prompt(
    name: str, arguments: dict[str, str] | None = None
) -> types.GetPromptResult:
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")

    if name == "create-walls":
        params_str = "参数详情：\n"
        if arguments:
            params_str += f"- 起点：({arguments.get('startX', '?')}, {arguments.get('startY', '?')})\n"
            params_str += f"- 终点：({arguments.get('endX', '?')}, {arguments.get('endY', '?')})\n"
            params_str += f"- 高度：{arguments.get('height', '?')} mm\n"
            params_str += f"- 宽度：{arguments.get('width', '?')} mm"

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"创建墙体，具体参数如下：\n\n{params_str}"
                    )
                )
            ]
        )

    if name == "update-elements":
        params_str = "更新详情：\n"
        if arguments:
            params_str += f"- 元素 ID：{arguments.get('elementId', '?')}\n"
            params_str += f"- 参数名称：{arguments.get('parameterName', '?')}\n"
            params_str += f"- 新值：{arguments.get('parameterValue', '?')}"

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"更新元素参数：\n\n{params_str}"
                    )
                )
            ]
        )

    raise ValueError("Prompt implementation not found")
