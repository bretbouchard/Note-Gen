import requests
import json
from pymongo import MongoClient
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

# Get all chord progressions from the database
db_progressions = list(db.chord_progressions.find({}))
print(f"Found {len(db_progressions)} chord progressions in the database")

# Get all chord progressions from the API
api_url = "http://localhost:8000/api/v1/chord-progressions/"
try:
    response = requests.get(api_url)
    response.raise_for_status()
    api_data = response.json()
    api_progressions = api_data.get("progressions", [])
    print(f"Found {len(api_progressions)} chord progressions from the API")
    
    # Compare the results
    print("\nAPI Response:")
    print(json.dumps(api_data, indent=2))
    
    # Check the export endpoint
    export_url = "http://localhost:8000/api/v1/import-export/export/chord-progressions?format=json"
    export_response = requests.get(export_url)
    export_response.raise_for_status()
    export_data = export_response.json() if export_response.text else []
    print(f"\nFound {len(export_data)} chord progressions from the export endpoint")
    print("Export Response:")
    print(json.dumps(export_data, indent=2)[:500] + "..." if len(json.dumps(export_data, indent=2)) > 500 else json.dumps(export_data, indent=2))
    
except Exception as e:
    print(f"Error accessing API: {e}")

# Print the database progressions for comparison
print("\nDatabase Progressions:")
for i, prog in enumerate(db_progressions):
    print(f"\nProgression {i+1}:")
    print(json.dumps(prog, cls=JSONEncoder, indent=2))
