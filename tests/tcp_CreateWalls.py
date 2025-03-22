import socket
import json

# 定义墙数据
walls = [
    {"startX": 0, "startY": 0, "endX": 12000, "endY": 0, "height": 3000, "width": 200},
    {"startX": 12000, "startY": 0, "endX": 12000, "endY": 10000, "height": 3000, "width": 200},
    {"startX": 12000, "startY": 10000, "endX": 0, "endY": 10000, "height": 3000, "width": 200},
    {"startX": 0, "startY": 10000, "endX": 0, "endY": 0, "height": 3000, "width": 200},
    {"startX": 6000, "startY": 0, "endX": 6000, "endY": 5000, "height": 3000, "width": 200},
    {"startX": 6000, "startY": 5000, "endX": 12000, "endY": 5000, "height": 3000, "width": 200},
    {"startX": 12000, "startY": 5000, "endX": 12000, "endY": 8000, "height": 3000, "width": 200},
    {"startX": 0, "startY": 5000, "endX": 6000, "endY": 5000, "height": 3000, "width": 200},
    {"startX": 6000, "startY": 5000, "endX": 6000, "endY": 8000, "height": 3000, "width": 200},
    {"startX": 6000, "startY": 8000, "endX": 12000, "endY": 8000, "height": 3000, "width": 200},
]

# 构造JSON-RPC请求
json_rpc_request = {
    "Id": "2.0",
    "Method": "CreateWalls",
    "Params": walls
}

def send_tcp_data(data, host="localhost", port=8080):
    try:
        # 将数据转换为JSON字符串
        data_str = json.dumps(data)
        
        # 创建TCP客户端
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

# 发送墙数据
send_tcp_data(json_rpc_request)
