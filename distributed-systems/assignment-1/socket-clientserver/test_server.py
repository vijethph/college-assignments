import unittest
import socket
import threading
import time

class TestSocket(unittest.TestCase):
    def test_hello_message(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 0))
        port = server_socket.getsockname()[1]
        server_socket.listen(1)

        def server():
            client_socket, _ = server_socket.accept()
            data = client_socket.recv(1024)
            message = data.decode('utf-8')
            if message == 'hello':
                client_socket.send(b'Hello from server!')
            client_socket.close()

        server_thread = threading.Thread(target=server)
        server_thread.start()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', port))
        client_socket.send(b'hello')
        response = client_socket.recv(1024)

        self.assertEqual(response, b'Hello from server!')

        client_socket.close()
        server_socket.close()
        server_thread.join()

if __name__ == '__main__':
    unittest.main()