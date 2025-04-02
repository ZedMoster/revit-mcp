# -*- coding: utf-8 -*-

import socket
import json

def receive_full_response(client, buffer_size=4096):
    """
    循环接收完整的响应数据
    """
    chunks = []
    while True:
        try:
            chunk = client.recv(buffer_size)
            if not chunk:
                break  # 连接关闭
            chunks.append(chunk)
        except socket.timeout:
            break  # 超时退出
        except Exception as e:
            print(f"接收数据时发生错误: {e}")
            break

    # 合并所有接收到的字节
    return b''.join(chunks)

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

            # 循环接收完整响应数据
            response_data = receive_full_response(client)

            # 解码响应数据
            if response_data:
                try:
                    response = response_data.decode('utf-8')
                    print(f"服务器响应: {response}")
                except UnicodeDecodeError as e:
                    print(f"解码错误: {e}")
                    response = response_data.decode('utf-8', errors='replace')
                    print(f"修正后的响应: {response}")
            else:
                print("未收到服务器响应")
    except socket.error as e:
        print(f"网络错误: {e}")
    except Exception as e:
        print(f"异常: {e}")
