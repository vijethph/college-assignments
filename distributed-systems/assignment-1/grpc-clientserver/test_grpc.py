import grpc
import pytest
import threading
import time
import os
import sys
from concurrent import futures

sys.path.append(os.path.join(os.path.dirname(__file__), 'generated'))

import user_service_pb2
import user_service_pb2_grpc
from server import UserService, serve

class TestGRPCUserService:
    @classmethod
    def setup_class(cls):
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        user_service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), cls.server)
        cls.server.add_insecure_port('[::]:50052')
        cls.server.start()

        cls.channel = grpc.insecure_channel('localhost:50052')
        cls.stub = user_service_pb2_grpc.UserServiceStub(cls.channel)
        time.sleep(0.1)

    @classmethod
    def teardown_class(cls):
        cls.channel.close()
        cls.server.stop(0)
        if os.path.exists('users.db'):
            os.remove('users.db')

    def test_create_user_success(self):
        request = user_service_pb2.CreateUserRequest(
            name="John Doe",
            email="john@example.com",
            age=30
        )
        response = self.stub.CreateUser(request)

        assert response.success == True
        assert response.user.name == "John Doe"
        assert response.user.email == "john@example.com"
        assert response.user.age == 30
        assert response.user.id > 0

    def test_get_user_success(self):
        create_request = user_service_pb2.CreateUserRequest(
            name="Jane Smith",
            email="jane@example.com",
            age=25
        )
        create_response = self.stub.CreateUser(create_request)
        user_id = create_response.user.id

        get_request = user_service_pb2.GetUserRequest(id=user_id)
        response = self.stub.GetUser(get_request)

        assert response.success == True
        assert response.user.name == "Jane Smith"
        assert response.user.email == "jane@example.com"
        assert response.user.age == 25

    def test_get_user_not_found(self):
        request = user_service_pb2.GetUserRequest(id=999)
        response = self.stub.GetUser(request)

        assert response.success == False
        assert "not found" in response.message.lower()

    def test_update_user_success(self):
        create_request = user_service_pb2.CreateUserRequest(
            name="Bob Wilson",
            email="bob@example.com",
            age=35
        )
        create_response = self.stub.CreateUser(create_request)
        user_id = create_response.user.id

        update_request = user_service_pb2.UpdateUserRequest(
            id=user_id,
            name="Bob Updated",
            email="bob.updated@example.com",
            age=36
        )
        response = self.stub.UpdateUser(update_request)

        assert response.success == True
        assert response.user.name == "Bob Updated"
        assert response.user.email == "bob.updated@example.com"
        assert response.user.age == 36

    def test_delete_user_success(self):
        create_request = user_service_pb2.CreateUserRequest(
            name="Alice Brown",
            email="alice@example.com",
            age=28
        )
        create_response = self.stub.CreateUser(create_request)
        user_id = create_response.user.id

        delete_request = user_service_pb2.DeleteUserRequest(id=user_id)
        response = self.stub.DeleteUser(delete_request)

        assert response.success == True

        get_request = user_service_pb2.GetUserRequest(id=user_id)
        get_response = self.stub.GetUser(get_request)
        assert get_response.success == False

    def test_list_users(self):
        request = user_service_pb2.ListUsersRequest()
        response = self.stub.ListUsers(request)

        assert response.success == True
        assert len(response.users) > 0

    def test_create_user_duplicate_email(self):
        request1 = user_service_pb2.CreateUserRequest(
            name="User One",
            email="duplicate@example.com",
            age=25
        )
        self.stub.CreateUser(request1)

        request2 = user_service_pb2.CreateUserRequest(
            name="User Two",
            email="duplicate@example.com",
            age=30
        )
        response = self.stub.CreateUser(request2)

        assert response.success == False
        assert "email" in response.message.lower()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])