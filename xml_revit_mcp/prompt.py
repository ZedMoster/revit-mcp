from mcp.server import Server
import mcp.types as types

# Define available prompts
PROMPTS = {
    "create-walls": types.Prompt(
        name="create-walls",
        description="Create walls in Revit",
        arguments=[
            types.PromptArgument(
                name="startX",
                description="Wall start X coordinate (mm)",
                required=True
            ),
            types.PromptArgument(
                name="startY",
                description="Wall start Y coordinate (mm)",
                required=True
            ),
            types.PromptArgument(
                name="endX",
                description="Wall end X coordinate (mm)",
                required=True
            ),
            types.PromptArgument(
                name="endY",
                description="Wall end Y coordinate (mm)",
                required=True
            ),
            types.PromptArgument(
                name="height",
                description="Wall height (mm), must be positive",
                required=True
            ),
            types.PromptArgument(
                name="width",
                description="Wall width (mm), must be positive",
                required=True
            )
        ],
    ),
    "update-elements": types.Prompt(
        name="update-elements",
        description="Update Revit element parameters",
        arguments=[
            types.PromptArgument(
                name="elementId",
                description="Element ID to update",
                required=True
            ),
            types.PromptArgument(
                name="parameterName",
                description="Name of the parameter to update",
                required=True
            ),
            types.PromptArgument(
                name="parameterValue",
                description="New value for the parameter",
                required=True
            )
        ],
    )
}

# Initialize server
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
        params_str = "Parameter details:\n"
        if arguments:
            params_str += f"- Start Point: ({arguments.get('startX', '?')}, {arguments.get('startY', '?')})\n"
            params_str += f"- End Point: ({arguments.get('endX', '?')}, {arguments.get('endY', '?')})\n"
            params_str += f"- Height: {arguments.get('height', '?')} mm\n"
            params_str += f"- Width: {arguments.get('width', '?')} mm"

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Create wall with the following details:\n\n{params_str}"
                    )
                )
            ]
        )

    if name == "update-elements":
        params_str = "Update details:\n"
        if arguments:
            params_str += f"- Element ID: {arguments.get('elementId', '?')}\n"
            params_str += f"- Parameter Name: {arguments.get('parameterName', '?')}\n"
            params_str += f"- New Value: {arguments.get('parameterValue', '?')}"

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Update element parameter with the following details:\n\n{params_str}"
                    )
                )
            ]
        )

    raise ValueError("Prompt implementation not found")
