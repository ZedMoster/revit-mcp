# -*- coding: utf-8 -*-
# rpc.py
# Copyright (c) 2025 zedmoster

from dataclasses import dataclass
from typing import Dict, Any, Optional


class JsonRPCRequest:
    def __init__(self, method, params, id="2.0"):
        self.jsonrpc = "2.0"
        self.id = id
        self.method = method
        self.params = params

    def is_valid(self):
        return bool(self.id and self.method)


class JsonRPCResponse:
    def __init__(self, id, result=None, error=None):
        self.jsonrpc = "2.0"
        self.id = id
        self.result = result
        self.error = error if error else []


class JsonRPCError:
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data


class JsonRPCErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass
class JsonRPCRequest:
    """JSON-RPC request object"""
    method: str
    params: Optional[Dict[str, Any]] = None
    id: int = 1
    jsonrpc: str = "2.0"


@dataclass
class JsonRPCResponse:
    """JSON-RPC response object"""
    id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"
