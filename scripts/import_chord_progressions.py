#!/usr/bin/env python
"""
Script to import chord progressions from the docs/_chords_grouped.json file into the database.

This script will:
1. Read the chord progressions from the JSON file
2. Convert them to the database format
3. Save them to the database

Usage:
    python scripts/import_chord_progressions.py           # Add progressions without clearing existing ones
    python scripts/import_chord_progressions.py --clear   # Clear existing progressions before adding new ones
"""

import asyncio
import logging
import argparse
import sys
import os
import json
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import models
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.chord import Chord
from note_gen.models.chord_progression_item import ChordProgressionItem
from note_gen.core.enums import ScaleType, ChordQuality

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description="Import chord progressions from JSON file")
parser.add_argument("--clear", action="store_true", help="Clear existing chord progressions before adding new ones")
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
    """Clear existing chord progressions collection."""
    try:
        if args.clear:
            result = await db.chord_progressions.delete_many({})
            logger.info(f"Cleared {result.deleted_count} chord progressions")
    except Exception as e:
        logger.error(f"Clear failed: {e}")
        raise

def parse_chord_symbol(chord_symbol: str) -> tuple:
    """Parse a chord symbol into root and quality."""
    # Handle special cases
    if 'dim' in chord_symbol:
        if '7' in chord_symbol:
            return chord_symbol[0], ChordQuality.DIMINISHED_SEVENTH
        return chord_symbol[0], ChordQuality.DIMINISHED

    if 'aug' in chord_symbol:
        if '7' in chord_symbol:
            return chord_symbol[0], ChordQuality.AUGMENTED
        return chord_symbol[0], ChordQuality.AUGMENTED

    if 'sus' in chord_symbol:
        if 'sus2' in chord_symbol:
            return chord_symbol[0], ChordQuality.SUSPENDED_SECOND
        return chord_symbol[0], ChordQuality.SUSPENDED_FOURTH

    # Handle common qualities
    if 'maj7' in chord_symbol:
        return chord_symbol[0], ChordQuality.MAJOR_SEVENTH

    if 'm7b5' in chord_symbol:
        return chord_symbol[0], ChordQuality.HALF_DIMINISHED_SEVENTH

    if 'm7' in chord_symbol:
        return chord_symbol[0], ChordQuality.MINOR_SEVENTH

    if '7' in chord_symbol:
        if '#9' in chord_symbol or 'b9' in chord_symbol:
            return chord_symbol[0], ChordQuality.DOMINANT_SEVENTH
        return chord_symbol[0], ChordQuality.DOMINANT_SEVENTH

    if 'm' in chord_symbol:
        return chord_symbol[0], ChordQuality.MINOR

    # Handle power chords
    if '5' in chord_symbol:
        return chord_symbol[0], ChordQuality.MAJOR

    # Default to major
    return chord_symbol[0], ChordQuality.MAJOR

def get_scale_type_from_name(name: str) -> ScaleType:
    """Determine scale type from progression name."""
    name_lower = name.lower()

    if 'minor' in name_lower or ' min' in name_lower or 'dorian' in name_lower or 'phrygian' in name_lower:
        return ScaleType.MINOR

    if 'blues' in name_lower:
        # Use MINOR for blues since we don't have a BLUES scale type
        return ScaleType.MINOR

    if 'pentatonic' in name_lower:
        # Use MAJOR for pentatonic since we don't have a PENTATONIC_MAJOR scale type
        return ScaleType.MAJOR

    # Default to major
    return ScaleType.MAJOR

def get_tags_from_name(name: str) -> List[str]:
    """Extract tags from progression name."""
    tags = ["preset"]

    name_lower = name.lower()

    if 'jazz' in name_lower or 'ii-v-i' in name_lower or 'bebop' in name_lower:
        tags.append("jazz")

    if 'blues' in name_lower:
        tags.append("blues")

    if 'funk' in name_lower or 'groove' in name_lower:
        tags.append("funk")

    if 'metal' in name_lower or 'power' in name_lower or 'riff' in name_lower:
        tags.append("metal")

    if 'pop' in name_lower or 'axis' in name_lower:
        tags.append("pop")

    return tags

