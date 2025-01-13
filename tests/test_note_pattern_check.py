import pytest
from fastapi.testclient import TestClient
from src.note_gen.routers.user_routes import app

client = TestClient(app)

def test_manual_note_pattern_check():
    response = client.get("/note-patterns/1")
    print(response.json())  # Print the response data for inspection

if __name__ == "__main__":
    test_manual_note_pattern_check()
