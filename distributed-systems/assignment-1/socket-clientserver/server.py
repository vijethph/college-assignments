import socket
import threading

class SocketServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.running = False

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        self.running = True

        print(f"Server listening on {self.host}:{self.port}")

        while self.running:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address}")

            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.daemon = True
            thread.start()

    def handle_client(self, client_socket):
        with client_socket:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8').strip()

                if message.lower() == 'hello':
                    response = "Hello from server!"
                elif message.lower() == 'quit':
                    response = "Goodbye!"
                else:
                    response = f"Server received: {message}"

                client_socket.send(response.encode('utf-8'))

server = SocketServer()
server.start()