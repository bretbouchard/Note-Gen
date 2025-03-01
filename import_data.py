import os
import bson
from pymongo import MongoClient

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_TEST_URI'))
db = client[os.getenv('DATABASE_NAME')]

# Function to import data from BSON files

def import_bson_data(collection_name, bson_file):
    with open(bson_file, 'rb') as f:
        data = bson.decode_all(f.read())
        db[collection_name].insert_many(data)
        print(f'Imported {len(data)} documents into {collection_name}.')

# Importing data from files

if __name__ == '__main__':
    import_bson_data('chord_progressions', 'db_backup/note_gen/chord_progressions.bson')
    import_bson_data('note_patterns', 'db_backup/note_gen/note_patterns.bson')
    import_bson_data('rhythm_patterns', 'db_backup/note_gen/rhythm_patterns.bson')

# Close MongoDB connection
client.close()
