from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
import time

def init_replica_set():
    """Initialize MongoDB replica set configuration - for external testing only"""
    print("Connecting to MongoDB...")

    try:
        client = MongoClient(
            'localhost',
            27017,
            username='admin',
            password='admin123',
            authSource='admin',
            directConnection=True,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )

        client.admin.command('ping')
        print("Connected to MongoDB successfully!")
    except ServerSelectionTimeoutError as e:
        print(f"Connection timeout: {e}")
        return False
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error connecting to MongoDB: {e}")
        return False

    try:
        status = client.admin.command('replSetGetStatus')
        print(f"Replica set already initialized: {status['set']}")
        print(f"Members: {len(status['members'])}")
        for member in status['members']:
            print(f"  - {member['name']}: {member['stateStr']}")
        return True
    except OperationFailure as e:
        print(f"Replica set not initialized or error: {e}")
        return False

if __name__ == '__main__':
    init_replica_set()
