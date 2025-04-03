from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')

all_dbs = client.list_database_names()
print('All databases:', all_dbs)

for db_name in all_dbs:
    db = client[db_name]
    collections = db.list_collection_names()
    print(f'\nDatabase: {db_name}')
    
    for coll in collections:
        count = db[coll].count_documents({})
        if count > 0:
            print(f'  - {coll}: {count} documents')
    
    if not collections:
        print('  No collections')
