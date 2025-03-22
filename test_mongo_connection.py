from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    try:
        # Verify connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # List databases
        databases = await client.list_database_names()
        print("Available databases:", databases)
        
    except Exception as e:
        print("Connection failed:", e)
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_connection())