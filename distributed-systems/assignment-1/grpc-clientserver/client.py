import grpc
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'generated'))

import user_service_pb2
import user_service_pb2_grpc

def run_client():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_service_pb2_grpc.UserServiceStub(channel)

        print("Creating a user...")
        create_response = stub.CreateUser(user_service_pb2.CreateUserRequest(
            name="John Doe",
            email="john@example.com",
            age=30
        ))
        print(f"Create response: {create_response.message}")

        if create_response.success:
            user_id = create_response.user.id
            print(f"Created user with ID: {user_id}")

            print("\nGetting user...")
            get_response = stub.GetUser(user_service_pb2.GetUserRequest(id=user_id))
            if get_response.success:
                user = get_response.user
                print(f"User: ID={user.id}, Name={user.name}, Email={user.email}, Age={user.age}")

            print("\nUpdating user...")
            update_response = stub.UpdateUser(user_service_pb2.UpdateUserRequest(
                id=user_id,
                name="John Smith",
                email="johnsmith@example.com",
                age=31
            ))
            print(f"Update response: {update_response.message}")

            print("\nListing all users...")
            list_response = stub.ListUsers(user_service_pb2.ListUsersRequest())
            print(f"List response: {list_response.message}")
            for user in list_response.users:
                print(f"User: ID={user.id}, Name={user.name}, Email={user.email}, Age={user.age}")

            print("\nDeleting user...")
            delete_response = stub.DeleteUser(user_service_pb2.DeleteUserRequest(id=user_id))
            print(f"Delete response: {delete_response.message}")

if __name__ == '__main__':
    run_client()