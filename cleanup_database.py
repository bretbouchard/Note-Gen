from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["note_gen"]

# Cleanup function for note_patterns
def cleanup_note_patterns():
    result = db.note_patterns.delete_many({"id": {"$exists": False}})
    print(f"Removed {result.deleted_count} note patterns without an ID.")

# Cleanup function for rhythm_patterns
def cleanup_rhythm_patterns():
    result = db.rhythm_patterns.delete_many({"id": {"$exists": False}})
    print(f"Removed {result.deleted_count} rhythm patterns without an ID.")

# Run the cleanup functions
cleanup_note_patterns()
cleanup_rhythm_patterns()

# Close the connection
client.close()
