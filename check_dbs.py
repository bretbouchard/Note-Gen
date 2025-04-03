from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')

possible_dbs = [
    'note_gen', 
    'note_gen_db', 
    'note_gen_db_dev', 
    'test_note_gen', 
    'note_gen_test', 
    'test_db', 
    'dev_db', 
    'production_db', 
    'prod_db'
]

for db_name in possible_dbs:
    db = client[db_name]
    collections = db.list_collection_names()
    print(f'Database: {db_name}')
    
    for coll in collections:
        count = db[coll].count_documents({})
        if count > 0:
            print(f'  - {coll}: {count} documents')
    
    if not collections:
        print('  No collections')
    print()
