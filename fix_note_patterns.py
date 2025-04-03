import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import json

async def fix_note_patterns():
    # Connect to the database
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['note_gen']
    
    # Get all note patterns
    note_patterns = await db.note_patterns.find({}).to_list(length=None)
    print(f"Found {len(note_patterns)} note patterns")
    
    # Fix each note pattern
    for pattern in note_patterns:
        pattern_id = pattern['_id']
        name = pattern.get('name', 'Unknown')
        print(f"Fixing note pattern '{name}' with ID {pattern_id}")
        
        # Convert pattern to string representation
        if 'pattern' in pattern and isinstance(pattern['pattern'], list):
            # Convert each note to a string representation
            string_notes = []
            for note in pattern['pattern']:
                if isinstance(note, dict) and 'pitch' in note and 'octave' in note:
                    # Create a string representation of the note
                    pitch = note['pitch']
                    octave = note['octave']
                    string_note = f"{pitch}{octave}"
                    string_notes.append(string_note)
            
            # Update the pattern with string notes
            if string_notes:
                print(f"  - Converting {len(string_notes)} notes to strings")
                await db.note_patterns.update_one(
                    {'_id': pattern_id},
                    {'$set': {'pattern': string_notes}}
                )
                print(f"  - Updated pattern with string notes: {string_notes}")
            else:
                print(f"  - No valid notes found in pattern")
        else:
            print(f"  - No pattern field found or pattern is not a list")
    
    # Verify the fix
    fixed_patterns = await db.note_patterns.find({}).to_list(length=None)
    print(f"\nVerified {len(fixed_patterns)} note patterns")
    for pattern in fixed_patterns:
        name = pattern.get('name', 'Unknown')
        pattern_notes = pattern.get('pattern', [])
        print(f"- {name}: {len(pattern_notes)} notes, types: {[type(note).__name__ for note in pattern_notes[:3]]}...")

if __name__ == "__main__":
    asyncio.run(fix_note_patterns())
