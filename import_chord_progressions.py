import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.chord import Chord
from note_gen.core.enums import ChordQuality

async def import_chord_progressions():
    # Connect to the database
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['note_gen']
    collection = db.chord_progressions
    
    # Load the chord progressions from the JSON file
    with open('docs/_chords_grouped.json', 'r') as f:
        progressions_data = json.load(f)
    
    print(f"Loaded {len(progressions_data)} chord progressions from file")
    
    # Count existing progressions
    existing_count = await collection.count_documents({})
    print(f"Found {existing_count} existing chord progressions in the database")
    
    # Import each progression
    imported_count = 0
    for prog_data in progressions_data:
        name = prog_data.get('name', 'Unknown Progression')
        
        # Check if progression already exists
        existing = await collection.find_one({"name": name})
        if existing:
            print(f"Progression '{name}' already exists, skipping")
            continue
        
        # Create chord objects
        chords = []
        for chord_symbol in prog_data.get('chords', []):
            try:
                # Parse the chord symbol to get root and quality
                root = chord_symbol[0]  # First character is the root note
                idx = 1
                
                # Handle sharp/flat
                if idx < len(chord_symbol) and chord_symbol[idx] in '#b':
                    root += chord_symbol[idx]
                    idx += 1
                
                # Parse quality
                quality_str = chord_symbol[idx:] if idx < len(chord_symbol) else ''
                
                # Map quality string to enum value
                quality_mapping = {
                    '': 'MAJOR',
                    'maj': 'MAJOR',
                    'maj7': 'MAJOR_SEVENTH',
                    'm': 'MINOR',
                    'min': 'MINOR',
                    'm7': 'MINOR_SEVENTH',
                    'min7': 'MINOR_SEVENTH',
                    'dim': 'DIMINISHED',
                    'dim7': 'DIMINISHED_SEVENTH',
                    'aug': 'AUGMENTED',
                    '7': 'DOMINANT_SEVENTH',
                    '9': 'DOMINANT_SEVENTH',  # Simplify for now
                    '7sus4': 'SUSPENDED_FOURTH',
                    'sus4': 'SUSPENDED_FOURTH',
                    'sus2': 'SUSPENDED_SECOND',
                    '7b9': 'DOMINANT_SEVENTH',  # Simplify for now
                    '7#5': 'DOMINANT_SEVENTH',  # Simplify for now
                    '7#9': 'DOMINANT_SEVENTH',  # Simplify for now
                    'm7b5': 'HALF_DIMINISHED_SEVENTH',
                    '5': 'MAJOR'  # Power chord, simplify to major
                }
                
                quality = quality_mapping.get(quality_str, 'MAJOR')
                
                # Create chord object
                chord = {
                    "root": root,
                    "quality": quality,
                    "duration": 4.0  # Default duration
                }
                chords.append(chord)
            except Exception as e:
                print(f"Error parsing chord '{chord_symbol}': {e}")
        
        # Create progression document
        progression = {
            "name": name,
            "key": "C",  # Default key
            "scale_type": "MAJOR",  # Default scale type
            "chords": chords,
            "tags": prog_data.get('tags', ["imported"]),
            "description": f"{name} - {', '.join(prog_data.get('degrees', []))}"
        }
        
        # Insert into database
        try:
            result = await collection.insert_one(progression)
            print(f"Imported progression '{name}' with ID {result.inserted_id}")
            imported_count += 1
        except Exception as e:
            print(f"Error importing progression '{name}': {e}")
    
    print(f"\nImported {imported_count} new chord progressions")
    
    # Verify the import
    final_count = await collection.count_documents({})
    print(f"Total chord progressions in database: {final_count}")

if __name__ == "__main__":
    asyncio.run(import_chord_progressions())
