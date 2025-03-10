from typing import List, Optional, Dict, Union
from pydantic import BaseModel, field_validator, model_validator
import logging

from src.note_gen.models.note import Note
from src.note_gen.models.enums import ScaleType

logger = logging.getLogger(__name__)

class Scale(BaseModel):
    scale_type: ScaleType
    root: Note
    notes: Optional[List[Note]] = None

    # Comprehensive scale intervals dictionary
    SCALE_INTERVALS: Dict[ScaleType, List[int]] = {
        ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11],
        ScaleType.MINOR: [0, 2, 3, 5, 7, 8, 10],
        ScaleType.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
        ScaleType.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11],
        ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
        ScaleType.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
        ScaleType.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
        ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
        ScaleType.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
        ScaleType.CHROMATIC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        ScaleType.MAJOR_PENTATONIC: [0, 2, 4, 7, 9],
        ScaleType.MINOR_PENTATONIC: [0, 3, 5, 7, 10],
        ScaleType.HARMONIC_MAJOR: [0, 2, 4, 5, 7, 8, 11],
        ScaleType.MELODIC_MAJOR: [0, 2, 4, 5, 7, 8, 10],
        ScaleType.DOUBLE_HARMONIC_MAJOR: [0, 1, 4, 5, 7, 8, 11]
    }

    @model_validator(mode='before')
    @classmethod
    def validate_input_types(cls, values: dict) -> dict:
        """
        Validate input types before model creation.
        Ensures all critical fields are of the correct type and not None.
        """
        # Check for None values in critical fields
        if values.get('root') is None:
            raise ValueError("Root note cannot be None")
        if values.get('scale_type') is None:
            raise ValueError("Scale type cannot be None")
        
        # Ensure root is a Note instance
        if not isinstance(values['root'], Note):
            raise TypeError("root must be a Note instance")
        
        # Ensure scale_type is a valid ScaleType
        if not isinstance(values['scale_type'], ScaleType):
            try:
                values['scale_type'] = ScaleType(values['scale_type'])
            except (TypeError, ValueError):
                raise ValueError(f"Unsupported scale type: {values['scale_type']}")
        
        return values

    @model_validator(mode='after')
    def generate_notes(self) -> List[Note]:
        """
        Generate notes for the scale after validation.
        Ensures notes are generated automatically upon initialization.
        """
        if not self.root:
            raise ValueError("Root note cannot be None.")
        if self.scale_type is None:
            raise ValueError("Scale type cannot be None.")

        # Only generate notes if they are not already provided
        if not self.notes:
            logger.info(f"Generating notes for {self.root} {self.scale_type} scale")
            self.notes = self._generate_scale_notes()

        return self.notes

    def _generate_scale_notes(self) -> List[Note]:
        """
        Generate all notes in the scale.
        
        Returns:
            List[Note]: List of notes in the scale
            
        Raises:
            ValueError: If any note in the scale would be outside valid MIDI range (0-127)
        """
        if not self.root:
            raise ValueError("Root note cannot be None.")
        if self.scale_type is None:
            raise ValueError("Scale type cannot be None.")

        # Get intervals for the specific scale type
        intervals = self.calculate_intervals()
        root_midi = self.root.midi_number
        notes = []

        # Start with the root note
        notes.append(self.root)
        logger.debug(f"Starting note generation with root: {self.root.note_name}{self.root.octave}")

        for interval in intervals[1:]:  # Skip the first interval (0) as it's the root
            try:
                # Create a new note for each interval
                note = Note.from_midi(
                    midi_number=root_midi + interval,
                    duration=self.root.duration,
                    velocity=self.root.velocity
                )
                notes.append(note)
                logger.debug(f"Generated note: {note.note_name}{note.octave} (MIDI: {root_midi + interval})")
            except ValueError as e:
                # Provide a more helpful error message
                raise ValueError(
                    f"Cannot generate {self.scale_type} scale: note at interval {interval} "
                    f"from root {self.root.note_name}{self.root.octave} "
                    f"would be outside valid MIDI range (0-127). "
                    f"Try using a different octave for the root note."
                ) from e
        
        logger.debug(f"Generated Scale notes before deduplication: {[note.note_name + str(note.octave) for note in notes]}")
        return notes

    def get_degree_number(self, note: Union[int, 'Note']) -> int:
        """
        Get the scale degree number (1-based index) for a given note.

        Args:
            note: Either a scale degree (int) or a Note object

        Returns:
            int: The scale degree number (1-based index)

        Raises:
            ValueError: If the note is not in scale or invalid type
        """
        if isinstance(note, int):
            if 1 <= note <= len(self.notes):
                return note
            raise ValueError(f'Invalid scale degree: {note}')

        if not isinstance(note, Note):
            raise TypeError(f'Expected int or Note, got {type(note)}')

        if not self.notes:
            self.notes = self._generate_scale_notes()

        try:
            return self.notes.index(note) + 1
        except ValueError:
            raise ValueError(f'Note {note} is not in scale')

    def get_scale_degree(self, degree: int) -> Note:
        """
        Get the note at a specific scale degree (1-based indexing).

        Args:
            degree: The scale degree (1-based indexing)

        Returns:
            Note: The note at the specified scale degree

        Raises:
            ValueError: If the degree is not valid for this scale
        """
        if not self.notes:
            self.notes = self._generate_scale_notes()

        if not isinstance(degree, int):
            try:
                degree = int(degree)
            except (TypeError, ValueError):
                raise ValueError(f'Invalid degree type: {type(degree)}')

        scale_length = len(self.calculate_intervals())
        if not 1 <= degree <= scale_length:
            raise ValueError(f'Scale degree must be between 1 and {scale_length}')

        return self.notes[degree - 1]

    def get_triad(self, degree: int) -> List[Note]:
        """
        Get a triad starting at the given scale degree (1-based indexing).
        
        Args:
            degree: The scale degree (1-based indexing)
            
        Returns:
            List[Note]: Three notes forming the triad
            
        Raises:
            ValueError: If the degree is not valid for this scale
        """
        if not self.notes:
            self.notes = self._generate_scale_notes()
        
        # Validate degree
        if not isinstance(degree, int):
            try:
                degree = int(degree)
            except (TypeError, ValueError):
                raise ValueError(f"Invalid degree type: {type(degree)}")

        # Get the number of unique notes in the scale
        scale_length = len(self.calculate_intervals())
        
        if not 1 <= degree <= scale_length:
            raise ValueError(f"Scale degree must be between 1 and {scale_length}")
        
        # Get notes at positions 1, 3, and 5 relative to the degree
        positions = [degree - 1, degree + 1, degree + 3]
        if any(pos >= scale_length for pos in positions):
            raise ValueError(f"Cannot build triad at degree {degree} - would exceed scale length")
        
        return [self.notes[pos] for pos in positions]

    def transpose(self, semitones: int) -> 'Scale':
        """
        Transpose the scale by a number of semitones.
        
        Args:
            semitones: Number of semitones to transpose
            
        Returns:
            Scale: A new Scale instance with transposed root
        """
        if not isinstance(semitones, int):
            try:
                semitones = int(semitones)
            except (TypeError, ValueError):
                raise ValueError(f"Invalid semitones type: {type(semitones)}")
        
        new_root = self.root.transpose(semitones)
        return Scale(root=new_root, scale_type=self.scale_type)

    def get_degree_of_note(self, note: Note) -> int:
        """
        Get the scale degree of a note within the scale.
        
        Args:
            note: The note to find the degree for.
            
        Returns:
            int: The scale degree (1-based indexing).
            
        Raises:
            ValueError: If the note is not in the scale.
        """
        if self.notes is not None and isinstance(self.notes, list) and note in self.notes:
            return self.notes.index(note) + 1  # 1-based indexing
        else:
            raise ValueError(f"{note} is not in the scale.")

    def get_note_by_degree(self, degree: int) -> Note:
        """
        Get a note at a specific scale degree (1-based indexing).
        
        Args:
            degree: The scale degree (1-based indexing).
            
        Returns:
            Note: The note at the specified scale degree.
            
        Raises:
            ValueError: If the degree is not valid for this scale.
        """
        if self.notes is not None and isinstance(self.notes, list):
            if degree < 1 or degree > len(self.notes):
                raise ValueError(f"Degree {degree} is out of range for this scale.")
            return self.notes[degree - 1]  # Convert to 0-based indexing
        else:
            raise ValueError("Notes have not been generated for this scale")

    def validate_scale(self, scale: 'Scale') -> None:
        if scale.notes is not None and isinstance(scale.notes, list):
            for note in scale.notes:
                # Process each note
                pass

    def another_scale_function(self) -> None:
        pass

    def calculate_intervals(self) -> List[int]:
        """
        Calculate intervals for the scale based on its type.
        
        Returns:
            List[int]: Intervals for the scale
            
        Raises:
            ValueError: If the scale type is not recognized
        """
        if self.scale_type is None:
            raise ValueError("Scale type cannot be None")

        try:
            intervals = self.SCALE_INTERVALS.get(self.scale_type)
            if intervals is None:
                raise ValueError(f"Unsupported scale type: {self.scale_type}")
            return intervals
        except Exception as e:
            logger.error(f"Error calculating intervals for scale type {self.scale_type}: {e}")
            raise