import socket
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s  ')
logger = logging.getLogger("RevitConnection")


@dataclass
class RevitConnection:
    host: str
    port: int
    sock: socket.socket = None

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
        sock.settimeout(15.0)

        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise Exception("Connection closed before receiving any data")
                        break

                    chunks.append(chunk)

                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        continue
                except socket.timeout:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise
        except socket.timeout:
            logger.warning("Socket timeout during chunked receive")
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise

        if chunks:
            data = b''.join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Revit and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Revit")

        try:
            logger.info(f"Sending command: {command_type} with params: {params}")

            from .rpc import JsonRPCRequest, JsonRPCResponse
            command = JsonRPCRequest(method=command_type, params=params)
            command_json = json.dumps(command.__dict__)

            self.sock.sendall(command_json.encode('utf-8'))
            logger.info("Command sent, waiting for response...")

            self.sock.settimeout(30)

            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")

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
            self.sock = None
            raise Exception("Timeout waiting for Revit response - try simplifying your request")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Revit lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Revit: {str(e)}")
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Revit: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Revit: {str(e)}")
            self.sock = None
            raise Exception(f"Communication error with Revit: {str(e)}")
