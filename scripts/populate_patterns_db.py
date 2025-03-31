#!/usr/bin/env python
# scripts/populate_patterns_db.py

"""
Utility script to populate the database with patterns from presets.py.
This script will:
1. Convert chord progressions from presets.py to ChordProgressionPattern format
2. Convert note patterns from presets.py to NotePattern format
3. Convert rhythm patterns from presets.py to RhythmPattern format
4. Save all patterns to their respective collections in the database

Usage:
    python scripts/populate_patterns_db.py           # Add patterns without clearing existing ones
    python scripts/populate_patterns_db.py --clear   # Clear existing patterns before adding new ones
"""

import asyncio
import logging
import uuid
import argparse
import sys
import os
import re
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import models and patterns
from src.note_gen.models.patterns import (
    ChordProgressionPattern,
    ChordPatternItem,
    NotePattern,
    NotePatternData,
)
from src.note_gen.models.rhythm import RhythmPattern, RhythmNote  # Updated import
from src.note_gen.core.constants import (
    COMMON_PROGRESSIONS,
    NOTE_PATTERNS,
    RHYTHM_PATTERNS
)

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description="Populate database with patterns from presets")
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

# Reduce noise from MongoDB driver logs
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Also reduce noise from note pattern normalization unless in verbose mode
if not args.verbose:
    logging.getLogger("src.note_gen.models.patterns").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# MongoDB connection setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "test_note_gen")

async def get_db_conn():
    """Get a connection to the MongoDB database."""
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        await client.admin.command('ping')
        db = client[DATABASE_NAME]
        logger.info(f"Connected to: {DATABASE_NAME}")
        return client, db
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return None, None

async def close_db_conn(client):
    """Close the database connection."""
    if client is not None:
        try:
            client.close()
            logger.info("Connection closed")
        except Exception as e:
            logger.error(f"Close failed: {e}")

async def clear_collections(db):
    """Clear existing pattern collections."""
    if db is None:
        logger.error("Cannot clear: no database connection")
        return
        
    try:
        if args.clear:
            result = await db.chord_progression_patterns.delete_many({})
            logger.info(f"Cleared {result.deleted_count} chord patterns")
            
            result = await db.note_patterns.delete_many({})
            logger.info(f"Cleared {result.deleted_count} note patterns")
            
            result = await db.rhythm_patterns.delete_many({})
            logger.info(f"Cleared {result.deleted_count} rhythm patterns")
    except Exception as e:
        logger.error(f"Clear failed: {e}")
        raise

def sanitize_name(name: str) -> str:
    """Sanitize a name by removing special characters and replacing spaces with underscores."""
    # Remove special characters
    name = re.sub(r'[()\-]', '', name)
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    return name

async def convert_chord_progressions() -> List[ChordProgressionPattern]:
    """Convert chord progressions from presets to database format."""
    logger.info('\nConverting chord progressions...')
    patterns = []
    
    try:
        for name, numerals in COMMON_PROGRESSIONS.items():
            try:
                if args.verbose:
                    logger.debug(f"Processing: {name} ({numerals})")
                
                pattern_items = []
                for numeral in numerals:
                    try:
                        pattern_item = ChordPatternItem(
                            degree=numeral,
                            duration=4.0
                        )
                        pattern_items.append(pattern_item)
                        if args.verbose:
                            logger.debug(f"Created: {numeral} ({pattern_item.quality})")
                    except Exception as e:
                        logger.error(f"✗ {numeral} - {str(e)}")
                        raise
                
                pattern = ChordProgressionPattern(
                    name=name,
                    description=f"Common {name} progression",
                    pattern=pattern_items,
                    tags=["default", "common"],
                    complexity=0.5
                )
                patterns.append(pattern)
                logger.info(f'✓ {name} ({len(pattern_items)})')
            except Exception as e:
                logger.error(f'✗ {name} - {str(e)}')
                continue
    except Exception as e:
        logger.error(f'Conversion error: {str(e)}')
    
    logger.info(f'Done. {len(patterns)} patterns processed.')
    return patterns

