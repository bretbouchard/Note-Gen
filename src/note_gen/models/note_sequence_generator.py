from typing import List, Optional
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.rhythm_pattern import RhythmPattern
from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale, ScaleType

class NoteSequenceGenerator:
    """Generates a sequence of notes based on a chord progression, note sequence, and rhythm sequence."""

    def __init__(self, chord_progression: ChordProgression, note_sequence: NoteSequence, rhythm_sequence: RhythmPattern, key_scale: Optional[str] = "C Major") -> None:
        self.chord_progression = chord_progression
        self.note_sequence = note_sequence
        self.rhythm_sequence = rhythm_sequence
        self.key_scale = ScaleType(key_scale) if key_scale else None  # Convert key_scale to ScaleType before storing

    def generate_sequence(self) -> List[Note]:
        """Generate a sequence of notes based on the provided inputs."""
        generated_notes: List[Note] = []
        for i, chord in enumerate(self.chord_progression.get_all_chords()):
            root_note = self.get_root_note_from_chord(chord)
            chord_quality = chord.chord.quality  # Access quality from the Chord instance
            rhythm_note = self.rhythm_sequence.data[i % len(self.rhythm_sequence.data)]  # Get the corresponding rhythm note
            duration = rhythm_note.duration  # Use the duration from the rhythm note
            generated_notes.append(Note(pitch=root_note, duration=duration))
            print(f"Generated note: {root_note} with duration: {duration} for chord: {chord}")
        return generated_notes

    def get_root_note_from_chord(self, chord) -> Note:
        """Determine the root note based on the current chord and key/scale."""
        root = chord.root
        if root is None:
            raise ValueError("The root note cannot be None.")
        if self.key_scale is None:
            raise ValueError("scale_type cannot be None")
        scale = Scale(root=root, scale_type=self.key_scale)
        scale_notes = scale.get_notes()  # Get the notes of the scale
        root_note = scale_notes[chord.chord.quality - 1]  # Assuming chord.quality corresponds to scale degree
        print(f"Determined root note: {root_note} for chord: {chord}")
        return Note(pitch=root_note)
