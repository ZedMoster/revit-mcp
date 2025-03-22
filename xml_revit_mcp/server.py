import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
import mcp.types as types

from .revit_connection import RevitConnection
from .tools import create_walls, update_elements, asset_creation_strategy
from .prompt import *

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RevitMCPServer")

# Global connection for resources
_Revit_connection = None
_polyhaven_enabled = False
_port = 8080


def get_Revit_connection():
    """Get or create a persistent Revit connection"""
    global _Revit_connection, _polyhaven_enabled

    if _Revit_connection is not None:
        try:
            result = _Revit_connection.send_command("get_polyhaven_status")
            _polyhaven_enabled = result.get("enabled", False)
            return _Revit_connection
        except Exception as e:
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _Revit_connection.disconnect()
            except:
                pass
            _Revit_connection = None

    if _Revit_connection is None:
        _Revit_connection = RevitConnection(host="localhost", port=_port)
        if not _Revit_connection.connect():
            logger.error("Failed to connect to Revit")
            _Revit_connection = None
            raise Exception(
                "Could not connect to Revit. Make sure the Revit addon is running.")
        logger.info("Created new persistent connection to Revit")

    return _Revit_connection


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    try:
        logger.info("RevitMCP server starting up")
        try:
            Revit = get_Revit_connection()
            logger.info("Successfully connected to Revit on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Revit on startup: {str(e)}")
            logger.warning(
                "Make sure the Revit addon is running before using Revit resources or tools")

        yield {}
    finally:
        global _Revit_connection
        if _Revit_connection:
            logger.info("Disconnecting from Revit on shutdown")
            _Revit_connection.disconnect()
            _Revit_connection = None
        logger.info("RevitMCP server shut down")


# Create the MCP server with lifespan support
mcp = FastMCP(
    "RevitMCP",
    description="Revit integration through the Model Context Protocol",
    lifespan=server_lifespan
)


async def list_prompts() -> list[types.Prompt]:
    """List available prompts"""
    return get_available_prompts()


async def get_prompt(name: str, arguments: Dict[str, Any] = None) -> types.GetPromptResult:
    """Get prompt details"""
    return get_prompt_response(name, arguments)


# Register prompts
mcp.list_prompts_handler = list_prompts
mcp.get_prompt_handler = get_prompt

# Register tools
mcp.tool()(create_walls)
mcp.tool()(update_elements)


def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
