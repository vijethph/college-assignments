import time
import socket
import threading

def start_test_server():
    def server_handler():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', 8081))
        server_socket.listen(1)
        
        while True:
            client_socket, _ = server_socket.accept()
            data = client_socket.recv(1024)
            if data == b'hello':
                client_socket.send(b'Hello from server!')
            client_socket.close()
    
    server_thread = threading.Thread(target=server_handler)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.5)

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
    
    start_test_server()
    response_time = benchmark_socket()
    
    print(f"Socket response time: {response_time:.4f} seconds")