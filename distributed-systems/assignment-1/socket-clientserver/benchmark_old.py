import time
import socket
import threading
from server import SocketServer

def benchmark_socket():
    start = time.time()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8081))
    client_socket.send(b'hello')
    client_socket.recv(1024)
    client_socket.close()

    end = time.time()
    return end - start

if __name__ == "__main__":
    print("Starting benchmark...")

    response_time = benchmark_socket()

    print(f"Socket response time: {response_time:.4f} seconds")