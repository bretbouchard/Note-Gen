### Root conftest.py

import pytest
import asyncio

@pytest.fixture(scope='session')
def event_loop():
    """Create a new event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop  # Yield the loop to the tests
    loop.close()  # Close the loop after tests are done