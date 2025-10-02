import time
import requests

BASE_URL = "http://localhost:8000"

def benchmark_rest():
    start = time.time()

    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "email": "john@example.com"
    }

    response = requests.post(f"{BASE_URL}/users/", json=user_data)

    if response.status_code == 200:
        user_id = response.json()["id"]

        requests.get(f"{BASE_URL}/users/{user_id}")

        update_data = {"age": 31}
        requests.patch(f"{BASE_URL}/users/{user_id}", json=update_data)

        requests.delete(f"{BASE_URL}/users/{user_id}")

    end = time.time()
    return end - start

def test_server_connection():
    try:
        response = requests.get(f"{BASE_URL}/healthcheck", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

if __name__ == "__main__":
    if not test_server_connection():
        print("Server not running at http://localhost:8000")
        exit(1)

    response_time = benchmark_rest()
    print("REST API benchmark time: ", end="")
    print(f"{response_time:.3f}s")