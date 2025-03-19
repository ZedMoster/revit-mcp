# revit_mcp_server.py
from mcp.server.fastmcp import FastMCP, Context
import socket
import json
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s  ')
logger = logging.getLogger("RevitMCPServer")

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
        self.error = error

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
class RevitConnection:
    host: str
    port: int
    sock: socket.socket = None  # Changed from 'socket' to 'sock' to avoid naming conflict

    def connect(self) -> bool:
        """Connect to the Revit addon socket server"""
        if self.sock:
            return True

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Revit at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Revit: {str(e)}")
            self.sock = None
            return False

    def disconnect(self):
        """Disconnect from the Revit addon"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Revit: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        # Use a consistent timeout value that matches the addon's timeout
        sock.settimeout(15.0)  # Match the addon's timeout

        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        # If we get an empty chunk, the connection might be closed
                        if not chunks:  # If we haven't received anything yet, this is an error
                            raise Exception(
                                "Connection closed before receiving any data")
                        break

                    chunks.append(chunk)

                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        # If we get here, it parsed successfully
                        logger.info(
                            f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    # If we hit a timeout during receiving, break the loop and try to use what we have
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(
                        f"Socket connection error during receive: {str(e)}")
                    raise  # Re-raise to be handled by the caller
        except socket.timeout:
            logger.warning("Socket timeout during chunked receive")
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise

        # If we get here, we either timed out or broke out of the loop
        # Try to use what we have
        if chunks:
            data = b''.join(chunks)
            logger.info(
                f"Returning data after receive completion ({len(data)} bytes)")
            try:
                # Try to parse what we have
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                # If we can't parse it, it's incomplete
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Revit and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Revit")

        try:
            # Log the command being sent
            logger.info(f"Sending command: {command_type} with params: {params}")

            # Create the JSON-RPC request
            command = JsonRPCRequest(method=command_type, params=params)
            command_json = json.dumps(command.__dict__)

            # Send the command
            self.sock.sendall(command_json.encode('utf-8'))
            logger.info("Command sent, waiting for response...")

            # Set a timeout for receiving - use the same timeout as in receive_full_response
            self.sock.settimeout(30)  # Match the addon's timeout

            # Receive the response using the improved receive_full_response method
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")

            # Parse the response
            response_dict = json.loads(response_data.decode('utf-8'))
            response = JsonRPCResponse(
                id=response_dict.get("id"),
                result=response_dict.get("result"),
                error=response_dict.get("error")
            )

            logger.info(f"Response parsed, error: {response.error}")

            if response.error:
                logger.error(f"Revit error: {response.error.get('message')}")
                raise Exception(response.error.get("message", "Unknown error from Revit"))

            return response.result or {}
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Revit")
            # Don't try to reconnect here - let the get_Revit_connection handle reconnection
            # Just invalidate the current socket so it will be recreated next time
            self.sock = None
            raise Exception("Timeout waiting for Revit response - try simplifying your request")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Revit lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Revit: {str(e)}")
            # Try to log what was received
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Revit: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Revit: {str(e)}")
            # Don't try to reconnect here - let the get_Revit_connection handle reconnection
            self.sock = None
            raise Exception(f"Communication error with Revit: {str(e)}")


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    try:
        # Just log that we're starting up
        logger.info("RevitMCP server starting up")
        # Try to connect to Revit on startup to verify it's available
        try:
            # This will initialize the global connection if needed
            Revit = get_Revit_connection()
            logger.info("Successfully connected to Revit on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Revit on startup: {str(e)}")
            logger.warning(
                "Make sure the Revit addon is running before using Revit resources or tools")

        # Return an empty context - we're using the global connection
        yield {}
    finally:
        # Clean up the global connection on shutdown
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

# Global connection for resources (since resources can't access context)
_Revit_connection = None
_polyhaven_enabled = False  # Add this global variable


def get_Revit_connection():
    """Get or create a persistent Revit connection"""
    global _Revit_connection, _polyhaven_enabled  # Add _polyhaven_enabled to globals

    # If we have an existing connection, check if it's still valid
    if _Revit_connection is not None:
        try:
            # First check if PolyHaven is enabled by sending a ping command
            result = _Revit_connection.send_command("get_polyhaven_status")
            # Store the PolyHaven status globally
            _polyhaven_enabled = result.get("enabled", False)
            return _Revit_connection
        except Exception as e:
            # Connection is dead, close it and create a new one
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _Revit_connection.disconnect()
            except:
                pass
            _Revit_connection = None

    # Create a new connection if needed
    if _Revit_connection is None:
        _Revit_connection = RevitConnection(host="localhost", port=8080)
        if not _Revit_connection.connect():
            logger.error("Failed to connect to Revit")
            _Revit_connection = None
            raise Exception(
                "Could not connect to Revit. Make sure the Revit addon is running.")
        logger.info("Created new persistent connection to Revit")

    return _Revit_connection

@mcp.tool()
def create_object(
    ctx: Context,
    method: str = "CreateWalls",
    params: List[dict[str, int]] = None,
) -> str:
    """
    Create a new object in the Revit scene.

    Parameters:
    - method: Object type (e.g., "CreateWalls").
    - params: List of dictionaries containing wall parameters. Each dictionary should include:
        - startX: X-coordinate of the wall's start point.
        - startY: Y-coordinate of the wall's start point.
        - endX: X-coordinate of the wall's end point.
        - endY: Y-coordinate of the wall's end point.
        - height: Height of the wall.
        - width: Width of the wall.

    Returns:
    A message indicating the created object's ElementId.
    """
    try:
        # Validate parameters
        if not all(isinstance(param, dict) for param in params):
            raise ValueError("Invalid parameter format. Expected a list of dictionaries.")

        # Get the global connection
        Revit = get_Revit_connection()

        result = Revit.send_command(method, params)
        return f"Created result: {result}"

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return f"Validation error: {str(ve)}"

    except Exception as e:
        logger.error(f"Error creating object: {str(e)}")
        return f"Error creating object: {str(e)}"


@mcp.prompt()
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


def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
