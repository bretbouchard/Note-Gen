import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.note import Note
from note_gen.core.constants import NOTE_PATTERNS, RHYTHM_PATTERNS
from note_gen.validation.midi_validation import midi_to_octave_pitch

async def import_patterns():
    # Connect to the database
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['note_gen']

    # Clear existing patterns
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})

    print("Importing note patterns...")

    # Define note patterns from constants
    note_patterns = []

    # Convert patterns from constants
    for pattern_name, pattern_data in NOTE_PATTERNS.items():
        # Create pattern notes based on intervals
        pattern_notes = []

        # Get intervals and direction
        intervals = pattern_data.get("intervals", [])
        direction = pattern_data.get("direction", "up")

        # Generate notes from intervals
        for interval in intervals:
            # Calculate the note based on the interval
            # C4 is MIDI note 60
            midi_number = 60 + interval
            octave, semitone = midi_to_octave_pitch(midi_number)

            # Convert semitone to pitch
            pitch_map = {
                0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
                6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
            }
            pitch = pitch_map[semitone]

            # Create note
            note = Note(
                pitch=pitch,
                octave=octave,
                duration=1.0,
                velocity=100,
                position=0.0,
                stored_midi_number=None
            )
            pattern_notes.append(note)

        # Create pattern data
        pattern = {
            "name": pattern_name.replace("_", " ").title(),
            "pattern": pattern_notes,
            "data": {
                "key": "C",
                "root_note": "C",
                "scale_type": "MAJOR",
                "direction": direction,
                "octave": 4,
                "octave_range": [3, 5]
            },
            "tags": ["scale", pattern_name]
        }

        # Add description if available
        if "description" in pattern_data:
            pattern["description"] = pattern_data["description"]

        note_patterns.append(pattern)

    # Import note patterns
    for pattern_data in note_patterns:
        # Create NotePatternData
        data = NotePatternData(**pattern_data["data"])

        # Create NotePattern
        pattern = NotePattern(
            name=pattern_data["name"],
            pattern=pattern_data["pattern"],
            data=data,
            tags=pattern_data.get("tags", []),
            skip_validation=False
        )

        # Convert to dictionary for MongoDB
        pattern_dict = pattern.model_dump(exclude={"scale_info"})

        # Insert into database
        result = await db.note_patterns.insert_one(pattern_dict)
        print(f"Imported note pattern '{pattern_data['name']}' with ID {result.inserted_id}")

    print("\nImporting rhythm patterns...")

    # Define rhythm patterns from constants
    rhythm_patterns = []

    # Convert patterns from constants
    for pattern_name, pattern_data in RHYTHM_PATTERNS.items():
        # Get notes and other data
        notes = pattern_data.get("notes", [])
        total_duration = pattern_data.get("total_duration", 4.0)
        description = pattern_data.get("description", "")

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

        # Create rhythm notes
        rhythm_notes = []
        for note_data in notes:
            # Create a dictionary with the note data
            note_dict = {
                "position": note_data.get("position", 0.0),
                "duration": note_data.get("duration", 1.0),
                "velocity": note_data.get("velocity", 100),
                "accent": note_data.get("accent", False)
            }
            # Create the rhythm note
            rhythm_note = RhythmNote(**note_dict)
            rhythm_notes.append(rhythm_note)

        # Create pattern
        pattern = {
            "name": pattern_name.replace("_", " ").title(),
            "pattern": rhythm_notes,
            "time_signature": time_signature,
            "total_duration": total_duration,
            "style": style,
            "description": description,
            "swing_enabled": swing_enabled
        }

        rhythm_patterns.append(pattern)

    # Import rhythm patterns
    for pattern_data in rhythm_patterns:
        # The pattern already contains RhythmNote objects
        pattern_notes = pattern_data["pattern"]

        # Create RhythmPattern
        pattern = RhythmPattern(
            name=pattern_data["name"],
            pattern=pattern_notes,
            time_signature=pattern_data["time_signature"],
            total_duration=pattern_data["total_duration"],
            style=pattern_data["style"],
            description=pattern_data.get("description", ""),
            swing_enabled=pattern_data.get("swing_enabled", False)
        )

        # Convert to dictionary for MongoDB
        pattern_dict = pattern.model_dump()

        # Insert into database
        result = await db.rhythm_patterns.insert_one(pattern_dict)
        print(f"Imported rhythm pattern '{pattern_data['name']}' with ID {result.inserted_id}")

    # Verify the import
    note_patterns_count = await db.note_patterns.count_documents({})
    rhythm_patterns_count = await db.rhythm_patterns.count_documents({})

    print(f"\nImported {note_patterns_count} note patterns and {rhythm_patterns_count} rhythm patterns")

if __name__ == "__main__":
    asyncio.run(import_patterns())
