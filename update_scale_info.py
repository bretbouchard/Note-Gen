from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_TEST_URI'))
db = client[os.getenv('DATABASE_NAME')]
collection = db['chord_progressions']  # Replace with your actual collection name

# Update documents to add scale_info
update_count = 0
for doc in collection.find({ 'scale_info': { '$exists': False } }):
    scale_info = {
        "root": {
            "note_name": "C",  # Default value or adjust as needed
            "octave": 4,       # Default value or adjust as needed
            "duration": 1,
            "velocity": 64,
            "stored_midi_number": None,
            "scale_degree": None
        },
        "key": doc.get('key'),
        "scale_type": doc.get('scale_type')
    }
    
    # Update the document
    collection.update_one(
        { '_id': doc['_id'] },
        { '$set': { 'scale_info': scale_info } }
    )
    update_count += 1

print(f'Updated {update_count} documents to include scale_info.')
