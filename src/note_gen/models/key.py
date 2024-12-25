from typing import List
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.scale_info import ScaleInfo


class Key:
    def __init__(self, *, root: Note) -> None:
        self.root = root
        self.scale_info = ScaleInfo(root=root)  # Pass the root note to ScaleInfo

    def get_scale_notes(self) -> List[Note]:
        """Get the notes of the scale in this key."""
        scale_intervals = self.scale_info.intervals
        scale_notes = []
        current_note = self.root

        for interval in scale_intervals:
            scale_notes.append(current_note)
            current_note = Note.from_midi(current_note.midi_number + interval)

        return scale_notes
