# scripts/extract_chord_patterns.py
"""
Utility script to extract chord progression patterns from existing chord progressions
and save them to the chord_progression_patterns collection.

This helps populate the new collection with standardized patterns derived from
existing chord progressions in the database.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# MongoDB connection setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

async def get_db_conn():
    """Get a connection to the MongoDB database."""
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        logger.info(f"Connected to database: {DATABASE_NAME}")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

async def fetch_chord_progressions(db) -> List[Dict[str, Any]]:
    """Fetch all chord progressions from the database."""
    try:
        cursor = db.chord_progressions.find({})
        progressions = await cursor.to_list(length=None)
        logger.info(f"Fetched {len(progressions)} chord progressions")
        return progressions
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

async def extract_pattern_from_progression(progression: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract a chord progression pattern from a chord progression."""
    try:
        # Check if progression has the required fields
        if "chords" not in progression or not isinstance(progression["chords"], list) or len(progression["chords"]) == 0:
            logger.warning(f"Progression missing chords: {progression.get('name', 'unknown')}")
            return None
            
        if "key" not in progression or "scale_type" not in progression:
            logger.warning(f"Progression missing key or scale_type: {progression.get('name', 'unknown')}")
            return None
            
        # Get the scale info for determining scale degrees
        key = progression.get("key", "C")
        scale_type = progression.get("scale_type", "MAJOR")
        
        # Extract the pattern
        pattern_items = []
        for chord in progression["chords"]:
            if not isinstance(chord, dict):
                continue
                
            # Skip if chord is missing root
            if "root" not in chord or not isinstance(chord["root"], dict):
                continue
                
            # Get the note name (needed for determining scale degree)
            note_name = chord["root"].get("note_name")
            if not note_name:
                continue
                
            # Determine scale degree based on note name and key
            # This is a simplified approximation - in a real system with proper scale info
            # we would use scale_info.get_scale_degree_for_note()
            notes_in_key = {
                "C": ["C", "D", "E", "F", "G", "A", "B"],
                "G": ["G", "A", "B", "C", "D", "E", "F#"],
                "D": ["D", "E", "F#", "G", "A", "B", "C#"],
                "A": ["A", "B", "C#", "D", "E", "F#", "G#"],
                "E": ["E", "F#", "G#", "A", "B", "C#", "D#"],
                "B": ["B", "C#", "D#", "E", "F#", "G#", "A#"],
                "F#": ["F#", "G#", "A#", "B", "C#", "D#", "E#"],
                "C#": ["C#", "D#", "E#", "F#", "G#", "A#", "B#"],
                "F": ["F", "G", "A", "Bb", "C", "D", "E"],
                "Bb": ["Bb", "C", "D", "Eb", "F", "G", "A"],
                "Eb": ["Eb", "F", "G", "Ab", "Bb", "C", "D"],
                "Ab": ["Ab", "Bb", "C", "Db", "Eb", "F", "G"],
                "Db": ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C"],
                "Gb": ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F"],
                "Cb": ["Cb", "Db", "Eb", "Fb", "Gb", "Ab", "Bb"],
            }
            
            if key not in notes_in_key:
                logger.warning(f"Unsupported key: {key}")
                continue
                
            # Find degree based on note position in key
            try:
                degree = notes_in_key[key].index(note_name) + 1
            except ValueError:
                # Note not in key, try to find closest match (simplified)
                logger.warning(f"Note {note_name} not found in key {key}")
                # Default to tonic if we can't determine degree
                degree = 1
            
            # Get the quality
            quality = chord.get("quality", "MAJOR")
            if isinstance(quality, dict) and "name" in quality:
                quality = quality["name"]
                
            # Get duration if available
            duration = chord.get("duration", 4.0)
            
            # Create pattern item
            pattern_item = {
                "degree": degree,
                "quality": quality,
                "duration": duration
            }
            
            # Add inversion if available
            if "inversion" in chord:
                pattern_item["inversion"] = chord["inversion"]
                
            pattern_items.append(pattern_item)
            
        # Create the pattern document
        pattern = {
            "id": f"pattern_{progression.get('id', '')}",
            "name": f"{progression.get('name', 'Unnamed')} Pattern",
            "pattern": pattern_items,
            "description": f"Pattern extracted from {progression.get('name', 'unnamed progression')}",
            "tags": progression.get("tags", []),
            "complexity": progression.get("complexity", 0.5)
        }
        
        # Add genre if available
        if "genre" in progression:
            pattern["genre"] = progression["genre"]
            
        return pattern
    except Exception as e:
        logger.error(f"Error extracting pattern from progression {progression.get('name', 'unknown')}: {e}")
        return None

async def save_patterns_to_db(db, patterns: List[Dict[str, Any]]) -> int:
    """Save patterns to the chord_progression_patterns collection."""
    try:
        if len(patterns) == 0:
            logger.warning("No patterns to save")
            return 0
            
        # Check if collection exists
        collections = await db.list_collection_names()
        if "chord_progression_patterns" not in collections:
            logger.info("Creating chord_progression_patterns collection")
            
        # Save patterns
        result = await db.chord_progression_patterns.insert_many(patterns)
        logger.info(f"Saved {len(result.inserted_ids)} patterns to database")
        return len(result.inserted_ids)
    except Exception as e:
        logger.error(f"Error saving patterns to database: {e}")
        return 0

async def main() -> None:
    """Main function to extract and save chord progression patterns."""
    try:
        logger.info("Starting extraction of chord progression patterns")
        
        # Get database connection
        db = await get_db_conn()
        if db is None:
            logger.error("Failed to connect to database")
            return
            
        # Fetch chord progressions
        progressions = await fetch_chord_progressions(db)
        if len(progressions) == 0:
            logger.warning("No chord progressions found in database")
            return
            
        logger.info(f"Processing {len(progressions)} chord progressions")
        
        # Extract patterns
        patterns = []
        for progression in progressions:
            pattern = await extract_pattern_from_progression(progression)
            if pattern is not None:
                patterns.append(pattern)
                
        logger.info(f"Extracted {len(patterns)} valid patterns")
        
        # Save patterns to database
        if len(patterns) > 0:
            saved_count = await save_patterns_to_db(db, patterns)
            logger.info(f"Successfully saved {saved_count} patterns to chord_progression_patterns collection")
        else:
            logger.warning("No valid patterns were extracted, nothing to save")
        
    except Exception as e:
        logger.error(f"Error in pattern extraction process: {e}")
    finally:
        logger.info("Pattern extraction process completed")
        
if __name__ == "__main__":
    asyncio.run(main())