async def create_chord_progressions(json_file_path: str) -> List[ChordProgression]:
    """Create chord progressions from JSON file."""
    logger.info('\nCreating chord progressions...')
    progressions = []

    try:
        # Read JSON file
        with open(json_file_path, 'r') as f:
            chord_progressions_data = json.load(f)

        for prog_data in chord_progressions_data:
            try:
                name = prog_data.get('name', 'Unknown Progression')
                chord_symbols = prog_data.get('chords', [])

                # Skip if no chords
                if not chord_symbols:
                    logger.warning(f"Skipping {name}: No chords found")
                    continue

                # Extract data
                description = f"Progression: {name}"
                if 'degrees' in prog_data:
                    degrees_str = ', '.join(prog_data['degrees'])
                    description = f"{description} ({degrees_str})"

                # Determine scale type and tags
                scale_type = get_scale_type_from_name(name)
                tags = get_tags_from_name(name)

                # Add tags from JSON if available
                if 'tags' in prog_data:
                    tags.extend([tag for tag in prog_data['tags'] if tag not in tags])

                # Create chord objects
                chords = []
                items = []
                position = 0.0

                for chord_symbol in chord_symbols:
                    # Handle slash chords
                    if '/' in chord_symbol:
                        chord_part = chord_symbol.split('/')[0]
                        root, quality = parse_chord_symbol(chord_part)
                    else:
                        root, quality = parse_chord_symbol(chord_symbol)

                    duration = 1.0  # Default duration

                    # Create chord
                    chord = Chord(
                        root=root,
                        quality=quality,
                        duration=duration
                    )
                    chords.append(chord)

                    # Create chord progression item
                    item = ChordProgressionItem(
                        chord_symbol=chord_symbol,
                        chord=chord,
                        position=position
                    )
                    items.append(item)
                    position += duration

                # Determine key from first chord
                key = chords[0].root if chords else "C"

                # Create progression
                progression = ChordProgression(
                    name=name,
                    key=key,
                    scale_type=scale_type,
                    chords=chords,
                    items=items,
                    description=description,
                    tags=tags
                )

                progressions.append(progression)
                logger.info(f"✓ {name:<30} ({len(chords)} chords, tags: {', '.join(tags)})")
            except Exception as e:
                logger.error(f"✗ {prog_data.get('name', 'Unknown'):<30} {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")

    logger.info(f'Done. {len(progressions)} progressions processed.')
    return progressions

async def save_to_database(db: AsyncIOMotorDatabase, chord_progressions: List[ChordProgression]) -> None:
    """Save chord progressions to database."""
    logger.info("\nSaving to database...")

    try:
        # Save chord progressions
        if chord_progressions:
            chord_progression_dicts = [p.model_dump() for p in chord_progressions]
            result = await db.chord_progressions.insert_many(chord_progression_dicts)
            logger.info(f"Saved {len(result.inserted_ids)} chord progressions")
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

        # Path to JSON file
        json_file_path = os.path.join(project_root, "docs", "_chords_grouped.json")

        # Create chord progressions
        chord_progressions = await create_chord_progressions(json_file_path)

        # Save to database
        await save_to_database(db, chord_progressions)

        # Print summary
        logger.info("\nDone! Summary:")
        logger.info(f"- Chord progressions: {len(chord_progressions)}")

        # Print tags summary
        tags_count = {}
        for prog in chord_progressions:
            if prog.tags:  # Check if tags is not None
                for tag in prog.tags:
                    tags_count[tag] = tags_count.get(tag, 0) + 1

        logger.info("\nTags summary:")
        for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"- {tag}: {count}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
