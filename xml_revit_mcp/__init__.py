"""Revit integration through the Model Context Protocol."""

__name__ = "xml_revit_mcp"
__author__ = "zedmoster"
__version__ = "0.1.0"

from .server import mcp, main
from .tools import create_walls, update_elements
from .revit_connection import RevitConnection
from .rpc import JsonRPCRequest, JsonRPCResponse, JsonRPCError, JsonRPCErrorCodes

__all__ = [
    'mcp',
    'main',
    'RevitConnection',
    'JsonRPCRequest',
    'JsonRPCResponse',
    'JsonRPCError',
    'JsonRPCErrorCodes',
    'create_walls',
    'update_elements',
]
