from pymongo import MongoClient
import json
from bson import ObjectId
from typing import Dict, Any, List

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# Connect to the database
client = MongoClient('mongodb://localhost:27017')
db = client['note_gen']

# Get all chord progressions
progressions = list(db.chord_progressions.find({}))
print(f"Found {len(progressions)} chord progressions in the database")

# Define quality mapping
quality_mapping = {
    'maj': 'MAJOR',
    'min': 'MINOR',
    'dim': 'DIMINISHED',
    'aug': 'AUGMENTED',
    '7': 'DOMINANT_SEVENTH',
    'maj7': 'MAJOR_SEVENTH',
    'm7': 'MINOR_SEVENTH',
    'dim7': 'DIMINISHED_SEVENTH',
    'm7b5': 'HALF_DIMINISHED_SEVENTH',
    'sus2': 'SUSPENDED_SECOND',
    'sus4': 'SUSPENDED_FOURTH'
}

# Migrate each progression
for prog in progressions:
    print(f"\nMigrating progression: {prog.get('name', 'Unknown')}")
    
    # Check if the progression has chords
    if 'chords' in prog and prog['chords']:
        updated_chords = []
        
        for chord in prog['chords']:
            updated_chord = {}
            
            # Fix root field
            if 'root' in chord and isinstance(chord['root'], dict) and 'note_name' in chord['root']:
                updated_chord['root'] = chord['root']['note_name']
                print(f"  - Updated root from {chord['root']} to {updated_chord['root']}")
            else:
                updated_chord['root'] = chord.get('root', 'C')
                
            # Fix quality field
            if 'quality' in chord and isinstance(chord['quality'], str):
                if chord['quality'] in quality_mapping:
                    updated_chord['quality'] = quality_mapping[chord['quality']]
                    print(f"  - Updated quality from {chord['quality']} to {updated_chord['quality']}")
                else:
                    updated_chord['quality'] = 'MAJOR'
                    print(f"  - Unknown quality {chord['quality']}, defaulting to MAJOR")
            else:
                updated_chord['quality'] = 'MAJOR'
                
            # Copy other fields
            for key, value in chord.items():
                if key not in ['root', 'quality']:
                    updated_chord[key] = value
                    
            updated_chords.append(updated_chord)
            
        # Update the progression with the fixed chords
        result = db.chord_progressions.update_one(
            {'_id': prog['_id']},
            {'$set': {'chords': updated_chords}}
        )
        
        print(f"  - Updated {result.modified_count} progression")
    else:
        print("  - No chords to update")

# Verify the changes
updated_progressions = list(db.chord_progressions.find({}))
print(f"\nVerifying {len(updated_progressions)} chord progressions")

for prog in updated_progressions:
    print(f"\nProgression: {prog.get('name', 'Unknown')}")
    
    if 'chords' in prog and prog['chords']:
        for i, chord in enumerate(prog['chords']):
            print(f"  - Chord {i+1}: root={chord.get('root', 'N/A')}, quality={chord.get('quality', 'N/A')}")
    else:
        print("  - No chords")

print("\nMigration complete!")
