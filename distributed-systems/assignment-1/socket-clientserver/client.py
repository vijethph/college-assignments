import socket

class SocketClient:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port

    def start(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        print("Connected to server. Type 'quit' to exit.")

        while True:
            message = input("Enter message: ")
            client_socket.send(message.encode('utf-8'))

            response = client_socket.recv(1024)
            print(f"{response.decode('utf-8')}")

            if message.lower() == 'quit':
                break

        client_socket.close()

client = SocketClient()
client.start()