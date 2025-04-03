#!/usr/bin/env python
"""
Script to import note patterns from the constants into the database.

This script will:
1. Read the note patterns from the constants
2. Convert them to the database format
3. Save them to the database

Usage:
    python scripts/import_note_patterns.py           # Add patterns without clearing existing ones
    python scripts/import_note_patterns.py --clear   # Clear existing patterns before adding new ones
"""

import asyncio
import logging
import argparse
import sys
import os
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import models
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.note import Note
from note_gen.core.constants import NOTE_PATTERNS
from note_gen.core.enums import ScaleType, PatternDirection

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description="Import note patterns from constants")
parser.add_argument("--clear", action="store_true", help="Clear existing note patterns before adding new ones")
parser.add_argument("--verbose", action="store_true", help="Show detailed debug logs")
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
    """Clear existing note patterns collection."""
    try:
        if args.clear:
            result = await db.note_patterns.delete_many({})
            logger.info(f"Cleared {result.deleted_count} note patterns")
    except Exception as e:
        logger.error(f"Clear failed: {e}")
        raise

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
                        stored_midi_number=60 + interval  # C4 (60) + interval
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

async def save_to_database(db: AsyncIOMotorDatabase, note_patterns: List[NotePattern]) -> None:
    """Save note patterns to database."""
    logger.info("\nSaving to database...")
    
    try:
        # Save note patterns
        if note_patterns:
            note_pattern_dicts = [p.model_dump() for p in note_patterns]
            result = await db.note_patterns.insert_many(note_pattern_dicts)
            logger.info(f"Saved {len(result.inserted_ids)} note patterns")
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
        note_patterns = await create_note_patterns()
        
        # Save to database
        await save_to_database(db, note_patterns)
        
        # Print summary
        logger.info("\nDone! Summary:")
        logger.info(f"- Note patterns: {len(note_patterns)}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
