import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from note_gen.config import settings
from note_gen.database.db import get_db_conn
from note_gen.controllers.chord_progression_controller import ChordProgressionController
from note_gen.database.repositories.base import BaseRepository
from note_gen.models.chord_progression import ChordProgression
from note_gen.presenters.chord_progression_presenter import ChordProgressionPresenter
import json

async def debug_controller():
    print("Debugging chord progression controller...")
    
    # Get database connection
    db = await get_db_conn()
    print(f"Connected to database: {db.name}")
    
    # Create repository
    repository = BaseRepository[ChordProgression](db.chord_progressions)
    print("Created repository")
    
    # Create controller
    controller = ChordProgressionController(repository)
    print("Created controller")
    
    # Get all progressions
    print("\nGetting all progressions...")
    progressions = await controller.get_all_progressions()
    print(f"Found {len(progressions)} progressions")
    
    # Print progression details
    for i, prog in enumerate(progressions):
        print(f"\nProgression {i+1}:")
        print(f"ID: {prog.id}")
        print(f"Name: {prog.name}")
        print(f"Key: {prog.key}")
        print(f"Scale type: {prog.scale_type}")
        print(f"Number of chords: {len(prog.chords)}")
        
    # Present progressions
    print("\nPresenting progressions...")
    presented = ChordProgressionPresenter.present_many(progressions)
    print(f"Presented {len(presented)} progressions")
    print(json.dumps(presented, indent=2))
    
    # Check direct database access
    print("\nChecking direct database access...")
    cursor = db.chord_progressions.find({})
    documents = await cursor.to_list(length=None)
    print(f"Found {len(documents)} documents directly from database")
    
    # Try to convert documents to models
    print("\nConverting documents to models...")
    models = []
    for doc in documents:
        try:
            # Convert _id to id
            if '_id' in doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
            
            # Create model
            model = ChordProgression.model_validate(doc)
            models.append(model)
            print(f"Successfully converted document: {model.name}")
        except Exception as e:
            print(f"Error converting document: {e}")
            print(f"Document: {doc}")
    
    print(f"Successfully converted {len(models)} out of {len(documents)} documents")

if __name__ == "__main__":
    asyncio.run(debug_controller())
