from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, validator
import logging
import os
import sys

# Set up logging configuration
logger = logging.getLogger(__name__)
logger.propagate = False

# Set up logging to output to test console only
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Log to console only
    ]
)

from src.note_gen.models.note import Note
from src.note_gen.models.chord_progression import ChordProgression 
from src.note_gen.models.rhythm_pattern import RhythmPattern
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ScaleType, ChordQualityType
from src.note_gen.models.scale import Scale
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.scale_degree import ScaleDegree

logger = logging.getLogger(__name__)
logger.propagate = False

async def generate_sequence_from_presets(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
    chord_progression: Dict[str, Any],
    note_pattern: Dict[str, Any],
    rhythm_pattern: Dict[str, Any]
) -> NoteSequence:
    # Placeholder logic for generating a sequence from presets
    logger.debug("Generating sequence from presets...")
    # Implement placeholder body for the generate_sequence_from_presets function
    sequence = []
    for chord in chord_progression['chords']:
        # Generate all notes in the chord (not just the root)
        chord_notes = [Note(note_name=note) for note in chord['notes']]
        sequence.extend(chord_notes)
    logger.debug(f"Generated sequence: {sequence}")
    logger.info(f"Generated notes: {[note.note_name for note in sequence]}")
    logger.debug(f"Generated notes: {[note.note_name for note in sequence]}")  
    logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence]}")
    return NoteSequence(notes=sequence)

