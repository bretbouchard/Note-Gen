from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, validator
import logging
import os

# Set up logging configuration
log_file_path = os.path.join(os.path.dirname(__file__), '../../logs/app.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Log to specified file
        logging.StreamHandler()  # Also log to console
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
logger.propagate = True

async def generate_sequence_from_presets(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
    chord_progression: Dict[str, Any],
    note_pattern: Dict[str, Any],
    rhythm_pattern: Dict[str, Any]
) -> NoteSequence:
    """
    Generate a note sequence from presets.
    """
    try:
        logger.info(f"Generating sequence with scale_info: {scale_info.model_dump_json()}")
        # For Simple Triad pattern, generate notes based on the scale root
        root_note = scale_info.root
        
        # Calculate notes for the Simple Triad pattern (root, second, third)
        second_semitones = 2  # Whole step
        third_semitones = 4 if scale_info.scale_type == ScaleType.MAJOR else 3  # Major third (4) or minor third (3)
        
        root_midi = root_note.midi_number
        second_midi = root_midi + second_semitones
        third_midi = root_midi + third_semitones
        
        root = Note.from_midi(root_midi, velocity=64, duration=1)
        second = Note.from_midi(second_midi, velocity=64, duration=1)
        third = Note.from_midi(third_midi, velocity=64, duration=1)
        
        # Create a sequence with these notes
        sequence = NoteSequence(notes=[root, second, third])
        logger.debug(f"Generated sequence: {sequence.model_dump_json()}")
        
        return sequence
    except Exception as e:
        logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
        raise

class NoteSequenceGenerator(BaseModel):
    """Generator for creating note sequences from chord progressions and rhythm patterns."""
    
    chord_progression: ChordProgression = Field(...)
    note_pattern: NotePattern = Field(...)
    rhythm_pattern: RhythmPattern = Field(...)

    async def generate_sequence_from_presets(
        self,
        progression_name: str,
        note_pattern_name: str,
        rhythm_pattern_name: str,
        scale_info: ScaleInfo
    ) -> NoteSequence:
        # Create a ChordProgression instance directly
        chord_progression = ChordProgression(name=progression_name)  # Assuming ChordProgression can be initialized this way

        # Get other required components (note pattern, rhythm pattern)
        note_pattern = await self.get_note_pattern(note_pattern_name)
        rhythm_pattern = await self.get_rhythm_pattern(rhythm_pattern_name)

        # Generate the sequence using the retrieved components
        return await self.generate_sequence_async(
            chord_progression=chord_progression,
            note_pattern=note_pattern,
            rhythm_pattern=rhythm_pattern,
            scale_info=scale_info
        )

    async def get_note_pattern(self, note_pattern_name: str) -> NotePattern:
        # Implement logic to get note pattern from note_pattern_name
        pass

    async def get_rhythm_pattern(self, rhythm_pattern_name: str) -> RhythmPattern:
        # Logic to retrieve rhythm pattern from the name
        rhythm_patterns = {
            "pattern1": RhythmPattern(
                name="pattern1",
                data=RhythmPatternData(
                    notes=[RhythmNote(position=0, duration=1.0, velocity=100, is_rest=False)],
                    time_signature="4/4"
                ),
                description="Dummy rhythm pattern",
                tags=["test"],
                complexity=1.0,
                style="basic"
            ),
            "pattern2": RhythmPattern(
                name="pattern2",
                data=RhythmPatternData(
                    notes=[RhythmNote(position=0, duration=0.5, velocity=100, is_rest=False)],
                    time_signature="3/4"
                ),
                description="Another dummy rhythm pattern",
                tags=["test"],
                complexity=1.5,
                style="complex"
            )
        }
        logger.info(f"Retrieving rhythm pattern for name: {rhythm_pattern_name}")
        retrieved_rhythm_pattern = rhythm_patterns.get(rhythm_pattern_name, None)
        logger.info(f"Retrieved rhythm pattern: {retrieved_rhythm_pattern}")
        return retrieved_rhythm_pattern

    async def generate_sequence_async(
        self,
        chord_progression: ChordProgression,
        note_pattern: NotePattern,
        rhythm_pattern: Dict[str, Any],
        scale_info: ScaleInfo
    ) -> NoteSequence:
        try:
            logger.info(f"Received rhythm_pattern of type: {type(rhythm_pattern)}")
            print(f"Rhythm pattern before processing: {rhythm_pattern}")
            print(f"Chord progression: {chord_progression.chords}")

            if isinstance(rhythm_pattern, str):
                print(f"Converting rhythm_pattern from string to RhythmPattern using from_str.")
                rhythm_pattern = RhythmPattern.from_str(rhythm_pattern)

            if rhythm_pattern is None:
                print("Rhythm pattern is None after conversion.")
            if not rhythm_pattern.data.notes:
                print("Rhythm pattern has no notes.")

            print(f"Number of notes to generate: {len(rhythm_pattern.data.notes)}")
            print(f"Chord progression details: {chord_progression}")

            sequence = []  # Initialize the sequence
            for chord in chord_progression.chords:
                scale = Scale(root=chord.root, scale_type=scale_info.scale_type)
                notes = []  # Initialize notes for this chord

                chordDuration = chord.duration 
                print(f"Chord Duration: {chordDuration}")

                patternNoteCount = len(rhythm_pattern.data.notes)  
                print(f"Number of rhythm notes: {patternNoteCount}")

                patternDuration = rhythm_pattern.data.calculate_total_duration()
                print(f"Pattern Duration: {patternDuration}")

                howManyNotes = int(chordDuration / (patternDuration * patternNoteCount))
                print(f"Number of howManyNotes: {howManyNotes}")
                scaleNotes = scale.notes  
                rootIndex = scaleNotes.index(chord.root)  


                current_index = 0  # Initialize the index for the note pattern
                for _ in range(howManyNotes):
                    print(f"how many notes current note: {_}")
                    
                    interval = note_pattern.pattern[current_index]  # Get the note based on the current index

                    print(f"note_pattern.pattern: {interval}")
                    print(f"Current index: {current_index}")
                    print(f"Retrieving note for interval: {interval}")


                    new_index = (rootIndex + interval) % len(scaleNotes)  
                    note = scaleNotes[new_index] 
  
                    if note:
                        notes.append(note)
                    else:
                        print(f"No note found for interval {interval}.")

                    current_index += 1  # Move to the next note in the pattern
                    if current_index >= len(note_pattern.pattern):  # Reset if at the end of the pattern
                        current_index = 0

                sequence.extend(notes)  # Add all generated notes for this chord to the sequence

            logger.info(f"Generated sequence: {NoteSequence(notes=sequence).model_dump_json()}")
            logger.info(f"Generated notes: {[note.note_name for note in sequence]}")
            logger.debug(f"Generated notes: {[note.note_name for note in sequence]}")  
            logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence]}")
            return NoteSequence(notes=sequence)

            sequence.extend(notes)  # Add all generated notes for this chord to the sequence

            logger.info(f"Generated sequence: {NoteSequence(notes=sequence).model_dump_json()}")
            logger.info(f"Generated notes: {[note.note_name for note in sequence]}")
            logger.debug(f"Generated notes: {[note.note_name for note in sequence]}")  
            logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence]}")
            return NoteSequence(notes=sequence)
        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
            raise
    
    async def generate_sequence(self) -> NoteSequence:
        """Generate a note sequence based on the chord progression and rhythm pattern."""
        try:
            logger.info("Starting note sequence generation.")
            note_sequence = await self.generate_sequence_async(
                chord_progression=self.chord_progression,
                note_pattern=self.note_pattern,
                rhythm_pattern=self.rhythm_pattern.model_dump_json(),
                scale_info=ScaleInfo(root=self.chord_progression.chords[0].root, scale_type=self.chord_progression.scale_type)
            )
            return note_sequence
        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
            raise
    
    def _generate_basic_sequence(self) -> List[Note]:
        """Generate a basic sequence without rhythm pattern."""
        try:
            sequence = []
            for chord in self.chord_progression.chords:
                # Generate all notes in the chord (not just the root)
                chord_notes = chord.generate_notes()
                sequence.extend(chord_notes)
            logger.debug(f"Generated basic sequence: {sequence}")
            logger.info(f"Generated notes: {[note.note_name for note in sequence]}")
            logger.debug(f"Generated notes: {[note.note_name for note in sequence]}")  
            logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence]}")
            return sequence
        except Exception as e:
            logger.error(f"Error generating basic sequence: {str(e)}", exc_info=True)
            raise
    
    def _generate_rhythmic_sequence(self) -> List[Note]:
        """Generate a sequence using the rhythm pattern."""
        try:
            if not self.rhythm_pattern:
                raise ValueError("Rhythm pattern is required for rhythmic sequence generation")
            
            sequence = []
            durations = self.rhythm_pattern.get_durations()
            chord_idx = 0
            
            for duration in durations:
                if chord_idx >= len(self.chord_progression.chords):
                    chord_idx = 0  # Loop back to start of progression
                    
                chord = self.chord_progression.chords[chord_idx]
                note = Note(
                    note_name=chord.root.note_name,
                    octave=chord.root.octave,
                    duration=duration,
                    velocity=chord.root.velocity
                )
                sequence.append(note)
                chord_idx += 1
                
            logger.debug(f"Generated rhythmic sequence: {sequence}")
            logger.info(f"Generated notes: {[note.note_name for note in sequence]}")
            logger.debug(f"Generated notes: {[note.note_name for note in sequence]}")  
            logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence]}")
            return sequence
        except Exception as e:
            logger.error(f"Error generating rhythmic sequence: {str(e)}", exc_info=True)
            raise
    
    async def generate_sequence(self, note_length: float = 1.0, chord_length: float = 1.0) -> NoteSequence:
        """Generate a note sequence based on the chord progression and rhythm pattern."""
        try:
            logger.info(f"Starting note generation with note_length: {note_length}, chord_length: {chord_length}")
            
            sequence = []
            total_notes = 0
            
            logger.debug(f"Chord progression: {self.chord_progression.chords}")
            logger.debug(f"Rhythm pattern: {self.rhythm_pattern}")
            logger.debug(f"Chord progression details: {self.chord_progression.model_dump_json()}")
            logger.debug(f"Rhythm pattern details: {self.rhythm_pattern.model_dump_json()}")
            
            for chord in self.chord_progression.chords:
                
                logger.debug(f"Processing chord: {chord.root.note_name} {chord.root.octave}")
                logger.debug(f"Chord duration: {chord.duration}")
                logger.debug(f"Chord length: {chord_length}, Note length: {note_length}")
                
                expected_notes = int(chord.duration / note_length)
                
                logger.debug(f"Expected notes for chord: {expected_notes}")
                
                for _ in range(expected_notes):
                    note = Note(
                        note_name=chord.root.note_name,
                        octave=chord.root.octave,
                        duration=note_length,
                        velocity=chord.root.velocity
                    )
                    logger.debug(f"Generated note: {note.note_name} {note.octave} (duration: {note.duration}, velocity: {note.velocity})")
                    
                    sequence.append(note)
                    total_notes += 1
                    
                    logger.debug(f"Total notes generated so far: {total_notes}")
            
            logger.info(f"Generated sequence: {NoteSequence(notes=sequence).model_dump_json()}")
            logger.info(f"Generated notes: {[note.note_name for note in sequence]}")
            logger.debug(f"Generated notes: {[note.note_name for note in sequence]}")  
            logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence]}")
            logger.info(f"Total notes generated: {total_notes}")
            logger.info(f"Generated notes: {[note.note_name for note in sequence]}")  
            return NoteSequence(notes=sequence)
        
        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
            raise
    
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

    async def generate_sequence_from_presets(
        self,
        progression_name: str,
        note_pattern_name: str,
        rhythm_pattern_name: str,
        scale_info: ScaleInfo,
        chord_progression: ChordProgression,
        note_pattern: dict,
        rhythm_pattern: dict,
    ) -> NoteSequence:
        """
        Generate a note sequence from presets.
        """
        try:
            logger.info(f"Generating sequence with scale_info: {scale_info.model_dump_json()}")
            
            if not chord_progression.chords:
                raise ValueError("Chord progression has no chords")
            
            sequence = NoteSequence(notes=[])
            root_note = scale_info.root
            scale = Scale.from_root_and_type(root_note, scale_info.scale_type)
            
            # Apply note pattern to each chord in the progression
            for chord in chord_progression.chords:
                logger.debug(f"Processing chord: {chord.root.note_name} {chord.root.octave}")
                logger.debug(f"Chord duration: {chord.duration}")
                # Get the scale degree for this chord
                scale_degree = scale.get_degree_of_note(chord.root)
                # Get the root note for this chord
                chord_root = scale.get_note_at_scale_degree(scale_degree)
                
                print(f"Generating notes for chord: {chord.root.note_name}")
                print(f"Intervals used: {note_pattern['pattern']}")
                
                print(f"Starting note generation for chord: {chord.root.note_name}, Scale Type: {scale_info.scale_type}")
                print(f"Using note pattern: {note_pattern['pattern']}")
                print(f"Generating notes for chord: {chord.root.note_name}")
                print(f"Using note pattern intervals: {note_pattern['pattern']}")
                print(f"Scale degrees: {[scale.get_note_at_degree(degree).note_name for degree in note_pattern['pattern']]}")
                # Apply the note pattern relative to the chord root
                expected_notes = len(note_pattern["pattern"])
                notes = []
                logger.debug(f"Chord root: {chord.root.note_name}, Chord index: {chord_index}, Intervals: {note_pattern['pattern']}")

                for interval in note_pattern["pattern"]:
                    chord_index = scale.notes.index(chord.root)
                    logger.debug(f"Applying interval: {interval} from chord root index: {chord_index}")
                    chord_root_midi = chord.root.midi_number
                    note_midi = scale.get_note_at_degree(chord_index + interval).midi_number
                    expected_note = scale.get_note_at_degree(interval).note_name
                    logger.info(f"Chord root MIDI: {chord_root_midi}, Interval: {interval}, Expected note: {expected_note}, Generated note MIDI: {note_midi}")
                    logger.debug(f"Chord root index: {chord_index}, Interval: {interval}, Expected note: {expected_note}, Generated note MIDI: {note_midi}")
                    logger.info(f"Expected notes 1: {[scale.get_note_at_degree(interval).note_name for interval in note_pattern['pattern']]}")
                    logger.info(f"Final generated sequence: {[note.note_name for note in sequence.notes]}")
                    
                    notes.append(Note.from_midi(note_midi, velocity=root_note.velocity, duration=root_note.duration))
                    print(f"Generated note: {Note.from_midi(note_midi, velocity=root_note.velocity, duration=root_note.duration).note_name} (MIDI: {note_midi})")
                    logger.info(f"Chord root MIDI: {chord_root_midi}, Interval: {interval}, Expected note: {expected_note}, Generated note MIDI: {note_midi}")
                    logger.info(f"Chord root MIDI: {chord_root_midi}, Interval: {interval}, Expected note: {expected_note}, Generated note MIDI: {note_midi}")
                    
                    logger.info(f"Expected notes 2: {[scale.get_note_at_degree(interval).note_name for interval in note_pattern['pattern']]}")
                    logger.info(f"Total notes generated so far: {len(notes)}")
                    print(f"Generated notes so far: {[note.note_name for note in notes]}")
                    logger.info(f"Generated notes for chord: {chord.root.note_name}")
                    logger.info(f"Generated notes: {[note.note_name for note in notes]}")
                    logger.debug(f"Generated notes: {[note.note_name for note in notes]}")  
                    logger.debug(f"Generated notes before returning: {[note.note_name for note in notes]}")
                    logger.info(f"Scale degrees used: {[scale.get_degree_of_note(note) for note in notes]}")
                    # Check if we have reached the expected number of notes
                    if len(notes) >= expected_notes:
                        break
                logger.info(f"Expected notes 3: {[scale.get_note_at_degree(interval).note_name for interval in note_pattern['pattern']]}")
                logger.info(f"Generated notes for chord: {chord.root.note_name}")
                logger.info(f"Generated notes: {[note.note_name for note in notes]}")
                logger.debug(f"Generated notes: {[note.note_name for note in notes]}")  
                logger.debug(f"Generated notes before returning: {[note.note_name for note in notes]}")
                logger.info(f"Scale degrees used: {[scale.get_degree_of_note(note) for note in notes]}")
                logger.info(f"Final generated sequence: {[note.note_name for note in sequence.notes]}")

                sequence.notes.extend(notes)
            
            logger.info(f"Final generated sequence: {[note.note_name for note in sequence.notes]}")
            logger.info(f"Generated sequence: {sequence.model_dump_json()}")
            logger.info(f"Generated notes: {[note.note_name for note in sequence.notes]}")
            logger.debug(f"Generated notes: {[note.note_name for note in sequence.notes]}")  
            logger.debug(f"Generated notes before returning: {[note.note_name for note in sequence.notes]}")
            logger.info(f"Total notes generated: {len(sequence.notes)}")
            logger.info(f"Generated notes: {[note.note_name for note in sequence.notes]}")  
            print(f"Generated Note Pattern: {[note.note_name for note in sequence.notes]}")  
            return sequence
        except Exception as e:
            logger.error(f"Error generating sequence from presets: {str(e)}", exc_info=True)
            raise

    async def generate_sequence(self) -> NoteSequence:
        """Generate a note sequence based on the chord progression and rhythm pattern."""
        try:
            logger.info("Starting note sequence generation.")
            note_sequence = await self.generate_sequence_async(
                chord_progression=self.chord_progression,
                note_pattern=self.note_pattern,
                rhythm_pattern=self.rhythm_pattern.model_dump_json(),
                scale_info=ScaleInfo(root=self.chord_progression.chords[0].root, scale_type=self.chord_progression.scale_type)
            )
            return note_sequence
        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
            raise