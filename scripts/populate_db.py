#!/usr/bin/env python
"""
Utility script to populate the database with common chord progressions, note patterns, and rhythm patterns.

This script will:
1. Convert chord progressions from constants.py to the database format
2. Convert note patterns from constants.py to the database format
3. Convert rhythm patterns from constants.py to the database format
4. Save all patterns to their respective collections in the database

Usage:
    python scripts/populate_db.py           # Add patterns without clearing existing ones
    python scripts/populate_db.py --clear   # Clear existing patterns before adding new ones
"""

import asyncio
import logging
import argparse
import sys
import os
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import models and constants
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.chord import Chord
from note_gen.models.chord_progression_item import ChordProgressionItem
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.note import Note
from note_gen.core.constants import COMMON_PROGRESSIONS, NOTE_PATTERNS
from note_gen.core.enums import ScaleType, ChordQuality, PatternDirection

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description="Populate database with patterns from constants")
parser.add_argument("--clear", action="store_true", help="Clear existing patterns before adding new ones")
parser.add_argument("--verbose", action="store_true", help="Show detailed debug logs for pattern processing")
args = parser.parse_args()

# Configure logging
logging.basicConfig(
    level=logging.INFO if not args.verbose else logging.DEBUG,
    format="%(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def get_db_conn() -> AsyncIOMotorDatabase:
    """Get database connection."""
    # Use environment variables or default values
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "note_gen")

    client = AsyncIOMotorClient(mongodb_url)
    return client[database_name]

async def clear_collections(db: AsyncIOMotorDatabase) -> None:
    """Clear existing pattern collections."""
    if db is None:
        logger.error("Cannot clear: no database connection")
        return

    try:
        if args.clear:
            result = await db.chord_progressions.delete_many({})
            logger.info(f"Cleared {result.deleted_count} chord progressions")

            result = await db.note_patterns.delete_many({})
            logger.info(f"Cleared {result.deleted_count} note patterns")

            result = await db.rhythm_patterns.delete_many({})
            logger.info(f"Cleared {result.deleted_count} rhythm patterns")
    except Exception as e:
        logger.error(f"Clear failed: {e}")
        raise

async def create_chord_progressions() -> List[ChordProgression]:
    """Create chord progressions from constants."""
    logger.info('\nCreating chord progressions...')
    progressions = []

    try:
        for name, prog_data in COMMON_PROGRESSIONS.items():
            try:
                # Extract data
                description = prog_data.get('description', f'Progression: {name}')
                chord_data = prog_data.get('chords', [])

                # Create chord objects
                chords = []
                items = []
                position = 0.0

                for i, chord_info in enumerate(chord_data):
                    root = chord_info.get('root', 'C')
                    quality_str = chord_info.get('quality', 'MAJOR')
                    quality = ChordQuality(quality_str)
                    duration = 1.0  # Default duration

                    # Create chord
                    chord = Chord(
                        root=root,
                        quality=quality,
                        duration=duration
                    )
                    chords.append(chord)

                    # Create chord progression item
                    # Map quality to symbol
                    quality_symbols = {
                        ChordQuality.MAJOR: '',
                        ChordQuality.MINOR: 'm',
                        ChordQuality.DIMINISHED: 'dim',
                        ChordQuality.AUGMENTED: 'aug',
                        ChordQuality.DOMINANT_SEVENTH: '7',
                        ChordQuality.MAJOR_SEVENTH: 'maj7',
                        ChordQuality.MINOR_SEVENTH: 'm7',
                        ChordQuality.DIMINISHED_SEVENTH: 'dim7',
                        ChordQuality.HALF_DIMINISHED_SEVENTH: 'm7b5',
                        ChordQuality.SUSPENDED_SECOND: 'sus2',
                        ChordQuality.SUSPENDED_FOURTH: 'sus4'
                    }
                    chord_symbol = f"{root}{quality_symbols.get(quality, '')}"
                    item = ChordProgressionItem(
                        chord_symbol=chord_symbol,
                        chord=chord,
                        position=position
                    )
                    items.append(item)
                    position += duration

                # Create progression
                progression = ChordProgression(
                    name=prog_data.get('name', name),
                    key="C",  # Default key
                    scale_type=ScaleType.MAJOR,  # Default scale type
                    chords=chords,
                    items=items,
                    description=description,
                    tags=["default", "preset"]
                )

                progressions.append(progression)
                logger.info(f"✓ {name:<15} ({len(chords)} chords)")
            except Exception as e:
                logger.error(f"✗ {name:<15} {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")

    logger.info(f'Done. {len(progressions)} progressions processed.')
    return progressions

async def create_note_patterns() -> List[NotePattern]:
    """Create note patterns from constants."""
    logger.info('\nCreating note patterns...')
    patterns = []

    try:
        for name, pattern_data in NOTE_PATTERNS.items():
            try:
                # Extract data
                intervals = pattern_data.get('intervals', [0, 4, 7])
                direction_str = pattern_data.get('direction', 'up')
                description = pattern_data.get('description', f'Pattern: {name}')

                # Convert direction string to enum
                direction = PatternDirection.UP
                if direction_str.lower() == 'down':
                    direction = PatternDirection.DOWN

                # Create sample pattern notes (will be replaced when used)
                pattern_notes = []
                for i, interval in enumerate(intervals):
                    note = Note(
                        pitch="C",  # Default pitch
                        octave=4,   # Default octave
                        duration=1.0,  # Default duration
                        position=float(i),
                        velocity=64,  # Default velocity
                        stored_midi_number=None  # Required parameter
                    )
                    pattern_notes.append(note)

                # Create pattern data
                pattern_data_obj = NotePatternData(
                    intervals=intervals,
                    direction=direction,
                    scale_type=ScaleType.MAJOR  # Default scale type
                )

                # Create pattern
                pattern = NotePattern(
                    name=name,
                    pattern=pattern_notes,
                    data=pattern_data_obj,
                    description=description,
                    tags=["default", "preset"]
                )

                patterns.append(pattern)
                logger.info(f"✓ {name:<15} ({len(intervals)} intervals)")
            except Exception as e:
                logger.error(f"✗ {name:<15} {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")

    logger.info(f'Done. {len(patterns)} patterns processed.')
    return patterns