async def convert_note_patterns() -> List[NotePattern]:
    """Convert note patterns from presets to database format."""
    logger.info('\nConverting note patterns...')
    patterns = []
    
    try:
        for name, pattern_data in NOTE_PATTERNS.items():
            try:
                # Create pattern with proper validation
                pattern = NotePattern(
                    name=name,
                    description=pattern_data.get('description', ''),
                    tags=pattern_data.get('tags', ['default']),
                    complexity=pattern_data.get('complexity', 0.5),
                    pattern=pattern_data.get('pattern', []),
                    data=NotePatternData(**pattern_data['data'])
                )
                patterns.append(pattern)
                logger.info(f"✓ {name:<15} ({len(pattern.data.notes)} notes, {len(pattern.pattern)} intervals)")
            except Exception as e:
                logger.error(f"✗ {name:<15} {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
    
    logger.info(f'Done. {len(patterns)} patterns processed.')
    return patterns

async def convert_rhythm_patterns() -> List[RhythmPattern]:
    """Convert rhythm patterns from presets to database format."""
    logger.info('\nConverting rhythm patterns...')
    patterns = []
    
    try:
        for pattern_data in RHYTHM_PATTERNS.values():
            try:
                name = pattern_data.get('name', 'Unknown')
                pattern = RhythmPattern(**pattern_data)
                patterns.append(pattern)
                logger.info(f'✓ {name}')
            except Exception as e:
                logger.error(f'✗ {name} - {str(e)}')
                continue
    except Exception as e:
        logger.error(f'Conversion error: {str(e)}')
    
    logger.info(f'Done. {len(patterns)} patterns processed.')
    return patterns

async def save_patterns_to_db(db, chord_patterns: List[ChordProgressionPattern], 
                            note_patterns: List[NotePattern], 
                            rhythm_patterns: List[RhythmPattern]):
    """Save patterns to database using bulk operations."""
    try:
        if chord_patterns:
            validated_patterns = [
                {
                    **p.model_dump(exclude_none=True, mode='json'),
                    'pattern': [
                        {
                            **item.model_dump(exclude_none=True, mode='json'),
                            'quality': item.quality.value
                        }
                        for item in p.pattern
                    ]
                }
                for p in chord_patterns
            ]
            result = await db.chord_progression_patterns.insert_many(validated_patterns)
            logger.info(f"Saved {len(result.inserted_ids)} chord patterns")
        
        if note_patterns:
            validated_patterns = [
                p.model_dump(exclude_none=True, mode='json')
                for p in note_patterns
            ]
            result = await db.note_patterns.insert_many(validated_patterns)
            logger.info(f"Saved {len(result.inserted_ids)} note patterns")
        
        if rhythm_patterns:
            validated_patterns = [
                p.model_dump(exclude_none=True, mode='json')
                for p in rhythm_patterns
            ]
            result = await db.rhythm_patterns.insert_many(validated_patterns)
            logger.info(f"Saved {len(result.inserted_ids)} rhythm patterns")
            
    except Exception as e:
        logger.error(f"Save failed: {e}")
        raise

async def main():
    """Main function to populate the database with patterns."""
    client = None
    try:
        client, db = await get_db_conn()
        if db is None:
            logger.error("Database connection failed")
            return

        if args.clear:
            await clear_collections(db)

        # Convert and save patterns
        chord_patterns = await convert_chord_progressions()
        note_patterns = await convert_note_patterns()
        rhythm_patterns = await convert_rhythm_patterns()

        logger.info(f"\nSaving to database...")
        await save_patterns_to_db(db, chord_patterns, note_patterns, rhythm_patterns)
        logger.info("\nDone! Summary:")
        logger.info(f"- Chord progressions: {len(chord_patterns)}")
        logger.info(f"- Note patterns: {len(note_patterns)}")
        logger.info(f"- Rhythm patterns: {len(rhythm_patterns)}")

    except Exception as e:
        logger.error(f"Population failed: {e}")
    finally:
        if client:
            await close_db_conn(client)

if __name__ == "__main__":
    asyncio.run(main())
