### Root conftest.py

import pytest
import pytest_asyncio
import asyncio

@pytest_asyncio.fixture
async def client():
    """Async client fixture that can be used across tests."""
    from fastapi.testclient import TestClient
    from httpx import AsyncClient
    from main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client