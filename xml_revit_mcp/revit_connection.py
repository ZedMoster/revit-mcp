# -*- coding: utf-8 -*-
# revit_connection.py
# Copyright (c) 2025 zedmoster
# Revit integration through the Model Context Protocol.

import socket
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union, List, Tuple

# 创建日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

# 创建日志器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 防止日志重复输出
if not logger.handlers:
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.propagate = False


@dataclass
class RevitConnection:
    """
    与Revit插件的Socket连接管理类

    负责建立、维护和关闭与Revit插件的TCP连接，
    以及发送命令和接收响应。
    """
    host: str
    port: int
    sock: Optional[socket.socket] = None
    timeout: float = 30.0
    buffer_size: int = 8192
    retry_attempts: int = 3
    retry_delay: float = 1.0

    def connect(self) -> bool:
        """
        连接到Revit插件的Socket服务器

        返回:
            bool: 连接成功返回True，否则返回False
        """
        if self.sock:
            return True

        for attempt in range(self.retry_attempts):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.timeout)
                self.sock.connect((self.host, self.port))
                logger.info(f"已连接到Revit ({self.host}:{self.port})")
                return True
            except socket.timeout:
                logger.warning(f"连接Revit超时 (尝试 {attempt + 1}/{self.retry_attempts})")
            except ConnectionRefusedError:
                logger.warning(f"Revit拒绝连接 (尝试 {attempt + 1}/{self.retry_attempts})")
            except Exception as e:
                logger.error(f"连接Revit失败: {str(e)} (尝试 {attempt + 1}/{self.retry_attempts})")

            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
                self.sock = None

            if attempt < self.retry_attempts - 1:
                time.sleep(self.retry_delay)

        return False

    def disconnect(self) -> None:
        """
        断开与Revit插件的连接
        """
        if self.sock:
            try:
                self.sock.close()
                logger.info("已断开与Revit的连接")
            except Exception as e:
                logger.error(f"断开Revit连接时出错: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self) -> bytes:
        """
        接收完整的响应，可能分多个数据块

        返回:
            bytes: 完整的响应数据

        异常:
            ConnectionError: 连接错误
            TimeoutError: 接收超时
            ValueError: 响应数据无效
        """
        if not self.sock:
            raise ConnectionError("未连接到Revit")

        chunks: List[bytes] = []
        self.sock.settimeout(self.timeout)
        start_time = time.time()

        try:
            while True:
                # 检查是否超时
                if time.time() - start_time > self.timeout:
                    raise TimeoutError(f"接收响应超时 ({self.timeout}秒)")

                try:
                    chunk = self.sock.recv(self.buffer_size)
                    if not chunk:
                        if not chunks:
                            raise ConnectionError("连接关闭，未收到任何数据")
                        break

                    chunks.append(chunk)

                    # 尝试解析已接收的数据
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        logger.debug(f"已接收完整响应 ({len(data)} 字节)")
                        return data
                    except json.JSONDecodeError:
                        # 继续接收更多数据
                        continue

                except socket.timeout:
                    if chunks:
                        # 如果已经接收到部分数据，尝试解析
                        try:
                            data = b''.join(chunks)
                            json.loads(data.decode('utf-8'))
                            logger.warning("接收超时，但已获得完整响应")
                            return data
                        except json.JSONDecodeError:
                            raise TimeoutError("接收超时，响应不完整")
                    else:
                        raise TimeoutError("接收超时，未收到任何数据")

                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    raise ConnectionError(f"接收数据时连接错误: {str(e)}")

        except Exception as e:
            if isinstance(e, (ConnectionError, TimeoutError)):
                raise
            else:
                logger.error(f"接收数据时出错: {str(e)}")
                raise ValueError(f"接收数据时出错: {str(e)}")

        # 如果有数据但循环正常结束
        if chunks:
            data = b''.join(chunks)
            try:
                json.loads(data.decode('utf-8'))
                logger.debug(f"已接收数据 ({len(data)} 字节)")
                return data
            except json.JSONDecodeError:
                raise ValueError("接收到的JSON响应不完整")
        else:
            raise ValueError("未接收到任何数据")

    def send_command(self, command_type: str, params: Union[Dict[str, Any], List[Dict[str, Any]]] = None) -> Dict[
        str, Any]:
        """
        向Revit发送命令并返回响应

        参数:
            command_type (str): 命令类型
            params (Dict[str, Any] 或 List[Dict[str, Any]]): 命令参数

        返回:
            Dict[str, Any]: 命令响应

        异常:
            ConnectionError: 连接错误
            TimeoutError: 请求超时
            ValueError: 参数或响应无效
            Exception: 其他错误
        """
        # 确保连接
        if not self.sock and not self.connect():
            raise ConnectionError("无法连接到Revit")

        try:
            logger.info(f"发送命令: {command_type}")
            logger.debug(f"命令参数: {params}")

            # 导入并创建请求对象
            from .rpc import JsonRPCRequest, JsonRPCResponse
            command = JsonRPCRequest(method=command_type, params=params)
            command_json = json.dumps(command.__dict__)

            # 发送命令
            self.sock.sendall(command_json.encode('utf-8'))
            logger.debug("命令已发送，等待响应...")

            # 使用 receive_full_response 接收完整数据流
            response_data = self.receive_full_response()
            logger.debug(f"已接收 {len(response_data)} 字节数据")

            # 解析响应
            try:
                response_dict = json.loads(response_data.decode('utf-8'))
                response = JsonRPCResponse(
                    id=response_dict.get("id"),
                    result=response_dict.get("result"),
                    error=response_dict.get("error")
                )
            except json.JSONDecodeError as e:
                logger.error(f"无法解析Revit响应: {str(e)}")
                if response_data:
                    logger.error(f"原始响应 (前200字节): {response_data[:200]}")
                raise ValueError(f"无效的Revit响应: {str(e)}")

            # 处理错误
            if response.error:
                error_message = response.error.get("message", "未知错误")
                error_code = response.error.get("code", -1)
                error_data = response.error.get("data")

                logger.error(f"Revit错误 (代码: {error_code}): {error_message}")
                if error_data:
                    logger.error(f"错误数据: {error_data}")

                raise Exception(f"Revit错误: {error_message}")

            return response.result or {}

        except socket.timeout:
            self.sock = None
            raise TimeoutError("等待Revit响应超时 - 请尝试简化请求")

        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            self.sock = None
            raise ConnectionError(f"与Revit的连接丢失: {str(e)}")

        except json.JSONDecodeError as e:
            logger.error(f"Revit响应的JSON无效: {str(e)}")
            if 'response_data' in locals() and response_data:
                logger.error(f"原始响应 (前200字节): {response_data[:200]}")
            raise ValueError(f"Revit响应无效: {str(e)}")

        except (ValueError, TimeoutError, ConnectionError) as e:
            self.sock = None
            raise

        except Exception as e:
            logger.error(f"与Revit通信时出错: {str(e)}")
            self.sock = None
            raise Exception(f"与Revit通信错误: {str(e)}")

    def is_connected(self) -> bool:
        """
        检查是否已连接到Revit

        返回:
            bool: 已连接返回True，否则返回False
        """
        if not self.sock:
            return False

        try:
            # 尝试发送心跳命令
            self.sock.settimeout(2.0)  # 短超时
            self.sock.sendall(b'{"jsonrpc":"2.0","method":"ping","id":0}')
            response = self.sock.recv(64)
            return bool(response)
        except:
            self.sock = None
            return False
        finally:
            if self.sock:
                self.sock.settimeout(self.timeout)  # 恢复正常超时

    def reconnect(self) -> bool:
        """
        重新连接到Revit

        返回:
            bool: 重连成功返回True，否则返回False
        """
        self.disconnect()
        return self.connect()
