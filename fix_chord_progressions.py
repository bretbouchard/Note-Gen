from pymongo import MongoClient
import json
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# Define minimal versions of the models to match the database schema
class ScaleType(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    LOCRIAN = "locrian"

class ChordQuality(str, Enum):
    MAJOR = "maj"
    MINOR = "min"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    DOMINANT_SEVENTH = "7"
    MAJOR_SEVENTH = "maj7"
    MINOR_SEVENTH = "min7"
    HALF_DIMINISHED = "m7b5"
    DIMINISHED_SEVENTH = "dim7"
    AUGMENTED_SEVENTH = "aug7"
    SUSPENDED_FOURTH = "sus4"
    SUSPENDED_SECOND = "sus2"

class Note(BaseModel):
    note_name: str
    octave: int = 4

class Chord(BaseModel):
    root: Optional[Note] = None
    quality: Optional[ChordQuality] = ChordQuality.MAJOR
    duration: float = 1.0
    position: Optional[float] = None

class ChordProgressionItem(BaseModel):
    chord_symbol: str
    chord: Optional[Chord] = None
    duration: float = 1.0
    position: float = 0.0

class ScaleInfo(BaseModel):
    key: str
    scale_type: ScaleType = ScaleType.MAJOR
    notes: List[str] = []

class ChordProgression(BaseModel):
    id: Optional[str] = None
    name: str = ""
    key: str = "C"
    root_note: Optional[str] = None
    scale_type: ScaleType = ScaleType.MAJOR
    scale_info: Optional[ScaleInfo] = None
    chords: List[Chord] = []
    items: List[ChordProgressionItem] = []
    pattern: List[str] = []
    total_duration: float = 4.0
    time_signature: Tuple[int, int] = (4, 4)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    quality: Optional[str] = None

# Connect to the database
client = MongoClient('mongodb://localhost:27017')
db = client['note_gen']

# Get all chord progressions
progressions = list(db.chord_progressions.find({}))
print(f"Found {len(progressions)} chord progressions in the database")

# Try to convert them to ChordProgression models
valid_progressions = []
for prog in progressions:
    try:
        # Convert ObjectId to string
        if '_id' in prog:
            prog['id'] = str(prog['_id'])
            del prog['_id']
            
        # Try to create a ChordProgression model
        progression = ChordProgression(**prog)
        valid_progressions.append(progression)
        print(f"Successfully converted progression: {progression.name}")
    except Exception as e:
        print(f"Error converting progression: {e}")
        print(f"Progression data: {json.dumps(prog, cls=JSONEncoder)}")

print(f"Successfully converted {len(valid_progressions)} out of {len(progressions)} progressions")

# Print the valid progressions
for i, prog in enumerate(valid_progressions):
    print(f"\nProgression {i+1}: {prog.name}")
    print(f"ID: {prog.id}")
    print(f"Key: {prog.key}")
    print(f"Scale type: {prog.scale_type}")
    print(f"Number of chords: {len(prog.chords)}")
    print(f"Tags: {prog.tags}")
    
    # Print the chords
    if prog.chords:
        print("Chords:")
        for j, chord in enumerate(prog.chords):
            print(f"  {j+1}. Root: {chord.root}, Quality: {chord.quality}, Duration: {chord.duration}")
