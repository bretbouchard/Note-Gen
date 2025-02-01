from src.note_gen.models.enums import ChordQualityType

def test_chord_quality_print():
    """Test to print all members of ChordQualityType and their string representations."""
    for quality in ChordQualityType:
        print(f"Quality: {quality}, Value: {quality.value}, Type: {type(quality.value)}")
