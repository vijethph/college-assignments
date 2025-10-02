import time
import grpc
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'generated'))

import user_service_pb2
import user_service_pb2_grpc

SERVER_ADDRESS = 'localhost:50051'

def benchmark_grpc():
    channel = grpc.insecure_channel(SERVER_ADDRESS)
    stub = user_service_pb2_grpc.UserServiceStub(channel)

    start = time.time()

    create_request = user_service_pb2.CreateUserRequest(
        name="Test User",
        email="test@benchmark.com",
        age=25
    )
    create_response = stub.CreateUser(create_request)
    user_id = create_response.user.id

    get_request = user_service_pb2.GetUserRequest(id=user_id)
    stub.GetUser(get_request)

    update_request = user_service_pb2.UpdateUserRequest(
        id=user_id,
        name="Updated User",
        email="updated@benchmark.com",
        age=30
    )
    stub.UpdateUser(update_request)

    delete_request = user_service_pb2.DeleteUserRequest(id=user_id)
    stub.DeleteUser(delete_request)

    end = time.time()

    channel.close()
    return end - start

def main():
    print("gRPC Benchmark Results")

    try:
        total_time = benchmark_grpc()
        print(f"Total time for CRUD operations: {total_time:.4f} seconds")
        print(f"Time in milliseconds: {total_time*1000:.2f} ms")

    except grpc.RpcError as e:
        print(f"gRPC Error: {e}")
        print(f"Make sure the server is running on {SERVER_ADDRESS}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
