#!/usr/bin/env python
"""
Script to import rhythm patterns into the database.

This script will:
1. Create rhythm patterns
2. Save them to the database

Usage:
    python scripts/import_rhythm_patterns.py           # Add patterns without clearing existing ones
    python scripts/import_rhythm_patterns.py --clear   # Clear existing patterns before adding new ones
"""

import asyncio
import logging
import argparse
import sys
import os
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import models
from note_gen.models.rhythm import RhythmPattern, RhythmNote

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description="Import rhythm patterns")
parser.add_argument("--clear", action="store_true", help="Clear existing rhythm patterns before adding new ones")
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
    """Clear existing rhythm patterns collection."""
    try:
        if args.clear:
            result = await db.rhythm_patterns.delete_many({})
            logger.info(f"Cleared {result.deleted_count} rhythm patterns")
    except Exception as e:
        logger.error(f"Clear failed: {e}")
        raise

async def create_rhythm_patterns() -> List[RhythmPattern]:
    """Create rhythm patterns."""
    logger.info('\nCreating rhythm patterns...')
    patterns = []
    
    # Define rhythm patterns
    rhythm_patterns_data = [
        {
            "name": "Basic 4/4",
            "description": "Basic 4/4 rhythm with quarter notes",
            "time_signature": [4, 4],
            "style": "basic",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 64},
                {"position": 1.0, "duration": 1.0, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64},
                {"position": 3.0, "duration": 1.0, "velocity": 64}
            ]
        },
        {
            "name": "Basic 3/4",
            "description": "Basic 3/4 rhythm with quarter notes",
            "time_signature": [3, 4],
            "style": "basic",
            "total_duration": 3.0,
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 64},
                {"position": 1.0, "duration": 1.0, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64}
            ]
        },
        {
            "name": "Eighth Notes 4/4",
            "description": "4/4 rhythm with eighth notes",
            "time_signature": [4, 4],
            "style": "basic",
            "total_duration": 4.0,
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
        {
            "name": "Syncopated 4/4",
            "description": "Syncopated rhythm in 4/4",
            "time_signature": [4, 4],
            "style": "syncopated",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 64},
                {"position": 1.5, "duration": 0.5, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64},
                {"position": 3.5, "duration": 0.5, "velocity": 64}
            ]
        },
        {
            "name": "Waltz 3/4",
            "description": "Classic waltz rhythm in 3/4",
            "time_signature": [3, 4],
            "style": "waltz",
            "total_duration": 3.0,
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 80},
                {"position": 1.0, "duration": 1.0, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64}
            ]
        },
        {
            "name": "Sixteenth Notes 4/4",
            "description": "4/4 rhythm with sixteenth notes",
            "time_signature": [4, 4],
            "style": "basic",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 0.25, "velocity": 64},
                {"position": 0.25, "duration": 0.25, "velocity": 64},
                {"position": 0.5, "duration": 0.25, "velocity": 64},
                {"position": 0.75, "duration": 0.25, "velocity": 64},
                {"position": 1.0, "duration": 0.25, "velocity": 64},
                {"position": 1.25, "duration": 0.25, "velocity": 64},
                {"position": 1.5, "duration": 0.25, "velocity": 64},
                {"position": 1.75, "duration": 0.25, "velocity": 64},
                {"position": 2.0, "duration": 0.25, "velocity": 64},
                {"position": 2.25, "duration": 0.25, "velocity": 64},
                {"position": 2.5, "duration": 0.25, "velocity": 64},
                {"position": 2.75, "duration": 0.25, "velocity": 64},
                {"position": 3.0, "duration": 0.25, "velocity": 64},
                {"position": 3.25, "duration": 0.25, "velocity": 64},
                {"position": 3.5, "duration": 0.25, "velocity": 64},
                {"position": 3.75, "duration": 0.25, "velocity": 64}
            ]
        },
        {
            "name": "Funk 4/4",
            "description": "Funk rhythm in 4/4",
            "time_signature": [4, 4],
            "style": "funk",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 0.5, "velocity": 80},
                {"position": 0.75, "duration": 0.25, "velocity": 64},
                {"position": 1.0, "duration": 0.5, "velocity": 72},
                {"position": 1.75, "duration": 0.25, "velocity": 64},
                {"position": 2.0, "duration": 0.5, "velocity": 80},
                {"position": 2.75, "duration": 0.25, "velocity": 64},
                {"position": 3.0, "duration": 0.5, "velocity": 72},
                {"position": 3.75, "duration": 0.25, "velocity": 64}
            ]
        },
        {
            "name": "Swing 4/4",
            "description": "Swing rhythm in 4/4",
            "time_signature": [4, 4],
            "style": "swing",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 0.67, "velocity": 80},
                {"position": 0.67, "duration": 0.33, "velocity": 64},
                {"position": 1.0, "duration": 0.67, "velocity": 72},
                {"position": 1.67, "duration": 0.33, "velocity": 64},
                {"position": 2.0, "duration": 0.67, "velocity": 80},
                {"position": 2.67, "duration": 0.33, "velocity": 64},
                {"position": 3.0, "duration": 0.67, "velocity": 72},
                {"position": 3.67, "duration": 0.33, "velocity": 64}
            ]
        },
        {
            "name": "Bossa Nova",
            "description": "Bossa Nova rhythm pattern",
            "time_signature": [4, 4],
            "style": "latin",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 0.5, "velocity": 80},
                {"position": 1.0, "duration": 0.5, "velocity": 64},
                {"position": 1.5, "duration": 0.5, "velocity": 72},
                {"position": 2.0, "duration": 0.5, "velocity": 64},
                {"position": 3.0, "duration": 0.5, "velocity": 72},
                {"position": 3.5, "duration": 0.5, "velocity": 64}
            ]
        },
        {
            "name": "Samba",
            "description": "Samba rhythm pattern",
            "time_signature": [4, 4],
            "style": "latin",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 0.25, "velocity": 80},
                {"position": 0.5, "duration": 0.25, "velocity": 64},
                {"position": 1.0, "duration": 0.25, "velocity": 72},
                {"position": 1.5, "duration": 0.25, "velocity": 64},
                {"position": 2.0, "duration": 0.25, "velocity": 80},
                {"position": 2.5, "duration": 0.25, "velocity": 64},
                {"position": 3.0, "duration": 0.25, "velocity": 72},
                {"position": 3.5, "duration": 0.25, "velocity": 64}
            ]
        },
        {
            "name": "Rock 4/4",
            "description": "Basic rock rhythm in 4/4",
            "time_signature": [4, 4],
            "style": "rock",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 80},
                {"position": 1.0, "duration": 1.0, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 72},
                {"position": 3.0, "duration": 1.0, "velocity": 64}
            ]
        },
        {
            "name": "Hip Hop",
            "description": "Hip hop rhythm pattern",
            "time_signature": [4, 4],
            "style": "hip_hop",
            "total_duration": 4.0,
            "notes": [
                {"position": 0.0, "duration": 0.5, "velocity": 80},
                {"position": 1.0, "duration": 0.5, "velocity": 64},
                {"position": 2.0, "duration": 0.5, "velocity": 80},
                {"position": 3.0, "duration": 0.5, "velocity": 64},
                {"position": 3.5, "duration": 0.5, "velocity": 72}
            ]
        }
    ]
    
    try:
        for pattern_data in rhythm_patterns_data:
            try:
                # Extract data
                name = pattern_data.get('name', 'Unknown Pattern')
                description = pattern_data.get('description', f'Rhythm: {name}')
                time_signature = pattern_data.get('time_signature', [4, 4])
                style = pattern_data.get('style', 'basic')
                total_duration = pattern_data.get('total_duration', 4.0)
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
                    name=name,
                    pattern=rhythm_notes,
                    time_signature=time_signature,
                    description=description,
                    style=style,
                    total_duration=total_duration
                )
                
                patterns.append(pattern)
                logger.info(f"✓ {name:<20} ({len(rhythm_notes)} notes)")
            except Exception as e:
                logger.error(f"✗ {pattern_data.get('name', 'Unknown'):<20} {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
    
    logger.info(f'Done. {len(patterns)} patterns processed.')
    return patterns

async def save_to_database(db: AsyncIOMotorDatabase, rhythm_patterns: List[RhythmPattern]) -> None:
    """Save rhythm patterns to database."""
    logger.info("\nSaving to database...")
    
    try:
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
        rhythm_patterns = await create_rhythm_patterns()
        
        # Save to database
        await save_to_database(db, rhythm_patterns)
        
        # Print summary
        logger.info("\nDone! Summary:")
        logger.info(f"- Rhythm patterns: {len(rhythm_patterns)}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
