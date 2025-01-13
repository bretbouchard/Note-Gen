import sys
import os
import pytest
from fastapi.testclient import TestClient

# Adjust the path to include the src directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from note_gen.routers.user_routes import app

client = TestClient(app)

def test_manual_rhythm_pattern_check():
    response = client.get("/rhythm-patterns/quarter_notes")
    print(response.json())  # Print the response data for inspection

if __name__ == "__main__":
    test_manual_rhythm_pattern_check()
