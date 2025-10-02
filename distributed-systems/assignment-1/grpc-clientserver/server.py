import grpc
from concurrent import futures
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'generated'))

import user_service_pb2
import user_service_pb2_grpc

class Database:
    def __init__(self):
        self.db_path = 'users.db'
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def create_user(self, name, email, age):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', (name, email, age))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, age FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def update_user(self, user_id, name, email, age):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?', (name, email, age, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        result = cursor.rowcount > 0
        conn.close()
        return result

    def list_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, age FROM users')
        results = cursor.fetchall()
        conn.close()
        return results

class UserService(user_service_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.db = Database()

    def CreateUser(self, request, context):
        user_id = self.db.create_user(request.name, request.email, request.age)
        if user_id:
            user = user_service_pb2.User(
                id=user_id,
                name=request.name,
                email=request.email,
                age=request.age
            )
            return user_service_pb2.CreateUserResponse(
                user=user,
                success=True,
                message="User created successfully"
            )
        else:
            return user_service_pb2.CreateUserResponse(
                success=False,
                message="Failed to create user - email may already exist"
            )

    def GetUser(self, request, context):
        user_data = self.db.get_user(request.id)
        if user_data:
            user = user_service_pb2.User(
                id=user_data[0],
                name=user_data[1],
                email=user_data[2],
                age=user_data[3]
            )
            return user_service_pb2.GetUserResponse(
                user=user,
                success=True,
                message="User found"
            )
        else:
            return user_service_pb2.GetUserResponse(
                success=False,
                message="User not found"
            )

    def UpdateUser(self, request, context):
        success = self.db.update_user(request.id, request.name, request.email, request.age)
        if success:
            user = user_service_pb2.User(
                id=request.id,
                name=request.name,
                email=request.email,
                age=request.age
            )
            return user_service_pb2.UpdateUserResponse(
                user=user,
                success=True,
                message="User updated successfully"
            )
        else:
            return user_service_pb2.UpdateUserResponse(
                success=False,
                message="Failed to update user"
            )

    def DeleteUser(self, request, context):
        success = self.db.delete_user(request.id)
        if success:
            return user_service_pb2.DeleteUserResponse(
                success=True,
                message="User deleted successfully"
            )
        else:
            return user_service_pb2.DeleteUserResponse(
                success=False,
                message="User not found"
            )

    def ListUsers(self, request, context):
        users_data = self.db.list_users()
        users = []
        for user_data in users_data:
            user = user_service_pb2.User(
                id=user_data[0],
                name=user_data[1],
                email=user_data[2],
                age=user_data[3]
            )
            users.append(user)

        return user_service_pb2.ListUsersResponse(
            users=users,
            success=True,
            message=f"Found {len(users)} users"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    print("Starting gRPC server on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()