class NoteSequenceGenerator(BaseModel):
    """Generator for creating note sequences from chord progressions and rhythm patterns."""
    
    chord_progression: ChordProgression = Field(...)
    note_pattern: NotePattern = Field(...)
    rhythm_pattern: RhythmPattern = Field(...)

    async def generate_sequence_from_presets(
        progression_name: str,
        note_pattern_name: str,
        rhythm_pattern_name: str,
        scale_info: ScaleInfo,
        chord_progression: Dict[str, Any],
        note_pattern: Dict[str, Any],
        rhythm_pattern: Dict[str, Any]
    ) -> NoteSequence:
        logger.debug("Generating sequence from presets...")
        
        # Retrieve the rhythm pattern
        logger.debug(f"Retrieving rhythm pattern for: {rhythm_pattern_name}")
        rhythm_pattern_instance = await self.get_rhythm_pattern(rhythm_pattern_name)
        if rhythm_pattern_instance is None:
            logger.error(f"Rhythm pattern '{rhythm_pattern_name}' not found.")
            raise ValueError(f"Rhythm pattern '{rhythm_pattern_name}' not found.")
    
        # Convert the rhythm pattern to a dictionary using model_dump
        rhythm_pattern_data = rhythm_pattern_instance.model_dump()
    
        sequence = []
        for chord in chord_progression['chords']:
            # Generate all notes in the chord (not just the root)
            chord_notes = [Note(note_name=note) for note in chord['notes']]
            sequence.extend(chord_notes)
        
        logger.debug(f"Generated sequence: {sequence}")
        logger.info(f"Generated notes: {[note.note_name for note in sequence]}")
        logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence]}")
        
        return NoteSequence(notes=sequence)

    async def get_note_pattern(self, note_pattern_name: str) -> NotePattern:
        # Placeholder logic to simulate retrieving a note pattern
        logger.debug(f"Retrieving note pattern for: {note_pattern_name}")
        return NotePattern(pattern=[0, 2, 4])  # Example pattern

    async def get_rhythm_pattern(self, rhythm_pattern_name: str) -> RhythmPattern:
        # Placeholder logic to simulate retrieving a rhythm pattern
        logger.debug(f"Retrieving rhythm pattern for: {rhythm_pattern_name}")
        return RhythmPattern(pattern=[1, 0, 1, 0])  # Example rhythm pattern

    async def generate_sequence_async(
        self,
        chord_progression: ChordProgression,
        note_pattern: NotePattern,
        rhythm_pattern: RhythmPattern,
        scale_info: ScaleInfo
    ) -> NoteSequence:
        try:
            logger.debug("Generating sequence asynchronously...")        

            try:
                print(f"Rhythm pattern before processing: {rhythm_pattern}")
                print(f"Chord progression: {chord_progression.chords}")

                if isinstance(rhythm_pattern, str):
                    print(f"Converting rhythm_pattern from string to RhythmPattern using from_str.")
                    rhythm_pattern = RhythmPattern.from_str(rhythm_pattern)

                logger.debug(f"Rhythm pattern before validation: {rhythm_pattern}")  # Log the rhythm pattern being validated
                logger.debug(f"Type of rhythm pattern: {type(rhythm_pattern)}")  # Log the type of rhythm pattern
                logger.debug(f"Rhythm pattern attributes before validation: {rhythm_pattern.pattern}")
                logger.debug(f"Rhythm pattern data: {rhythm_pattern.data}")
                logger.debug(f"Rhythm pattern attributes: {rhythm_pattern.pattern}")  # Log the pattern attribute
                logger.debug(f"Rhythm pattern pattern length: {len(rhythm_pattern.pattern)}")  # Log the length of the pattern
                logger.debug(f"Rhythm pattern pattern type: {type(rhythm_pattern.pattern)}")  # Log the type of the pattern

                if rhythm_pattern is None:
                    raise ValueError("Rhythm pattern cannot be None")
                if rhythm_pattern.pattern is None:
                    raise ValueError("Rhythm pattern must have a valid pattern")

                print(f"Number of notes to generate: {len(rhythm_pattern.pattern)}")
                print(f"Chord progression details: {chord_progression}")

                sequence = []  # Initialize the sequence
                generated_notes = []
                for chord in chord_progression.chords:
                    # Ensure we use the scale from the chord progression
                    scale = Scale(root=chord_progression.scale_info.root, scale_type=chord_progression.scale_type)  # Use scale from chord progression
                    scaleNotes = scale.notes  # Get the notes from the scale
                    logger.debug(f"Scale notes: {scaleNotes}")  # Log the generated scale notes
                    rootIndex = next((i for i, note in enumerate(scaleNotes) if note.note_name == chord.root.note_name), None)
                    if rootIndex is None:
                        raise ValueError(f"Chord root {chord.root} not found in scale notes.")  # Current chord root index
                    logger.debug(f"Root index: {rootIndex}")

                    chordDuration = chord.duration 
                    print(f"Chord Duration: {chordDuration} seconds")
                    logger.debug(f"Chord Duration: {chordDuration}")  # Log the chord duration

                    patternNoteCount = len(rhythm_pattern.pattern)  
                    print(f"Number of rhythm notes: {patternNoteCount}")

                    patternDuration = rhythm_pattern.pattern[0]  # Use the first value of the rhythm pattern as duration
                    if patternDuration == 0:
                        raise ValueError("Pattern duration cannot be zero.")  # Raise an error if patternDuration is zero
                    print(f"Pattern Duration: {patternDuration}")
                    logger.debug(f"Pattern Duration: {patternDuration}")  # Log the pattern duration

                    howManyNotes = int(chordDuration / patternDuration)
                    print(f"Number of howManyNotes: {howManyNotes}")

                    current_index = 0  # Initialize the index for the note pattern
                    logger.debug(f"Note pattern content: {note_pattern.pattern}")
                    for _ in range(howManyNotes):
                        print(f"how many notes current note: {_}")
                        
                        offset = note_pattern.pattern[current_index]  # Offset from note pattern
                        logger.debug(f"Note pattern offset eeeee: {offset}")
                        new_index = (rootIndex + offset) % len(scaleNotes)  # Calculate new index based on offset
                        logger.debug(f"New index after applying offset fffff: {new_index}")
                        logger.debug(f"Scale notes hhhhh: {scaleNotes}")  # Log the generated scale notes
                        note = scaleNotes[new_index]  # Retrieve note from scale
                        note.octave = chord.root.octave  # Adjust the octave based on the chord's octave
                        logger.debug(f"Adjusted note: {note.note_name} with octave: {note.octave}")
                   
                        logger.debug(f"new note = scaleNotes[new_index] {new_index} ?? ggggg: {note}")
                        
                        if note:
                            sequence.append(note)
                            generated_notes.append(note)
                        else:
                            logger.warning(f"No note found for offset {offset} at index {new_index}.")
                        
                        logger.debug(f"Chord root: {chord.root.note_name}, Index in scale: {rootIndex}")
                        logger.debug(f"Offset from note pattern: {offset}")
                        logger.debug(f"New index after applying offset: {new_index}")
                        logger.debug(f"Generated note: {note.note_name} at index {new_index}")
                        
                        current_index += 1  # Move to the next note in the pattern
                        if current_index >= len(note_pattern.pattern):  # Reset if at the end of the pattern
                            current_index = 0


                for note in generated_notes:
                    if note.note_name not in [scale_note.note_name for scale_note in scaleNotes]:
                        raise ValueError(f"Note {note} not found in scale notes.")
                for note in generated_notes:
                    if note.note_name.split('-')[0] not in [scale_note.note_name.split('-')[0] for scale_note in scaleNotes]:
                        raise ValueError(f"Note {note} not found in scale notes.")

                logger.info(f"Generated sequence: {NoteSequence(notes=sequence).model_dump_json()}")
                logger.info(f"Generated notes: {[note.note_name for note in sequence]}")
                logger.debug(f"Generated notes: {[note.note_name for note in sequence]}")  
                logger.info(f"Generated notes before returning: {[note.note_name for note in sequence]}")
                logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence]}")
                logger.info(f"Generated notes before returning: {[note.note_name for note in sequence]}") # Added this line
                logger.info(f"Generated notes before returning: {[note.note_name for note in sequence]}") # Added this line
                logger.debug(f"Generated notes: {[note.note_name for note in generated_notes]}")
                logger.debug(f"Generated notes: {[note.note_name for note in generated_notes]}") # Added this line
                print(f"Generated notes: {[note.note_name for note in generated_notes]}") # Added this line
                print(f"Generated notes: {[note.note_name for note in generated_notes]}") # Added this line
                logger.debug(f"Generated notes structure: {[{'name': note.note_name, 'octave': note.octave} for note in generated_notes]}")
                logger.debug(f"Generated notes: {[note.note_name for note in generated_notes]}")
                return NoteSequence(notes=generated_notes, is_test=False)
            except Exception as e:
                logger.error(f"Error in generate_sequence_async inner try: {str(e)}", exc_info=True)
                raise
        except Exception as e:
            logger.error(f"Error in generate_sequence_async: {str(e)}", exc_info=True)
            raise
        finally:
            logger.debug("generate_sequence_async function execution completed.")

    async def generate_sequence(self, chord_progression: ChordProgression, note_pattern: NotePattern, rhythm_pattern: RhythmPattern, scale_info: ScaleInfo) -> List[Note]:
        logger.debug("Generating sequence asynchronously...")
        note_sequence = await self.generate_sequence_async(
            chord_progression,
            note_pattern,
            rhythm_pattern,
            scale_info
        )
        return NoteSequence(notes=note_sequence.notes)  # Return the list of notes from the NoteSequence

    def _generate_basic_sequence(self) -> List[Note]:
        """Generate a basic sequence without rhythm pattern."""
        logger.debug("Generating basic sequence...")
        sequence = []  # Initialize an empty sequence
        for chord in self.chord_progression.chords:
            # Generate all notes in the chord (not just the root)
            chord_notes = [Note(note_name=note.note_name, octave=chord.root.octave) for note in chord.notes]
            sequence.extend(chord_notes)
        logger.debug(f"Generated basic sequence: {sequence}")
        return sequence

    def _generate_rhythmic_sequence(self) -> List[Note]:
        """Generate a sequence using the rhythm pattern."""
        logger.debug("Generating rhythmic sequence...")
        sequence = []  # Initialize an empty sequence
        for chord in self.chord_progression.chords:
            # Ensure we use the scale from the chord progression
            scale = Scale(root=self.chord_progression.scale_info.root, scale_type=self.chord_progression.scale_type)  # Use scale from chord progression
            scaleNotes = scale.notes  # Get the notes from the scale

            # Generate notes based on the rhythm pattern
            for rhythm_note in self.rhythm_pattern.data.notes:
                # Calculate the index based on the chord root and rhythm pattern
                rootIndex = next((i for i, note in enumerate(scaleNotes) if note.note_name == chord.root.note_name), None)
                if rootIndex is None:
                    raise ValueError(f"Chord root {chord.root} not found in scale notes.")
                new_index = (rootIndex + rhythm_note.pitch) % len(scaleNotes)  

                note = scaleNotes[new_index]  # Retrieve note from scale
                sequence.append(note)  # Append the note to the sequence

        logger.debug(f"Generated rhythmic sequence: {sequence}")
        return sequence

    def get_root_note_from_chord(self, chord: Chord) -> Optional[Note]:
        """Get the root note from a chord."""
        try:
            if hasattr(chord, 'root') and isinstance(chord.root, Note):
                return chord.root
            logger.debug("No root note found")
            return None
        except Exception as e:
            logger.error(f"Error getting root note from chord: {str(e)}", exc_info=True)
            raise
    
    def set_rhythm_pattern(self, pattern: RhythmPattern) -> None:
        """Set a new rhythm pattern."""
        try:
            logger.info(f"Setting rhythm pattern: {pattern.model_dump_json()}")
            self.rhythm_pattern = pattern
        except Exception as e:
            logger.error(f"Error setting rhythm pattern: {str(e)}", exc_info=True)
            raise
    
    def set_chord_progression(self, progression: ChordProgression) -> None:
        """Set a new chord progression."""
        try:
            logger.info(f"Setting chord progression: {progression.model_dump_json()}")
            self.chord_progression = progression
        except Exception as e:
            logger.error(f"Error setting chord progression: {str(e)}", exc_info=True)
            raise

class ChordProgression(BaseModel):
    name: str
    key: str
    scale_type: ScaleType
    scale_info: ScaleInfo
    chords: List[Chord]
    complexity: float = 0.0
    description: str = ''