async def create_rhythm_patterns() -> List[RhythmPattern]:
    """Create rhythm patterns."""
    logger.info('\nCreating rhythm patterns...')
    patterns = []

    # Define some basic rhythm patterns
    rhythm_patterns_data = {
        "basic_4_4": {
            "name": "Basic 4/4",
            "description": "Basic 4/4 rhythm with quarter notes",
            "time_signature": [4, 4],
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 64},
                {"position": 1.0, "duration": 1.0, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64},
                {"position": 3.0, "duration": 1.0, "velocity": 64}
            ]
        },
        "basic_3_4": {
            "name": "Basic 3/4",
            "description": "Basic 3/4 rhythm with quarter notes",
            "time_signature": [3, 4],
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 64},
                {"position": 1.0, "duration": 1.0, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64}
            ]
        },
        "eighth_notes_4_4": {
            "name": "Eighth Notes 4/4",
            "description": "4/4 rhythm with eighth notes",
            "time_signature": [4, 4],
            "notes": [
                {"position": 0.0, "duration": 0.5, "velocity": 64},
                {"position": 0.5, "duration": 0.5, "velocity": 64},
                {"position": 1.0, "duration": 0.5, "velocity": 64},
                {"position": 1.5, "duration": 0.5, "velocity": 64},
                {"position": 2.0, "duration": 0.5, "velocity": 64},
                {"position": 2.5, "duration": 0.5, "velocity": 64},
                {"position": 3.0, "duration": 0.5, "velocity": 64},
                {"position": 3.5, "duration": 0.5, "velocity": 64}
            ]
        },
        "syncopated_4_4": {
            "name": "Syncopated 4/4",
            "description": "Syncopated rhythm in 4/4",
            "time_signature": [4, 4],
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 64},
                {"position": 1.5, "duration": 0.5, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64},
                {"position": 3.5, "duration": 0.5, "velocity": 64}
            ]
        },
        "waltz_3_4": {
            "name": "Waltz 3/4",
            "description": "Classic waltz rhythm in 3/4",
            "time_signature": [3, 4],
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 80},
                {"position": 1.0, "duration": 1.0, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64}
            ]
        }
    }

    try:
        for name, pattern_data in rhythm_patterns_data.items():
            try:
                # Extract data
                time_signature = pattern_data.get('time_signature', [4, 4])
                description = pattern_data.get('description', f'Rhythm: {name}')
                notes_data = pattern_data.get('notes', [])

                # Create rhythm notes
                rhythm_notes = []
                for note_data in notes_data:
                    note = RhythmNote(
                        position=note_data.get('position', 0.0),
                        duration=note_data.get('duration', 1.0),
                        velocity=note_data.get('velocity', 64)
                    )
                    rhythm_notes.append(note)

                # Create pattern
                pattern = RhythmPattern(
                    name=pattern_data.get('name', name),
                    pattern=rhythm_notes,
                    time_signature=time_signature,
                    description=description,
                    style="basic",
                    total_duration=float(time_signature[0])
                )

                patterns.append(pattern)
                logger.info(f"✓ {name:<15} ({len(rhythm_notes)} notes)")
            except Exception as e:
                logger.error(f"✗ {name:<15} {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")

    logger.info(f'Done. {len(patterns)} patterns processed.')
    return patterns

async def save_to_database(db: AsyncIOMotorDatabase,
                          chord_progressions: List[ChordProgression],
                          note_patterns: List[NotePattern],
                          rhythm_patterns: List[RhythmPattern]) -> None:
    """Save patterns to database."""
    logger.info("\nSaving to database...")

    try:
        # Save chord progressions
        if chord_progressions:
            chord_progression_dicts = [p.model_dump() for p in chord_progressions]
            result = await db.chord_progressions.insert_many(chord_progression_dicts)
            logger.info(f"Saved {len(result.inserted_ids)} chord progressions")

        # Save note patterns
        if note_patterns:
            note_pattern_dicts = [p.model_dump() for p in note_patterns]
            result = await db.note_patterns.insert_many(note_pattern_dicts)
            logger.info(f"Saved {len(result.inserted_ids)} note patterns")

        # Save rhythm patterns
        if rhythm_patterns:
            rhythm_pattern_dicts = [p.model_dump() for p in rhythm_patterns]
            result = await db.rhythm_patterns.insert_many(rhythm_pattern_dicts)
            logger.info(f"Saved {len(result.inserted_ids)} rhythm patterns")
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        raise

async def main():
    """Main function."""
    try:
        # Get database connection
        db = await get_db_conn()

        # Clear collections if requested
        if args.clear:
            await clear_collections(db)

        # Create patterns
        chord_progressions = await create_chord_progressions()
        note_patterns = await create_note_patterns()
        rhythm_patterns = await create_rhythm_patterns()

        # Save to database
        await save_to_database(db, chord_progressions, note_patterns, rhythm_patterns)

        # Print summary
        logger.info("\nDone! Summary:")
        logger.info(f"- Chord progressions: {len(chord_progressions)}")
        logger.info(f"- Note patterns: {len(note_patterns)}")
        logger.info(f"- Rhythm patterns: {len(rhythm_patterns)}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
