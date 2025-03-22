import logging
from typing import List, Dict
from mcp.server.fastmcp import Context

logger = logging.getLogger("RevitTools")


def create_walls(
        ctx: Context,
        method: str = "CreateWalls",
        params: List[dict[str, int]] = None,
) -> str:
    """
    Create a new object in the Revit scene.

    Parameters:
    - method: (str) Object type (e.g., "CreateWalls").
    - params: (List[dict]) List of dictionaries containing wall parameters. Each dictionary should include:
        - startX (int or float): X-coordinate of the wall's start point.
        - startY (int or float): Y-coordinate of the wall's start point.
        - endX (int or float): X-coordinate of the wall's end point.
        - endY (int or float): Y-coordinate of the wall's end point.
        - height (int or float): Height of the wall (must be positive).
        - width (int or float): Width of the wall (must be positive).

    Returns:
    str: A message indicating the created object's ElementId or an error message.
    """
    try:
        if not isinstance(params, list) or not all(isinstance(param, dict) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries with wall parameters.")

        required_keys = {"startX", "startY", "endX", "endY", "height", "width"}
        for i, param in enumerate(params):
            missing_keys = required_keys - param.keys()
            if missing_keys:
                raise ValueError(
                    f"Missing keys in parameter {i + 1}: {', '.join(missing_keys)}. Please provide all required keys: {', '.join(required_keys)}.")

            for key in required_keys:
                if not isinstance(param[key], (int, float)):
                    raise ValueError(
                        f"Invalid data type for '{key}' in parameter {i + 1}: Expected int or float, but got {type(param[key])}.")

                if key in {"height", "width"} and param[key] <= 0:
                    raise ValueError(
                        f"Invalid value for '{key}' in parameter {i + 1}: Must be a positive number. Received: {param[key]}.")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully created object(s). Result: {result}"

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)} | Method: {method}, Params: {params}")
        return f"Validation error: {str(ve)}"

    except Exception as e:
        logger.error(f"Unexpected error while creating objects. Method: {method}, Params: {params}, Error: {str(e)}",
                     exc_info=True)
        return f"Error: An unexpected issue occurred. {str(e)}"


def update_elements(ctx: Context, method: str = "UpdateElements", params: list[dict[str, str]] = None) -> str:
    """
    Update parameters of elements in Revit.

    Parameters:
    - method: (str) The method name for the update (e.g., "UpdateElements").
    - params: (list) List of dictionaries containing element parameters to be updated. Each dictionary should include:
        - elementId (int or str): ID of the element.
        - parameterName (str): The name of the parameter to be updated.
        - parameterValue (str): The new value for the parameter.

    Returns:
    str: A message indicating the result of the update.
    """
    try:
        if not isinstance(params, list) or not all(isinstance(param, dict) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries with element parameters.")

        required_keys = {"elementId", "parameterName", "parameterValue"}
        for i, param in enumerate(params):
            missing_keys = required_keys - param.keys()
            if missing_keys:
                raise ValueError(
                    f"Missing keys in parameter {i + 1}: {', '.join(missing_keys)}. Please provide all required keys: {', '.join(required_keys)}."
                )

            for key in required_keys:
                if not isinstance(param[key], (int, str)):
                    raise ValueError(
                        f"Invalid data type for '{key}' in parameter {i + 1}: Expected int or str, but got {type(param[key])}."
                    )

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully updated element(s). Result: {result}"

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)} | Method: {method}, Params: {params}")
        return f"Validation error: {str(ve)}"

    except Exception as e:
        logger.error(f"Unexpected error while updating elements. Method: {method}, Params: {params}, Error: {str(e)}",
                     exc_info=True)
        return f"Error: An unexpected issue occurred. {str(e)}"


def asset_creation_strategy() -> str:
    """Defines the preferred strategy for creating walls in Revit"""
    return """When creating walls in Revit using create_object(), follow these guidelines:

    1. Ensure the scene is properly initialized using get_scene_info().
    2. Use create_object() with appropriate parameters for wall creation.
       - Provide startX, startY, endX, endY, height, and width values.
    3. Verify the created walls using get_object_info().
    4. If necessary, adjust wall dimensions or position using modify_object().
    5. Always check for errors in the response from create_object() to ensure walls are created successfully.

    Example:
    ```python
    create_object(ctx, method="CreateWalls", params=[
        {"startX": 0, "startY": 0, "endX": 12000, "endY": 0, "height": 3000, "width": 200}
    ])
    ```
    """


from mcp.server import Server
import mcp.types as types

# Define available prompts
PROMPTS = {
    "create-walls": types.Prompt(
        name="create-walls",
        description="Create walls in Revit using specified parameters",
        arguments=[
            types.PromptArgument(
                name="params",
                description="List of dictionaries containing wall parameters (startX, startY, endX, endY, height, width)",
                required=True
            )
        ],
    ),
    "update-elements": types.Prompt(
        name="update-elements",
        description="Update element parameters in Revit",
        arguments=[
            types.PromptArgument(
                name="params",
                description="List of dictionaries containing element parameters (elementId, parameterName, parameterValue)",
                required=True
            )
        ],
    ),
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
        params = arguments.get("params") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Create walls in Revit with the following parameters:\n\n{params}"
                    )
                )
            ]
        )

    if name == "update-elements":
        params = arguments.get("params") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Update the following elements in Revit:\n\n{params}"
                    )
                )
            ]
        )

    raise ValueError("Prompt implementation not found")
