import unittest
from note_gen.models.chord import Chord
from note_gen.models.note import Note
from note_gen.core.enums import ChordQuality

class TestChord(unittest.TestCase):
    def test_enharmonic_equivalence(self):
        """Test that chords with enharmonically equivalent roots are handled correctly."""
        # Create notes with enharmonic equivalence
        note1 = Note(pitch="C#", octave=4)
        note2 = Note(pitch="Db", octave=4)

        # Verify they have the same MIDI number
        self.assertEqual(note1.midi_number, note2.midi_number)

        # Test that they are considered enharmonically equivalent
        self.assertEqual(note1.get_enharmonic().pitch, "Db")
        self.assertEqual(note2.get_enharmonic().pitch, "C#")

        # Create chords using the pitch strings
        chord1 = Chord(root=note1.pitch, quality=ChordQuality.MAJOR)
        chord2 = Chord(root=note2.pitch, quality=ChordQuality.MAJOR)

        # Generate notes for both chords
        notes1 = chord1.get_notes()
        notes2 = chord2.get_notes()

        # Test that the chords have equivalent root notes
        self.assertEqual(notes1[0].midi_number, notes2[0].midi_number)

        # Test that all notes in both chords have the same MIDI numbers
        for n1, n2 in zip(notes1, notes2):
            self.assertEqual(n1.midi_number, n2.midi_number)
