from pymongo import MongoClient
import json
from bson import ObjectId

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# Connect to the database
client = MongoClient('mongodb://localhost:27017')
db = client['note_gen']

# Check note patterns
note_patterns = list(db.note_patterns.find({}))
print(f"Found {len(note_patterns)} note patterns")
if note_patterns:
    print("\nSample note pattern:")
    print(json.dumps(note_patterns[0], cls=JSONEncoder, indent=2))

# Check rhythm patterns
rhythm_patterns = list(db.rhythm_patterns.find({}))
print(f"\nFound {len(rhythm_patterns)} rhythm patterns")
if rhythm_patterns:
    print("\nSample rhythm pattern:")
    print(json.dumps(rhythm_patterns[0], cls=JSONEncoder, indent=2))
