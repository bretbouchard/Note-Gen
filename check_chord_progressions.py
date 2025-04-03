from pymongo import MongoClient
import json
from bson import ObjectId

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

client = MongoClient('mongodb://localhost:27017')
db = client['note_gen']

# Get all chord progressions
progressions = list(db.chord_progressions.find({}))
print(f"Found {len(progressions)} chord progressions")

# Print the first 5 progressions with their names
for i, prog in enumerate(progressions[:5]):
    print(f"\nProgression {i+1}:")
    print(f"Name: {prog.get('name', 'No name')}")
    print(f"Tags: {prog.get('tags', [])}")
    print(f"Key: {prog.get('key', 'No key')}")
    print(f"Scale type: {prog.get('scale_type', 'No scale type')}")
    print(f"Number of chords: {len(prog.get('chords', []))}")

# Check if there are any other collections that might contain chord progressions
for collection in db.list_collection_names():
    if collection != 'chord_progressions' and db[collection].count_documents({}) > 0:
        # Check if documents in this collection have chord-related fields
        sample = db[collection].find_one({})
        if sample and ('chords' in sample or 'progression' in str(sample) or 'chord' in str(sample)):
            print(f"\nPossible chord progressions in {collection}:")
            count = db[collection].count_documents({})
            print(f"Found {count} documents")
            if count > 0:
                sample_doc = db[collection].find_one({})
                print(f"Sample document: {json.dumps(sample_doc, cls=JSONEncoder, indent=2)[:500]}...")
