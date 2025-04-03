import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import json
from note_gen.models.note import Note

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
        
        # Convert pattern to Note objects
        if 'pattern' in pattern and isinstance(pattern['pattern'], list):
            # Convert each note to a Note object
            note_objects = []
            for note in pattern['pattern']:
                if isinstance(note, str):
                    try:
                        # Create a Note object from the string
                        note_obj = Note.from_name(note)
                        note_dict = {
                            "pitch": note_obj.pitch,
                            "octave": note_obj.octave,
                            "duration": note_obj.duration,
                            "velocity": note_obj.velocity,
                            "position": note_obj.position,
                            "stored_midi_number": note_obj.stored_midi_number
                        }
                        note_objects.append(note_dict)
                    except Exception as e:
                        print(f"  - Error converting note '{note}': {e}")
                elif isinstance(note, dict):
                    # Already a dictionary, keep it
                    note_objects.append(note)
            
            # Update the pattern with Note objects
            if note_objects:
                print(f"  - Converting {len(note_objects)} notes to Note objects")
                await db.note_patterns.update_one(
                    {'_id': pattern_id},
                    {'$set': {'pattern': note_objects}}
                )
                print(f"  - Updated pattern with Note objects")
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
