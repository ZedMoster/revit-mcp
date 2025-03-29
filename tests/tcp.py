# -*- coding: utf-8 -*-

import socket
import json


def send_tcp_data(data, host="localhost", port=8080):
    """
    发送 TCP 数据到指定的主机和端口
    """
    try:
        # 将数据转换为 JSON 字符串
        data_str = json.dumps(data)

        # 创建 TCP 客户端
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            print(f"正在连接到 {host}:{port}")
            client.connect((host, port))
            print("连接成功，发送数据...")

            # 发送数据
            client.sendall(data_str.encode('utf-8'))
            print("数据已发送，等待响应...")

            # 接收响应数据
            buffer = client.recv(4096)
            if buffer:
                response = buffer.decode('utf-8')
                print(f"服务器响应: {response}")
            else:
                print("未收到服务器响应")
    except socket.error as e:
        print(f"网络错误: {e}")
    except Exception as e:
        print(f"异常: {e}")
