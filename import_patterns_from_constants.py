import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from note_gen.core.constants import NOTE_PATTERNS, RHYTHM_PATTERNS
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.core.enums import PatternDirection

async def import_patterns():
    # Connect to the database
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['note_gen']
    
    # Clear existing patterns
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    
    print("Importing note patterns...")
    
    # Import note patterns from constants
    for pattern_name, pattern_data in NOTE_PATTERNS.items():
        # Get pattern data
        intervals = pattern_data.get('intervals', [])
        direction = pattern_data.get('direction', 'up')
        description = pattern_data.get('description', '')
        
        # Create pattern data
        data = {
            "key": "C",
            "root_note": "C",
            "scale_type": "MAJOR",
            "direction": direction,
            "octave": 4,
            "octave_range": [3, 5],
            "intervals": intervals
        }
        
        # Create pattern
        pattern = {
            "name": pattern_name.replace("_", " ").title(),
            "description": description,
            "pattern": [f"C{4 + i//12}" for i in intervals],  # Convert intervals to note names
            "data": data,
            "tags": ["scale", pattern_name]
        }
        
        # Insert into database
        result = await db.note_patterns.insert_one(pattern)
        print(f"Imported note pattern '{pattern_name}' with ID {result.inserted_id}")
    
    print("\nImporting rhythm patterns...")
    
    # Import rhythm patterns from constants
    for pattern_name, pattern_data in RHYTHM_PATTERNS.items():
        # Get pattern data
        notes = pattern_data.get('notes', [])
        total_duration = pattern_data.get('total_duration', 4.0)
        description = pattern_data.get('description', '')
        
        # Determine time signature based on total duration
        time_signature = [4, 4]  # Default
        if total_duration == 3.0:
            time_signature = [3, 4]  # Waltz
        
        # Determine style based on pattern name
        style = "basic"
        if "rock" in pattern_name:
            style = "rock"
        elif "swing" in pattern_name:
            style = "jazz"
        elif "waltz" in pattern_name:
            style = "waltz"
        elif "bossa" in pattern_name:
            style = "latin"
        elif "syncopated" in pattern_name:
            style = "syncopated"
        
        # Determine if swing is enabled
        swing_enabled = "swing" in pattern_name
        
        # Create pattern
        pattern = {
            "name": pattern_name.replace("_", " ").title(),
            "pattern": notes,
            "time_signature": time_signature,
            "total_duration": total_duration,
            "style": style,
            "description": description,
            "swing_enabled": swing_enabled
        }
        
        # Insert into database
        result = await db.rhythm_patterns.insert_one(pattern)
        print(f"Imported rhythm pattern '{pattern_name}' with ID {result.inserted_id}")
    
    # Verify the import
    note_patterns_count = await db.note_patterns.count_documents({})
    rhythm_patterns_count = await db.rhythm_patterns.count_documents({})
    
    print(f"\nImported {note_patterns_count} note patterns and {rhythm_patterns_count} rhythm patterns")

if __name__ == "__main__":
    asyncio.run(import_patterns())
