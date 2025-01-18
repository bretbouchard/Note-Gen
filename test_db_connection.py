from pymongo import MongoClient

def test_db_connection():
    try:
        # Connect to the MongoDB server
        client = MongoClient('mongodb://localhost:27017/')
        
        # Access the note_gen database
        db = client['note_gen']
        
        # Fetch and print the names of the collections
        collections = db.list_collection_names()
        print("Connected to the database. Collections:", collections)
        
    except Exception as e:
        print("Failed to connect to the database:", str(e))

if __name__ == "__main__":
    test_db_connection()
