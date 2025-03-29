# prompt.py
# Copyright (c) 2025 zedmoster

import mcp.types as types

PROMPTS = {
    "CallFunc": types.Prompt(
        name="CallFunc",
        description="Call a function asynchronously based on the given parameters.",
        arguments=[
            types.PromptArgument(
                name="func",
                description=(
                    "The name of the function to call. Supported functions: 'ClearDuplicates'. "
                    "Use 'ClearDuplicates' to remove duplicate elements at the same location, "
                    "preventing them from being counted multiple times in schedules. This function "
                    "is useful when instances of the same family are unintentionally placed on top "
                    "of each other."
                ),
                required=True
            ),
        ],
    ),

    "FindElements": types.Prompt(
        name="FindElements",
        description="Find elements in the Revit scene",
        arguments=[
            types.PromptArgument(
                name="categoryName",
                description="Category name to search categoryName. must be provided.",
                required=True
            ),
            types.PromptArgument(
                name="categoryId",
                description="Category ID to search (optional) ",
            ),
            types.PromptArgument(
                name="isInstance",
                description="Whether to search for instances or types (optional)",
                required=False
            )
        ],
    ),
    "UpdateElements": types.Prompt(
        name="UpdateElements",
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
    ),
    "DeleteElements": types.Prompt(
        name="DeleteElements",
        description="Delete elements from Revit",
        arguments=[
            types.PromptArgument(
                name="elementId",
                description="Element ID to delete",
                required=True
            )
        ],
    ),
    "ShowElements": types.Prompt(
        name="ShowElements",
        description="Show elements in Revit",
        arguments=[
            types.PromptArgument(
                name="elementId",
                description="Element ID to show",
                required=True
            )
        ],
    ),

    "CreateLevels": types.Prompt(
        name="CreateLevels",
        description="Create levels in Revit.",
        arguments=[
            types.PromptArgument(
                name="name",
                description="The name of the level.",
                required=True
            ),
            types.PromptArgument(
                name="elevation",
                description="The elevation of the level in mm. This parameter is required.",
                required=True
            ),
        ],
    ),
    "CreateGrids": types.Prompt(
        name="CreateGrids",
        description="Create grids in Revit. Supports both linear and arc grids.",
        arguments=[
            types.PromptArgument(
                name="name",
                description="The name of the grid.",
                required=True
            ),
            types.PromptArgument(
                name="startX",
                description="Start X coordinate for the grid (mm).",
                required=True
            ),
            types.PromptArgument(
                name="startY",
                description="Start Y coordinate for the grid (mm).",
                required=True
            ),
            types.PromptArgument(
                name="endX",
                description="End X coordinate for the grid (mm).",
                required=True
            ),
            types.PromptArgument(
                name="endY",
                description="End Y coordinate for the grid (mm).",
                required=True
            ),
            types.PromptArgument(
                name="centerX",
                description="Center X coordinate for arc grids (mm). "
                            "This parameter is optional, required only for arc grids.",
            ),
            types.PromptArgument(
                name="centerY",
                description="Center Y coordinate for arc grids (mm). "
                            "This parameter is optional, required only for arc grids.",
            ),
        ],
    ),

    "CreateWalls": types.Prompt(
        name="CreateWalls",
        description="Create walls in Revit.",
        arguments=[
            types.PromptArgument(
                name="startX",
                description="Wall start X coordinate (mm).",
                required=True
            ),
            types.PromptArgument(
                name="startY",
                description="Wall start Y coordinate (mm).",
                required=True
            ),
            types.PromptArgument(
                name="endX",
                description="Wall end X coordinate (mm).",
                required=True
            ),
            types.PromptArgument(
                name="endY",
                description="Wall end Y coordinate (mm).",
                required=True
            ),
            types.PromptArgument(
                name="height",
                description="Wall height (mm), must be positive.",
                required=True
            ),
            types.PromptArgument(
                name="width",
                description="Wall width (mm), must be positive.",
                required=True
            ),
            types.PromptArgument(
                name="elevation",
                description="Wall level elevation (mm). This parameter is optional."
            ),
        ],
    ),

    "CreateFloors": types.Prompt(
        name="CreateFloors",
        description="Create a floor in Revit using specified boundary points and floor type.",
        arguments=[
            types.PromptArgument(
                name="boundaryPoints",
                description="A list of dictionaries representing XYZ points (x, y, z) for the floor boundary.",
                required=True
            ),
            types.PromptArgument(
                name="floorTypeName",
                description="The name of the floor type to be used for creating the floor. This parameter is optional.",
                required=False
            ),
            types.PromptArgument(
                name="structural",
                description="Whether the floor is a structural floor. "
                            "True if structural, False otherwise. Default is False.",
                required=False,
                default=False
            ),
        ]
    ),

    "CreateFamilyInstances": types.Prompt(
        name="CreateFamilyInstances",
        description="Create a family instances in Revit.",
        arguments=[
            types.PromptArgument(
                name="categoryName",
                description="Category name of the family (e.g., Windows, Doors, etc.).",
                required=True
            ),
            types.PromptArgument(
                name="startX",
                description="Start X coordinate (mm) for placing the family instance.",
                required=True
            ),
            types.PromptArgument(
                name="startY",
                description="Start Y coordinate (mm) for placing the family instance.",
                required=True
            ),
            types.PromptArgument(
                name="startZ",
                description="Start Z coordinate (mm) for placing the family instance.",
                required=True
            ),
            types.PromptArgument(
                name="name",
                description="Family symbol name (e.g., 500x500, 600x600, etc.).",
                required=True
            ),
            types.PromptArgument(
                name="familyName",
                description="Family name (e.g., Steel, Concrete, etc.). This parameter is optional."
            ),
            types.PromptArgument(
                name="endX",
                description="End X coordinate (mm) for placing the family instance (optional).",
            ),
            types.PromptArgument(
                name="endY",
                description="End Y coordinate (mm) for placing the family instance (optional).",
            ),
            types.PromptArgument(
                name="endZ",
                description="End Z coordinate (mm) for placing the family instance (optional).",
            ),
            types.PromptArgument(
                name="hostId",
                description="Element ID of the host (e.g., wall, floor, etc.) for the family instance to be hosted on."
            ),
            types.PromptArgument(
                name="viewName",
                description="View name where the family instance will be placed (e.g., 3D_view, Floor_plan_view)."
            ),
            types.PromptArgument(
                name="rotationAngle",
                description="Rotation angle (degrees) for the family instance, if applicable.",
            ),
            types.PromptArgument(
                name="offset",
                description="Offset distance (mm) from the host or base level, if applicable."
            ),
        ]
    ),

}


async def list_prompts_response() -> list[types.Prompt]:
    """
    Retrieve a list of all available prompts.
    The language for the response message.

    Returns:
    - list[types.Prompt]: List of prompt definitions.
    """
    return list(PROMPTS.values())


async def get_prompt_response(method: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
    """
    Generate a response for a given method with provided arguments.
    The language for the response message.

    Parameters:
    - method (str): The name of the prompt method to execute.
    - arguments (dict[str, str] | None): Optional. Dictionary containing argument names and values.

    Returns:
    - types.GetPromptResult: A formatted response object containing execution details.

    Raises:
    - ValueError: If the provided method is not found in PROMPTS.
    """
    if method not in PROMPTS:
        available_prompts = ', '.join(PROMPTS.keys())
        raise ValueError(f"Invalid method: '{method}'. Available prompts: {available_prompts}")

    # Format parameters for display if provided
    params_str = "\n".join(f"- {key}: {value}" for key, value in (arguments or {}).items())

    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"The language for the response message.Executing '{method}' with the following details:\n\n{params_str or 'No parameters provided.'}"
                )
            )
        ]
    )
