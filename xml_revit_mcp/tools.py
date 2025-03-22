import logging
from typing import List
from mcp.server.fastmcp import Context

logger = logging.getLogger("RevitTools")


def find_elements(ctx: Context, method: str = "FindElements", params: List[dict[str, object]] = None) -> List[int]:
    """
    Find elements in the Revit scene based on categoryId or categoryName.
    * At least one of categoryId or categoryName must be provided.

    :param ctx: The current context from FastMCP to manage Revit operations.
    :param method: The method name for finding elements. Default is "FindElements".
    :param params: A list of dictionaries containing search parameters with keys:
      - categoryId (int, optional): The ID of the category to search.
      - categoryName (str, optional): The name of the category to search.
      - isInstance (bool, optional): Whether to search for instances or types.
    :return: A list of element IDs matching the search criteria.
    """
    try:
        if not isinstance(params, list) or not all(isinstance(param, dict) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries.")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return result

    except Exception as e:
        logger.error(f"Error finding elements. {str(e)}", exc_info=True)
        return []


def create_walls(
        ctx: Context,
        method: str = "CreateWalls",
        params: List[dict[str, int]] = None,
) -> str:
    """
    Create new objects in the Revit scene.

    :param ctx: The current context from FastMCP.
    :param method: The method name for creating elements. Default is "CreateElements".
    :param params: A list of dictionaries containing parameters for creating elements with keys:
      - startX (int or float): X-coordinate of the wall's start point.
      - startY (int or float): Y-coordinate of the wall's start point.
      - endX (int or float): X-coordinate of the wall's end point.
      - endY (int or float): Y-coordinate of the wall's end point.
      - height (int or float): Height of the wall (must be positive).
      - width (int or float): Width of the wall (must be positive).
    :return: Result message indicating success or error.
    """
    try:
        if not isinstance(params, list) or not all(isinstance(param, dict) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries.")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully created object(s). Result: {result}"

    except Exception as e:
        logger.error(f"Error creating objects. {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


def update_elements(ctx: Context, method: str = "UpdateElements", params: list[dict[str, str]] = None) -> str:
    """
    Update parameters of elements in Revit.

    :param ctx: The current context from FastMCP.
    :param method: The method name for updating elements. Default is "UpdateElements".
    :param params: A list of dictionaries containing element update data with keys:
      - elementId (int or str): The ID of the element to be updated.
      - parameterName (str): The name of the parameter to be updated.
      - parameterValue (str): The new value for the parameter.
    :return: Result message indicating success or error.
    """
    try:
        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully updated element(s). Result: {result}"

    except Exception as e:
        logger.error(f"Error updating elements. {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


def delete_elements(ctx: Context, method: str = "DeleteElements", params: List[dict[str, str]] = None) -> str:
    """
    Delete elements in Revit by their IDs.

    :param ctx: The current context from FastMCP.
    :param method: The method name for deleting elements. Default is "DeleteElements".
    :param params: A list of element IDs to be deleted with keys:
      - elementId (int or str): The ID of the element to be deleted.
    :return: Result message indicating success or error.
    """
    try:
        if not params or not all(isinstance(el_id, int) for el_id in params):
            raise ValueError("Invalid input: 'params' should be a list of element IDs (int).")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully deleted element(s). Result: {result}"

    except Exception as e:
        logger.error(f"Error deleting elements. {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


def show_elements(ctx: Context, method: str = "ShowElements", params: List[dict[str, str]] = None) -> str:
    """
    Show elements in Revit by their IDs.

    :param ctx: The current context from FastMCP.
    :param method: The method name for showing elements. Default is "ShowElements".
    :param params: A list of dictionaries containing element IDs with keys:
      - elementId (int or str): The ID of the element to be shown.
    :return: Result message indicating success or error.
    """
    try:
        if not params or not all(isinstance(param.get("elementId"), (int, str)) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries with 'elementId' (int or str).")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully shown element(s). Result: {result}"

    except Exception as e:
        logger.error(f"Error showing elements. {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

