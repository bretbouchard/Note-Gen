from src.note_gen.models.note import Note
import traceback

def test_create_note(note_name, octave):
    print(f"\nTesting Note creation with note_name='{note_name}', octave={octave}")
    try:
        note = Note(note_name=note_name, octave=octave, duration=1, velocity=64, position=0.0)
        print(f"Success! Created note: {note}")
        return True
    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        traceback.print_exc()
        return False

# Test valid note
test_create_note("C", 4)

# Test invalid note name
test_create_note("Invalid", 4)

# Test invalid octave
test_create_note("C", 10)
test_create_note("C", -1)

# Test invalid octave type
test_create_note("C", "not_a_number")
