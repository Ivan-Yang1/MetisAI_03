import sys
import asyncio
sys.path.append("E:\\Project\\MetisAI\\MetisAI_03\\backend")
from fastapi.testclient import TestClient
from main import app

def test_list_agents():
    client = TestClient(app)
    response = client.get("/api/v1/agents/")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")

if __name__ == "__main__":
    test_list_agents()
