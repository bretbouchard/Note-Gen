E       For further information visit https://errors.pydantic.dev/2.10/v/missing
E   pattern
E     Input should be a valid list [type=list_type, input_value='1 1 1 1', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/list_type
E   duration
E     Extra inputs are not permitted [type=extra_forbidden, input_value=1.0, input_type=float]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   position
E     Extra inputs are not permitted [type=extra_forbidden, input_value=0.0, input_type=float]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   velocity
E     Extra inputs are not permitted [type=extra_forbidden, input_value=100, input_type=int]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   direction
E     Extra inputs are not permitted [type=extra_forbidden, input_value='up', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   use_chord_tones
E     Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   use_scale_mode
E     Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   arpeggio_mode
E     Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   restart_on_chord
E     Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   octave_range
E     Extra inputs are not permitted [type=extra_forbidden, input_value=[4, 5], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
_____________________________________________________________________ test_load_presets _____________________________________________________________________
tests/models/test_presets.py:48: in test_load_presets
    mock_load.return_value = [Presets()]
src/note_gen/models/presets.py:145: in <lambda>
    data=RhythmPatternData(
E   pydantic_core._pydantic_core.ValidationError: 12 validation errors for RhythmPatternData
E   notes
E     Field required [type=missing, input_value={'pattern': '1 1 1 1', 'd...'default_duration': 1.0}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.10/v/missing
E   time_signature
E     Field required [type=missing, input_value={'pattern': '1 1 1 1', 'd...'default_duration': 1.0}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.10/v/missing
E   pattern
E     Input should be a valid list [type=list_type, input_value='1 1 1 1', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/list_type
E   duration
E     Extra inputs are not permitted [type=extra_forbidden, input_value=1.0, input_type=float]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   position
E     Extra inputs are not permitted [type=extra_forbidden, input_value=0.0, input_type=float]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   velocity
E     Extra inputs are not permitted [type=extra_forbidden, input_value=100, input_type=int]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   direction
E     Extra inputs are not permitted [type=extra_forbidden, input_value='up', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   use_chord_tones
E     Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   use_scale_mode
E     Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   arpeggio_mode
E     Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   restart_on_chord
E     Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   octave_range
E     Extra inputs are not permitted [type=extra_forbidden, input_value=[4, 5], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
_________________________________________________ TestRhythmPatternInterpreter.test_generate_note_sequence __________________________________________________
tests/models/test_rhythm_pattern_interpreter.py:39: in test_generate_note_sequence
    rhythm_pattern = RhythmPatternData(
E   pydantic_core._pydantic_core.ValidationError: 4 validation errors for RhythmPatternData
E   notes.0
E     Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=0.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
E       For further information visit https://errors.pydantic.dev/2.10/v/dict_type
E   pattern
E     Input should be a valid list [type=list_type, input_value='4 4 4 4', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/list_type
E   name
E     Extra inputs are not permitted [type=extra_forbidden, input_value='Test Pattern', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   style
E     Extra inputs are not permitted [type=extra_forbidden, input_value='rock', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
_____________________________________________ TestRhythmPatternString.test_rhythm_pattern_string_representation _____________________________________________
tests/models/test_rhythm_pattern_string.py:19: in test_rhythm_pattern_string_representation
    data=RhythmPatternData(
E   pydantic_core._pydantic_core.ValidationError: 6 validation errors for RhythmPatternData
E   notes.0
E     Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=0.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
E       For further information visit https://errors.pydantic.dev/2.10/v/dict_type
E   notes.1
E     Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=1.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
E       For further information visit https://errors.pydantic.dev/2.10/v/dict_type
E   notes.2
E     Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=2.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
E       For further information visit https://errors.pydantic.dev/2.10/v/dict_type
E   pattern
E     Field required [type=missing, input_value={'notes': [RhythmNote(pos...'jazz', 'duration': 4.0}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.10/v/missing
E   style
E     Extra inputs are not permitted [type=extra_forbidden, input_value='jazz', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
E   duration
E     Extra inputs are not permitted [type=extra_forbidden, input_value=4.0, input_type=float]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
__________________________________________ TestRhythmPatternValidation.test_validate_humanize_amount_out_of_bounds __________________________________________
tests/models/test_rhythm_pattern_validation.py:28: in test_validate_humanize_amount_out_of_bounds
    RhythmPatternData(
E   pydantic_core._pydantic_core.ValidationError: 4 validation errors for RhythmPatternData
E   notes.0
E     Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=0.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
E       For further information visit https://errors.pydantic.dev/2.10/v/dict_type
E   time_signature
E     Field required [type=missing, input_value={'notes': [RhythmNote(pos... 'humanize_amount': 1.5}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.10/v/missing
E   pattern
E     Field required [type=missing, input_value={'notes': [RhythmNote(pos... 'humanize_amount': 1.5}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.10/v/missing
E   humanize_amount
E     Extra inputs are not permitted [type=extra_forbidden, input_value=1.5, input_type=float]
E       For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden

During handling of the above exception, another exception occurred:
tests/models/test_rhythm_pattern_validation.py:27: in test_validate_humanize_amount_out_of_bounds
    with pytest.raises(ValueError, match="Input should be less than or equal to 1"):
E   AssertionError: Regex pattern did not match.
E    Regex: 'Input should be less than or equal to 1'
E    Input: "4 validation errors for RhythmPatternData\nnotes.0\n  Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=0.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]\n    For further information visit https://errors.pydantic.dev/2.10/v/dict_type\ntime_signature\n  Field required [type=missing, input_value={'notes': [RhythmNote(pos... 'humanize_amount': 1.5}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing\npattern\n  Field required [type=missing, input_value={'notes': [RhythmNote(pos... 'humanize_amount': 1.5}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing\nhumanize_amount\n  Extra inputs are not permitted [type=extra_forbidden, input_value=1.5, input_type=float]\n    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden"
______________________________________________________ TestRomanNumeral.test_from_scale_degree_MAJOR_7 ______________________________________________________
tests/models/test_roman.py:65: in test_from_scale_degree_MAJOR_7
    self.assertEqual(numeral.numeral, "Imaj7")
E   AssertionError: 'i' != 'Imaj7'
E   - i
E   + Imaj7
_______________________________________________________ TestRomanNumeral.test_from_scale_degree_MINOR _______________________________________________________
tests/models/test_roman.py:46: in test_from_scale_degree_MINOR
    self.assertEqual(numeral.quality, ChordQuality.MINOR)
E   AssertionError: <ChordQuality.MINOR: 'MINOR'> != <ChordQuality.MINOR: 'MINOR'>
______________________________________________________ TestRomanNumeral.test_from_scale_degree_MINOR_7 ______________________________________________________
tests/models/test_roman.py:60: in test_from_scale_degree_MINOR_7
    self.assertEqual(numeral.numeral, "ii7")
E   AssertionError: 'ii' != 'ii7'
E   - ii
E   + ii7
E   ?   +
_____________________________________________________ TestRomanNumeral.test_from_scale_degree_augmented _____________________________________________________
tests/models/test_roman.py:55: in test_from_scale_degree_augmented
    self.assertEqual(numeral.numeral, "IV+")
E   AssertionError: 'iv' != 'IV+'
E   - iv
E   + IV+
____________________________________________________ TestRomanNumeral.test_from_scale_degree_diminished _____________________________________________________
tests/models/test_roman.py:50: in test_from_scale_degree_diminished
    self.assertEqual(numeral.numeral, "iii°")
E   AssertionError: 'iii' != 'iii°'
E   - iii
E   + iii°
E   ?    +
____________________________________________________ TestRomanNumeral.test_from_scale_degree_dominant_7 _____________________________________________________
tests/models/test_roman.py:70: in test_from_scale_degree_dominant_7
    self.assertEqual(numeral.numeral, "V7")
E   AssertionError: 'v' != 'V7'
E   - v
E   + V7
_________________________________________________ TestRomanNumeral.test_get_roman_numeral_from_chord_MAJOR __________________________________________________
tests/models/test_roman.py:38: in test_get_roman_numeral_from_chord_MAJOR
    self.assertEqual(result.numeral, "I")
E   AssertionError: 'i' != 'I'
E   - i
E   + I
___________________________________________ TestRomanNumeral.test_get_roman_numeral_from_chord_different_degrees ____________________________________________
tests/models/test_roman.py:115: in test_get_roman_numeral_from_chord_different_degrees
    self.assertEqual(result.quality, quality)
E   AssertionError: <ChordQuality.MINOR: 'MINOR'> != <ChordQuality.MINOR: 'MINOR'>
_____________________________________________________ test_scale_creation_and_notes[C4-ScaleType.MAJOR] _____________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_____________________________________________________ test_scale_creation_and_notes[D3-ScaleType.MINOR] _____________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
________________________________________________ test_scale_creation_and_notes[A4-ScaleType.HARMONIC_MINOR] _________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
____________________________________________________ test_scale_creation_and_notes[G2-ScaleType.DORIAN] _____________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
___________________________________________________ test_scale_creation_and_notes[C4-ScaleType.CHROMATIC] ___________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_______________________________________________ test_scale_creation_and_notes[E4-ScaleType.MINOR_PENTATONIC] ________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_______________________________________________ test_scale_creation_and_notes[B3-ScaleType.MAJOR_PENTATONIC] ________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
________________________________________________ test_scale_creation_and_notes[C5-ScaleType.HARMONIC_MAJOR] _________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_________________________________________________ test_scale_creation_and_notes[D4-ScaleType.MELODIC_MAJOR] _________________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_____________________________________________ test_scale_creation_and_notes[E5-ScaleType.DOUBLE_HARMONIC_MAJOR] _____________________________________________
tests/models/test_scale.py:31: in test_scale_creation_and_notes
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_____________________________________________________ test_get_scale_degree_valid[C4-ScaleType.MAJOR-1] _____________________________________________________
tests/models/test_scale.py:49: in test_get_scale_degree_valid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_____________________________________________________ test_get_scale_degree_valid[C4-ScaleType.MAJOR-4] _____________________________________________________
tests/models/test_scale.py:49: in test_get_scale_degree_valid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_____________________________________________________ test_get_scale_degree_valid[D3-ScaleType.MINOR-2] _____________________________________________________
tests/models/test_scale.py:49: in test_get_scale_degree_valid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
________________________________________________ test_get_scale_degree_valid[A4-ScaleType.HARMONIC_MINOR-3] _________________________________________________
tests/models/test_scale.py:49: in test_get_scale_degree_valid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
____________________________________________________ test_get_scale_degree_invalid[C4-ScaleType.MAJOR-0] ____________________________________________________
tests/models/test_scale.py:69: in test_get_scale_degree_invalid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
____________________________________________________ test_get_scale_degree_invalid[C4-ScaleType.MAJOR-8] ____________________________________________________
tests/models/test_scale.py:69: in test_get_scale_degree_invalid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_________________________________________________ test_get_scale_degree_invalid[C4-ScaleType.CHROMATIC-13] __________________________________________________
tests/models/test_scale.py:69: in test_get_scale_degree_invalid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
___________________________________________________ test_get_scale_degree_invalid[D3-ScaleType.MINOR--1] ____________________________________________________
tests/models/test_scale.py:69: in test_get_scale_degree_invalid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_______________________________________________ test_get_scale_degree_invalid[A4-ScaleType.HARMONIC_MINOR-8] ________________________________________________
tests/models/test_scale.py:69: in test_get_scale_degree_invalid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
___________________________________________________ test_get_scale_degree_invalid[G2-ScaleType.DORIAN-0] ____________________________________________________
tests/models/test_scale.py:69: in test_get_scale_degree_invalid
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_______________________________________________________________ test_scale_type_degree_count ________________________________________________________________
tests/models/test_scale.py:109: in test_scale_type_degree_count
    scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
________________________________________________________________ test_scale_type_is_diatonic ________________________________________________________________
tests/models/test_scale.py:134: in test_scale_type_is_diatonic
    scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
___________________________________________________ test_scale_type_validate_degree[ScaleType.MAJOR-3-8] ____________________________________________________
tests/models/test_scale.py:154: in test_scale_type_validate_degree
    scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
______________________________________________ test_scale_type_validate_degree[ScaleType.MAJOR_PENTATONIC-4-6] ______________________________________________
tests/models/test_scale.py:154: in test_scale_type_validate_degree
    scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
________________________________________________ test_scale_type_validate_degree[ScaleType.CHROMATIC-10-13] _________________________________________________
tests/models/test_scale.py:154: in test_scale_type_validate_degree
    scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
src/note_gen/models/note.py:276: in from_full_name
    match = cls.FULL_NOTE_REGEX.match(full_name)
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: FULL_NOTE_REGEX
_______________________________________________________ test_chord_progression_with_string_scale_info _______________________________________________________
tests/test_chord_progression.py:13: in test_chord_progression_with_string_scale_info
    chords=[Chord(root='C', quality='MAJOR'), Chord(root='G', quality='MAJOR')]
src/note_gen/models/chord.py:47: in __init__
    super().__init__(**data)
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for Chord
E   root
E     Input should be a valid dictionary or instance of Note [type=model_type, input_value='C', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/model_type
_______________________________________________________ test_chord_progression_with_scale_info_object _______________________________________________________
tests/test_chord_progression.py:19: in test_chord_progression_with_scale_info_object
    scale = ScaleInfo(key='C', scale_type='MAJOR')
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for ScaleInfo
E   root
E     Field required [type=missing, input_value={'key': 'C', 'scale_type': 'MAJOR'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.10/v/missing
_____________________________________________________ test_chord_progression_invalid_scale_info_string ______________________________________________________
tests/test_chord_progression.py:37: in test_chord_progression_invalid_scale_info_string
    chords=[Chord(root='C', quality='MAJOR'), Chord(root='G', quality='MAJOR')]
src/note_gen/models/chord.py:47: in __init__
    super().__init__(**data)
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for Chord
E   root
E     Input should be a valid dictionary or instance of Note [type=model_type, input_value='C', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/model_type

During handling of the above exception, another exception occurred:
tests/test_chord_progression.py:31: in test_chord_progression_invalid_scale_info_string
    with pytest.raises(ValueError, match="Invalid scale info format"):
E   AssertionError: Regex pattern did not match.
E    Regex: 'Invalid scale info format'
E    Input: "1 validation error for Chord\nroot\n  Input should be a valid dictionary or instance of Note [type=model_type, input_value='C', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.10/v/model_type"
______________________________________________________ test_chord_progression_invalid_scale_info_type _______________________________________________________
tests/test_chord_progression.py:48: in test_chord_progression_invalid_scale_info_type
    chords=[Chord(root='C', quality='MAJOR'), Chord(root='G', quality='MAJOR')]
src/note_gen/models/chord.py:47: in __init__
    super().__init__(**data)
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for Chord
E   root
E     Input should be a valid dictionary or instance of Note [type=model_type, input_value='C', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.10/v/model_type

During handling of the above exception, another exception occurred:
tests/test_chord_progression.py:42: in test_chord_progression_invalid_scale_info_type
    with pytest.raises(ValueError, match="scale_info must be either a string or ScaleInfo object"):
E   AssertionError: Regex pattern did not match.
E    Regex: 'scale_info must be either a string or ScaleInfo object'
E    Input: "1 validation error for Chord\nroot\n  Input should be a valid dictionary or instance of Note [type=model_type, input_value='C', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.10/v/model_type"
____________________________________________________________ test_format_chord_progression_valid ____________________________________________________________
tests/test_formatting.py:10: in test_format_chord_progression_valid
    COMMON_PROGRESSIONS = Patterns.COMMON_PROGRESSIONS
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: COMMON_PROGRESSIONS
___________________________________________________________ test_format_chord_progression_invalid ___________________________________________________________
tests/test_formatting.py:41: in test_format_chord_progression_invalid
    COMMON_PROGRESSIONS = Patterns.COMMON_PROGRESSIONS
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: COMMON_PROGRESSIONS
____________________________________________________________ test_format_chord_progression_empty ____________________________________________________________
tests/test_formatting.py:52: in test_format_chord_progression_empty
    COMMON_PROGRESSIONS = Patterns.COMMON_PROGRESSIONS
venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:264: in __getattr__
    raise AttributeError(item)
E   AttributeError: COMMON_PROGRESSIONS
_______________________________________________________ TestTypeSafety.test_type_annotations_present ________________________________________________________
tests/test_types.py:40: in test_type_annotations_present
    assert sig.return_annotation != inspect.Parameter.empty, \
E   AssertionError: Function asynccontextmanager is missing return type annotation
===================================================================== warnings summary ======================================================================
venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:295
venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:295
  /Users/bretbouchard/apps/nick/venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

tests/api/test_fetch_patterns.py:1700
  tests/api/test_fetch_patterns.py:1700: PytestCollectionWarning: Tests based on asynchronous generators are not supported. test_fetch_patterns_api will be ignored.
    @pytest.mark.asyncio

tests/api/test_api.py::test_api_functionality
  /Users/bretbouchard/apps/nick/tests/conftest.py:61: DeprecationWarning: There is no current event loop
    loop = asyncio.get_event_loop()

tests/api/test_api.py::test_invalid_note_name
  tests/api/test_api.py:355: PytestWarning: The test <Function test_invalid_note_name> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_invalid_note_name():

tests/api/test_api.py::test_invalid_note_octave
  tests/api/test_api.py:359: PytestWarning: The test <Function test_invalid_note_octave> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_invalid_note_octave():

tests/test_types.py::test_db_connection_types
  /Users/bretbouchard/apps/nick/tests/test_types.py:18: RuntimeWarning: coroutine 'test_db_connection_types.<locals>.check_db_types' was never awaited
    pytest.mark.asyncio(check_db_types)()
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html

---------- coverage: platform darwin, python 3.12.9-final-0 ----------
Name                                                     Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------------------
src/__init__.py                                              1      0   100%
src/logging_test.py                                          8      8     0%   1-20
src/note_gen/__init__.py                                    15      0   100%
src/note_gen/config.py                                       6      6     0%   4-13
src/note_gen/count_documents.py                             10     10     0%   1-12
src/note_gen/database.py                                   200    200     0%   3-316
src/note_gen/database/__init__.py                           10      3    70%   20, 24, 28
src/note_gen/database/db.py                                 82     23    72%   68-70, 97, 112-129, 132-134
src/note_gen/dependencies.py                                30     12    60%   39-59
src/note_gen/fetch_patterns.py                             936    534    43%   39, 45-55, 59-69, 73-74, 95, 102-103, 107, 111, 117, 127, 148, 150, 152, 154-156, 173, 176, 180, 184, 188-198, 246, 272, 288-289, 297-298, 305-307, 322, 342-343, 351-352, 377, 394, 397, 408, 411, 421-422, 435, 438, 441, 446-447, 449-459, 467-468, 472-474, 490, 493, 506, 510, 530, 575, 584, 587-588, 604-606, 620-631, 633-646, 650-653, 668, 687-690, 697-698, 711-795, 806-834, 856, 866-881, 885-900, 907-941, 954-1018, 1032-1116, 1128-1159, 1182-1184, 1201-1202, 1227-1228, 1242-1244, 1254, 1262-1263, 1268-1269, 1276-1277, 1284-1285, 1288-1289, 1294, 1300, 1318-1336, 1353, 1365-1423, 1436-1507, 1533-1608, 1628-1691, 1709, 1717-1718, 1729-1731, 1740-1741, 1747-1748, 1758-1759, 1781-1782, 1786, 1813, 1817, 1821
src/note_gen/generators/chord_progression_generator.py     357    303    15%   29, 82-98, 105-122, 140-180, 196-221, 225-248, 252-292, 313-319, 323-328, 333-339, 343-395, 398-442, 452-461, 484-556, 574-637, 659-787, 806-840, 855-861, 874-893, 901-904
src/note_gen/generators/note_sequence_generator.py         208    168    19%   35-47, 66-88, 92-93, 97-98, 107-223, 226-233, 237-244, 248-267, 271-278, 282-287, 291-296
src/note_gen/import_presets.py                              91     91     0%   3-193
src/note_gen/models/__init__.py                              7      0   100%
src/note_gen/models/base.py                                  6      1    83%   16
src/note_gen/models/base_enums.py                           35     35     0%   1-81
src/note_gen/models/chord.py                                98     25    74%   39, 42-44, 54-66, 111-112, 130, 149-162, 176, 179
src/note_gen/models/chord_progression.py                    13      0   100%
src/note_gen/models/chord_progression_extras.py            121    121     0%   1-194
src/note_gen/models/chord_quality.py                        47     16    66%   32-60, 64, 70-114
src/note_gen/models/enums.py                                37      5    86%   57-58, 63, 67, 71
src/note_gen/models/fake_scale_info.py                      23      4    83%   31-45
src/note_gen/models/musical_elements.py                     58     58     0%   1-109
src/note_gen/models/note.py                                229     75    67%   25, 29-34, 61, 67, 72-77, 98, 105-106, 110, 116, 118-120, 156, 163, 203, 273, 277-290, 303-306, 322-325, 374, 392, 410, 419, 439, 451, 489, 504-525, 554-556, 562-564, 570-572, 576-587, 591-592
src/note_gen/models/note_event.py                           57     30    47%   39-41, 46-48, 53-55, 60, 64, 68-86, 90, 100
src/note_gen/models/note_sequence.py                        86     39    55%   27-41, 46-48, 57-63, 68, 72-75, 79-82, 87-89, 93, 101, 127, 131, 134, 137
src/note_gen/models/pattern_interpreter.py                 130     81    38%   51, 53, 60-69, 76, 84-94, 98, 107-149, 153, 156-176, 180-200, 232-246, 263, 280, 298-302
src/note_gen/models/pattern_type.py                         31      1    97%   40
src/note_gen/models/patterns.py                            559    268    52%   254, 260-262, 267-269, 274-276, 285-287, 300-304, 310-320, 326-330, 342, 346, 352-371, 376, 381-385, 389-390, 394-395, 399-412, 428-432, 437-441, 445-447, 496-497, 501-508, 514-517, 523-537, 542-550, 554-562, 566, 590-622, 653-694, 720-743, 763-787, 811, 848-850, 893-898, 904-908, 914-919, 925-929, 934-939, 945, 948, 950, 956-958, 964, 971, 975-982, 987-989, 996, 1003, 1005, 1007, 1014, 1037, 1042, 1047-1048, 1063, 1069, 1072, 1078, 1083, 1114-1161, 1165, 1169, 1173
src/note_gen/models/presets.py                             127     54    57%   70-71, 78-86, 92-96, 100-114, 217-226, 230-232, 242, 263, 266, 273, 295, 316, 320, 324, 328-354, 366, 370, 374
src/note_gen/models/request_models.py                       10      0   100%
src/note_gen/models/rhythm_pattern.py                       12     12     0%   1-13
src/note_gen/models/roman_numeral.py                        82     25    70%   28, 33, 35, 37, 39, 41, 54-67, 74, 81-84, 110, 120, 124, 128
src/note_gen/models/scale.py                                53     18    66%   39-41, 45, 49-53, 57-60, 65-66, 75, 78, 81
src/note_gen/models/scale_degree.py                         15      5    67%   17-19, 23, 28
src/note_gen/models/scale_info.py                           19      8    58%   20-36
src/note_gen/models/sequence_generation.py                   7      7     0%   1-8
src/note_gen/models/user.py                                 12      0   100%
src/note_gen/populate_db.py                                 57     35    39%   35-37, 40-53, 72, 85, 97-99, 102-134, 137-138
src/note_gen/routers/chord_progression_routes.py            18      8    56%   18-20, 28-33
src/note_gen/routers/note_pattern_routes.py                265    234    12%   41-86, 90-98, 106-140, 149-150, 160-165, 172-239, 247-321, 330-408, 416-460
src/note_gen/routers/note_sequence_routes.py               265    238    10%   37-38, 55-61, 84-96, 119-142, 155-299, 326-540, 557-568
src/note_gen/routers/rhythm_pattern_routes.py              150    107    29%   34-40, 56-59, 65, 84-91, 103-168, 182-184, 193-238, 250-289
src/note_gen/routers/user_routes.py                         31     12    61%   27-28, 33-36, 41-43, 48-50
src/note_gen/run_import_presets.py                          14     14     0%   1-20
src/note_gen/run_import_presets_v2.py                       14     14     0%   1-20
src/note_gen/typings/__init__.py                             0      0   100%
src/note_gen/update_database.py                             13     13     0%   1-33
src/note_gen/update_scale_types.py                          17     17     0%   1-35
--------------------------------------------------------------------------------------
TOTAL                                                     4672   2938    37%

================================================================== short test summary info ==================================================================
XFAIL tests/api/test_fetch_patterns.py::test_fetch_patterns_api - reason: [NOTRUN] Tests based on asynchronous generators are not supported. test_fetch_patterns_api will be ignored.
ERROR tests/api/test_api.py::test_api_functionality - pymongo.errors.InvalidOperation: Cannot use MongoClient after close
ERROR tests/api/test_api.py::test_create_chord_progression_valid_data - pymongo.errors.InvalidOperation: Cannot use MongoClient after close
ERROR tests/api/test_api.py::test_create_chord_progression_invalid_data - pymongo.errors.InvalidOperation: Cannot use MongoClient after close
ERROR tests/api/test_api.py::test_create_chord_progression_valid_data_with_additional_fields - pymongo.errors.InvalidOperation: Cannot use MongoClient after close
ERROR tests/api/test_api.py::test_create_chord_progression_invalid_data_with_missing_chords - pymongo.errors.InvalidOperation: Cannot use MongoClient after close
ERROR tests/api/test_api.py::test_create_chord_progression_invalid_data_with_empty_chords - pymongo.errors.InvalidOperation: Cannot use MongoClient after close
ERROR tests/api/test_chord_progression_check.py::test_chord_progression_functionality
ERROR tests/api/test_note_sequence.py::test_note_sequence
ERROR tests/api/test_note_sequence.py::test_get_note_sequences
ERROR tests/api/test_note_sequence.py::test_note_sequence_functionality
ERROR tests/api/test_rhythm_pattern_check.py::test_rhythm_pattern_with_float_values
ERROR tests/api/test_rhythm_pattern_check.py::test_rhythm_pattern_with_rests
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_with_empty_chords_and_test_mode - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_with_invalid_scale_type - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_chord_with_duration - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_chord_progression_with_duration - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_progression_with_tension_resolution - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_chord_notes - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_chord_with_duration_and_velocity - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_invalid_note_name_raises_error - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_progression_with_complexity_target - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_genre_progression - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_get_root_note_from_degree - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_no_pattern_provided_raises_error - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_invalid_pattern_raises_validation_error - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_with_valid_pattern - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_custom_with_mismatched_lists_raises_error - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_custom_valid - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_custom_invalid_degree - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_random_valid_length - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_chord_progression_with_negative_length - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_chord_progression_with_boundary_values - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_calculate_pattern_complexity - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_chord_progression_generator.py::TestChordProgressionGenerator::test_generate_notes_from_chord_progression[chord_progression0-note_pattern0-expected_notes0] - typeguard.TypeCheckError: argument "scale_type" (src.note_gen.core.enums.ScaleType) is not an instance of str
ERROR tests/generators/test_note_sequence_generator.py::test_generate_sequence[chord_progression0-note_pattern0-expected_notes0] - AttributeError: 'list' object has no attribute 'split'
ERROR tests/test_main.py::test_startup_imports_presets_when_empty - pymongo.errors.InvalidOperation: Cannot use MongoClient after close
ERROR tests/test_main.py::test_startup_skips_import_when_not_empty - pymongo.errors.InvalidOperation: Cannot use MongoClient after close
ERROR tests/test_types.py::TestTypeSafety::test_type_annotations_present - ValueError: The future belongs to a different loop than the one specified as the loop argument
FAILED tests/api/test_api.py::test_invalid_note_octave - Failed: DID NOT RAISE <class 'pydantic_core._pydantic_core.ValidationError'>
FAILED tests/api/test_fetch_import_patterns.py::test_fetch_note_patterns - TypeError: object AsyncIOMotorDatabase can't be used in 'await' expression
FAILED tests/api/test_fetch_import_patterns.py::test_fetch_rhythm_patterns - TypeError: object AsyncIOMotorDatabase can't be used in 'await' expression
FAILED tests/api/test_fetch_patterns.py::test_fetch_chord_progressions - AssertionError: No chord progressions returned by fetch_chord_progressions
assert 0 > 0
 +  where 0 = len([])
FAILED tests/api/test_fetch_patterns.py::test_fetch_chord_progression_by_id_v1 - AssertionError: Failed to fetch chord progression by ID
assert None is not None
FAILED tests/api/test_fetch_patterns.py::test_fetch_rhythm_patterns - AssertionError: No rhythm patterns returned by fetch_rhythm_patterns
assert 0 > 0
 +  where 0 = len([])
FAILED tests/api/test_fetch_patterns.py::test_fetch_rhythm_pattern_by_id - AssertionError: Failed to fetch rhythm pattern by ID
assert None is not None
FAILED tests/api/test_fetch_patterns.py::test_fetch_note_patterns - AssertionError: No note patterns were fetched
assert 0 > 0
 +  where 0 = len([])
FAILED tests/api/test_fetch_patterns.py::test_fetch_note_pattern_by_id - AssertionError: No note patterns available for testing
assert False
FAILED tests/api/test_fetch_patterns.py::test_fetch_with_invalid_data - AssertionError: Regex pattern did not match.
 Regex: 'Value error, Chords list cannot be empty'
 Input: "2 validation errors for ChordProgression\nscale_info.key\n  Field required [type=missing, input_value={'root': {'note_name': 'C..., 'scale_type': 'MAJOR'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing\nid\n  Extra inputs are not permitted [type=extra_forbidden, input_value='invalid_id', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden"
FAILED tests/api/test_fetch_patterns.py::test_fetch_chord_progressions_with_new_data - pydantic_core._pydantic_core.ValidationError: 2 validation errors for ChordProgression
scale_info.key
  Field required [type=missing, input_value={'root': {'note_name': 'C..., 'scale_type': 'MAJOR'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
id
  Extra inputs are not permitted [type=extra_forbidden, input_value='ceb9870f-7463-4c4c-b361-4fc5306849d8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
FAILED tests/api/test_fetch_patterns.py::test_fetch_note_patterns_with_new_data - assert 0 > 0
 +  where 0 = len([])
FAILED tests/api/test_fetch_patterns.py::test_fetch_rhythm_patterns_with_new_data - assert 0 > 0
 +  where 0 = len([])
FAILED tests/api/test_fetch_patterns.py::test_fetch_note_patterns_with_structured_data - AttributeError: 'function' object has no attribute 'get'
FAILED tests/api/test_fetch_patterns.py::test_fetch_note_patterns_with_legacy_data - AssertionError: No note patterns found
assert 0 > 0
 +  where 0 = len([])
FAILED tests/api/test_fetch_patterns.py::test_fetch_chord_progression_patterns - pydantic_core._pydantic_core.ValidationError: 1 validation error for ChordProgressionPattern
chords
  Field required [type=missing, input_value={'id': 'a30beeec-824c-4f4...on'], 'complexity': 0.3}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
FAILED tests/api/test_fetch_patterns.py::test_fetch_chord_progression_pattern_by_id - assert None is not None
FAILED tests/api/test_fetch_patterns.py::test_extract_patterns_from_chord_progressions - pydantic_core._pydantic_core.ValidationError: 1 validation error for ScaleInfo
key
  Field required [type=missing, input_value={'root': Note(note_name='...aleType.MAJOR: 'MAJOR'>}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
FAILED tests/api/test_generate_sequence.py::test_generate_sequence_from_presets - assert 404 == 200
 +  where 404 = <Response [404 Not Found]>.status_code
FAILED tests/api/test_generate_sequence.py::test_generate_sequence_invalid_progression - AssertionError: assert 'Chord progression' in 'Not Found'
FAILED tests/api/test_generate_sequence.py::test_generate_sequence_invalid_note_pattern - AssertionError: assert 'Note pattern' in 'Not Found'
FAILED tests/api/test_generate_sequence.py::test_generate_sequence_invalid_rhythm_pattern - AssertionError: assert 'Rhythm pattern' in 'Not Found'
FAILED tests/api/test_generate_sequence.py::test_note_sequence - assert 404 == 200
 +  where 404 = <Response [404 Not Found]>.status_code
FAILED tests/api/test_generate_sequence.py::test_generate_sequence_functionality - assert 404 == 200
 +  where 404 = <Response [404 Not Found]>.status_code
FAILED tests/api/test_note_pattern_check.py::test_note_pattern_functionality - AssertionError: Failed to create note pattern: {"detail":"Not Found"}
assert 404 == 201
 +  where 404 = <Response [404 Not Found]>.status_code
FAILED tests/api/test_user_routes.py::test_get_rhythm_pattern - assert 422 == 201
 +  where 422 = <Response [422 Unprocessable Entity]>.status_code
FAILED tests/api/test_user_routes.py::test_create_rhythm_pattern - AssertionError: Failed to create pattern: {'detail': [{'type': 'missing', 'loc': ['body', 'pattern'], 'msg': 'Field required', 'input': {'name': 'Test Create Pattern', 'data': {'notes': [{'position': 0.0, 'duration': 1.0, 'velocity': 100, 'is_rest': False}, {'position': 1.0, 'duration': 1.0, 'velocity': 100, 'is_rest': True}], 'time_signature': '4/4', 'swing_ratio': 0.5, 'default_duration': 1.0, 'total_duration': 4.0, 'groove_type': 'swing'}, 'is_test': True, 'style': 'basic', 'tags': ['test']}}, {'type': 'missing', 'loc': ['body', 'data', 'pattern'], 'msg': 'Field required', 'input': {'notes': [{'position': 0.0, 'duration': 1.0, 'velocity': 100, 'is_rest': False}, {'position': 1.0, 'duration': 1.0, 'velocity': 100, 'is_rest': True}], 'time_signature': '4/4', 'swing_ratio': 0.5, 'default_duration': 1.0, 'total_duration': 4.0, 'groove_type': 'swing'}}, {'type': 'extra_forbidden', 'loc': ['body', 'data', 'total_duration'], 'msg': 'Extra inputs are not permitted', 'input': 4.0}]}
assert 422 == 201
 +  where 422 = <Response [422 Unprocessable Entity]>.status_code
FAILED tests/api/test_user_routes.py::test_create_duplicate_rhythm_pattern - AssertionError: Failed to create first pattern: {'detail': [{'type': 'missing', 'loc': ['body', 'pattern'], 'msg': 'Field required', 'input': {'name': 'Test Duplicate Pattern d25db8c2-eb6c-44b1-a07a-ef433d803744', 'data': {'notes': [{'position': 0.0, 'duration': 1.0, 'velocity': 100, 'is_rest': False}, {'position': 1.0, 'duration': 1.0, 'velocity': 100, 'is_rest': True}], 'time_signature': '4/4', 'swing_ratio': 0.5, 'default_duration': 1.0, 'total_duration': 4.0, 'groove_type': 'swing'}, 'is_test': True, 'style': 'basic', 'tags': ['test']}}, {'type': 'missing', 'loc': ['body', 'data', 'pattern'], 'msg': 'Field required', 'input': {'notes': [{'position': 0.0, 'duration': 1.0, 'velocity': 100, 'is_rest': False}, {'position': 1.0, 'duration': 1.0, 'velocity': 100, 'is_rest': True}], 'time_signature': '4/4', 'swing_ratio': 0.5, 'default_duration': 1.0, 'total_duration': 4.0, 'groove_type': 'swing'}}, {'type': 'extra_forbidden', 'loc': ['body', 'data', 'total_duration'], 'msg': 'Extra inputs are not permitted', 'input': 4.0}]}
assert 422 == 201
 +  where 422 = <Response [422 Unprocessable Entity]>.status_code
FAILED tests/api/test_user_routes.py::test_create_and_delete_rhythm_pattern - AssertionError: Failed to create pattern: {"detail":[{"type":"missing","loc":["body","pattern"],"msg":"Field required","input":{"name":"Test Delete Pattern 50a5349f-b6c4-4ed3-905c-f4281df775aa","data":{"notes":[{"position":0.0,"duration":1.0,"velocity":100,"is_rest":false},{"position":1.0,"duration":1.0,"velocity":100,"is_rest":true}],"time_signature":"4/4","swing_ratio":0.5,"default_duration":1.0,"total_duration":4.0,"groove_type":"swing"},"is_test":true,"style":"basic","tags":["test"]}},{"type":"missing","loc":["body","data","pattern"],"msg":"Field required","input":{"notes":[{"position":0.0,"duration":1.0,"velocity":100,"is_rest":false},{"position":1.0,"duration":1.0,"velocity":100,"is_rest":true}],"time_signature":"4/4","swing_ratio":0.5,"default_duration":1.0,"total_duration":4.0,"groove_type":"swing"}},{"type":"extra_forbidden","loc":["body","data","total_duration"],"msg":"Extra inputs are not permitted","input":4.0}]}
assert 422 == 201
 +  where 422 = <Response [422 Unprocessable Entity]>.status_code
FAILED tests/models/test_Integration.py::test_chord_with_note_event_integration - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord.py::test_create_chord - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord.py::test_chord_initialization - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord.py::test_chord_diminished_quality - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord.py::test_chord_inversion - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord.py::test_chord_invalid_inversion - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord.py::test_chord_MAJOR_with_seventh - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord.py::test_chord_transposition - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_chord_progression_edge_cases - AssertionError: ValidationError not raised
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_chord_progression_mismatched_scale_info - AssertionError: ValidationError not raised
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_chord_progression_optional_fields - AttributeError: 'ChordProgression' object has no attribute 'genre'
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_chord_progression_validation - AssertionError: ValidationError not raised
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_complexity_validation - AssertionError: ValidationError not raised
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_empty_chords - AssertionError: ValidationError not raised
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_generate_progression_from_pattern - AttributeError: 'ChordProgression' object has no attribute 'generate_progression_from_pattern'
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_invalid_complexity - AssertionError: ValidationError not raised
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_model_dump - AssertionError: assert 'id' in {'name': 'Test Progression', 'chords': [{'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, 'quality': <ChordQuality.MAJOR: 'MAJOR'>, 'duration': 1.0, 'inversion': 0, 'notes': [{'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 64, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 64, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}]}, {'root': {'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, 'quality': <ChordQuality.MAJOR: 'MAJOR'>, 'duration': 1.0, 'inversion': 0, 'notes': [{'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, {'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 64, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, {'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 64, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}]}], 'key': 'C', 'scale_type': 'MAJOR', 'scale_info': {'type': 'real', 'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, 'scale_type': <ScaleType.MAJOR: 'MAJOR'>, 'key': 'C'}, 'complexity': 0.5, 'quality': None}
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_name_validation - AssertionError: ValidationError not raised
FAILED tests/models/test_chord_progression.py::TestChordProgression::test_to_dict - AssertionError: assert 'id' in {'name': 'Test To Dict', 'chords': [{'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, 'quality': <ChordQuality.MAJOR: 'MAJOR'>, 'duration': 1.0, 'inversion': 0, 'notes': [{'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 64, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 64, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}]}, {'root': {'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, 'quality': <ChordQuality.MAJOR: 'MAJOR'>, 'duration': 1.0, 'inversion': 0, 'notes': [{'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, {'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 64, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, {'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 64, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}]}], 'key': 'C', 'scale_type': 'MAJOR', 'scale_info': {'type': 'real', 'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100, 'position': 0.0, 'stored_midi_number': None, 'scale_degree': None}, 'scale_type': <ScaleType.MAJOR: 'MAJOR'>, 'key': 'C'}, 'complexity': 0.7, 'quality': None}
FAILED tests/models/test_chord_quality.py::TestChordQuality::test_chord_quality_variations - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord_quality.py::TestChordQuality::test_from_string_valid - AttributeError: type object 'ChordQuality' has no attribute 'DOMINANT'
FAILED tests/models/test_chord_quality.py::TestChordQuality::test_get_intervals - AttributeError: type object 'ChordQuality' has no attribute 'DOMINANT'
FAILED tests/models/test_chord_quality.py::TestChordQuality::test_get_intervals_invalid_quality - AttributeError: 'ChordQuality' object has no attribute 'get_intervals'
FAILED tests/models/test_chord_quality.py::TestChordQuality::test_get_intervals_undefined_quality - AttributeError: type object 'ChordQuality' has no attribute 'from_string'
FAILED tests/models/test_chord_quality.py::TestChordQuality::test_invalid_quality - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_chord_quality.py::TestChordQuality::test_invalid_quality_string - AttributeError: type object 'ChordQuality' has no attribute 'from_string'
FAILED tests/models/test_chord_quality.py::TestChordQuality::test_str_representation - AttributeError: type object 'ChordQuality' has no attribute 'DOMINANT'
FAILED tests/models/test_chord_variations.py::test_chord_quality_variations - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_fake_scale_info.py::TestFakeScaleInfo::test_valid_initialization - pydantic_core._pydantic_core.ValidationError: 1 validation error for FakeScaleInfo
key
  Field required [type=missing, input_value={'root': Note(note_name='...OR'>, 'complexity': 0.5}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
FAILED tests/models/test_note.py::test_note_from_name - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_note_transpose - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_invalid_note_initialization - Failed: DID NOT RAISE <class 'pydantic_core._pydantic_core.ValidationError'>
FAILED tests/models/test_note.py::test_full_note_name - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_midi_conversion - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_transpose_out_of_range_high - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_transpose_out_of_range_low - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_fill_missing_fields_with_invalid_string - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_from_full_name - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_from_full_name_valid - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_from_full_name_invalid - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_transpose_to_limits - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note.py::test_fill_missing_fields_invalid_dict - Failed: DID NOT RAISE <class 'ValueError'>
FAILED tests/models/test_note.py::test_check_validations_invalid_duration - Failed: DID NOT RAISE <class 'pydantic_core._pydantic_core.ValidationError'>
FAILED tests/models/test_note.py::test_check_validations_invalid_octave - Failed: DID NOT RAISE <class 'pydantic_core._pydantic_core.ValidationError'>
FAILED tests/models/test_note.py::test_transpose_invalid_octave - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note_event.py::test_create_note_event - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note_event.py::test_invalid_position - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note_event.py::test_invalid_duration - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note_event.py::test_invalid_velocity - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note_event.py::test_note_event_creation_with_velocity - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note_event.py::test_note_event_negative_duration - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_note_pattern.py::test_name_validation - Failed: DID NOT RAISE <class 'pydantic_core._pydantic_core.ValidationError'>
FAILED tests/models/test_note_pattern.py::test_pattern_validation - AssertionError: Regex pattern did not match.
 Regex: 'List should have at least 1 item'
 Input: '1 validation error for NotePatternData\nintervals\n  Value error, Intervals cannot be empty [type=value_error, input_value=[], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.10/v/value_error'
FAILED tests/models/test_patterns.py::test_rhythm_pattern_validation - pydantic_core._pydantic_core.ValidationError: 5 validation errors for RhythmPattern
data.notes
  Field required [type=missing, input_value={'beats': 4, 'subdivisions': 4}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
data.time_signature
  Field required [type=missing, input_value={'beats': 4, 'subdivisions': 4}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
data.pattern
  Field required [type=missing, input_value={'beats': 4, 'subdivisions': 4}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
data.beats
  Extra inputs are not permitted [type=extra_forbidden, input_value=4, input_type=int]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
data.subdivisions
  Extra inputs are not permitted [type=extra_forbidden, input_value=4, input_type=int]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
FAILED tests/models/test_patterns.py::test_time_signature_validation - pydantic_core._pydantic_core.ValidationError: 3 validation errors for RhythmPattern
data.notes
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
data.time_signature
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
data.pattern
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
FAILED tests/models/test_presets.py::test_preset_initialization - pydantic_core._pydantic_core.ValidationError: 12 validation errors for RhythmPatternData
notes
  Field required [type=missing, input_value={'pattern': '1 1 1 1', 'd...'default_duration': 1.0}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
time_signature
  Field required [type=missing, input_value={'pattern': '1 1 1 1', 'd...'default_duration': 1.0}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
pattern
  Input should be a valid list [type=list_type, input_value='1 1 1 1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/list_type
duration
  Extra inputs are not permitted [type=extra_forbidden, input_value=1.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
position
  Extra inputs are not permitted [type=extra_forbidden, input_value=0.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
velocity
  Extra inputs are not permitted [type=extra_forbidden, input_value=100, input_type=int]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
direction
  Extra inputs are not permitted [type=extra_forbidden, input_value='up', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
use_chord_tones
  Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
use_scale_mode
  Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
arpeggio_mode
  Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
restart_on_chord
  Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
octave_range
  Extra inputs are not permitted [type=extra_forbidden, input_value=[4, 5], input_type=list]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
FAILED tests/models/test_presets.py::test_load_presets - pydantic_core._pydantic_core.ValidationError: 12 validation errors for RhythmPatternData
notes
  Field required [type=missing, input_value={'pattern': '1 1 1 1', 'd...'default_duration': 1.0}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
time_signature
  Field required [type=missing, input_value={'pattern': '1 1 1 1', 'd...'default_duration': 1.0}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
pattern
  Input should be a valid list [type=list_type, input_value='1 1 1 1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/list_type
duration
  Extra inputs are not permitted [type=extra_forbidden, input_value=1.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
position
  Extra inputs are not permitted [type=extra_forbidden, input_value=0.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
velocity
  Extra inputs are not permitted [type=extra_forbidden, input_value=100, input_type=int]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
direction
  Extra inputs are not permitted [type=extra_forbidden, input_value='up', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
use_chord_tones
  Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
use_scale_mode
  Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
arpeggio_mode
  Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
restart_on_chord
  Extra inputs are not permitted [type=extra_forbidden, input_value=False, input_type=bool]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
octave_range
  Extra inputs are not permitted [type=extra_forbidden, input_value=[4, 5], input_type=list]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
FAILED tests/models/test_rhythm_pattern_interpreter.py::TestRhythmPatternInterpreter::test_generate_note_sequence - pydantic_core._pydantic_core.ValidationError: 4 validation errors for RhythmPatternData
notes.0
  Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=0.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
    For further information visit https://errors.pydantic.dev/2.10/v/dict_type
pattern
  Input should be a valid list [type=list_type, input_value='4 4 4 4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/list_type
name
  Extra inputs are not permitted [type=extra_forbidden, input_value='Test Pattern', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
style
  Extra inputs are not permitted [type=extra_forbidden, input_value='rock', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
FAILED tests/models/test_rhythm_pattern_string.py::TestRhythmPatternString::test_rhythm_pattern_string_representation - pydantic_core._pydantic_core.ValidationError: 6 validation errors for RhythmPatternData
notes.0
  Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=0.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
    For further information visit https://errors.pydantic.dev/2.10/v/dict_type
notes.1
  Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=1.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
    For further information visit https://errors.pydantic.dev/2.10/v/dict_type
notes.2
  Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=2.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]
    For further information visit https://errors.pydantic.dev/2.10/v/dict_type
pattern
  Field required [type=missing, input_value={'notes': [RhythmNote(pos...'jazz', 'duration': 4.0}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
style
  Extra inputs are not permitted [type=extra_forbidden, input_value='jazz', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
duration
  Extra inputs are not permitted [type=extra_forbidden, input_value=4.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden
FAILED tests/models/test_rhythm_pattern_validation.py::TestRhythmPatternValidation::test_validate_humanize_amount_out_of_bounds - AssertionError: Regex pattern did not match.
 Regex: 'Input should be less than or equal to 1'
 Input: "4 validation errors for RhythmPatternData\nnotes.0\n  Input should be a valid dictionary [type=dict_type, input_value=RhythmNote(position=0.0, ...=None, swing_ratio=0.67), input_type=RhythmNote]\n    For further information visit https://errors.pydantic.dev/2.10/v/dict_type\ntime_signature\n  Field required [type=missing, input_value={'notes': [RhythmNote(pos... 'humanize_amount': 1.5}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing\npattern\n  Field required [type=missing, input_value={'notes': [RhythmNote(pos... 'humanize_amount': 1.5}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing\nhumanize_amount\n  Extra inputs are not permitted [type=extra_forbidden, input_value=1.5, input_type=float]\n    For further information visit https://errors.pydantic.dev/2.10/v/extra_forbidden"
FAILED tests/models/test_roman.py::TestRomanNumeral::test_from_scale_degree_MAJOR_7 - AssertionError: 'i' != 'Imaj7'
- i
+ Imaj7
FAILED tests/models/test_roman.py::TestRomanNumeral::test_from_scale_degree_MINOR - AssertionError: <ChordQuality.MINOR: 'MINOR'> != <ChordQuality.MINOR: 'MINOR'>
FAILED tests/models/test_roman.py::TestRomanNumeral::test_from_scale_degree_MINOR_7 - AssertionError: 'ii' != 'ii7'
- ii
+ ii7
?   +
FAILED tests/models/test_roman.py::TestRomanNumeral::test_from_scale_degree_augmented - AssertionError: 'iv' != 'IV+'
- iv
+ IV+
FAILED tests/models/test_roman.py::TestRomanNumeral::test_from_scale_degree_diminished - AssertionError: 'iii' != 'iii°'
- iii
+ iii°
?    +
FAILED tests/models/test_roman.py::TestRomanNumeral::test_from_scale_degree_dominant_7 - AssertionError: 'v' != 'V7'
- v
+ V7
FAILED tests/models/test_roman.py::TestRomanNumeral::test_get_roman_numeral_from_chord_MAJOR - AssertionError: 'i' != 'I'
- i
+ I
FAILED tests/models/test_roman.py::TestRomanNumeral::test_get_roman_numeral_from_chord_different_degrees - AssertionError: <ChordQuality.MINOR: 'MINOR'> != <ChordQuality.MINOR: 'MINOR'>
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[C4-ScaleType.MAJOR] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[D3-ScaleType.MINOR] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[A4-ScaleType.HARMONIC_MINOR] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[G2-ScaleType.DORIAN] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[C4-ScaleType.CHROMATIC] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[E4-ScaleType.MINOR_PENTATONIC] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[B3-ScaleType.MAJOR_PENTATONIC] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[C5-ScaleType.HARMONIC_MAJOR] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[D4-ScaleType.MELODIC_MAJOR] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_creation_and_notes[E5-ScaleType.DOUBLE_HARMONIC_MAJOR] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_valid[C4-ScaleType.MAJOR-1] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_valid[C4-ScaleType.MAJOR-4] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_valid[D3-ScaleType.MINOR-2] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_valid[A4-ScaleType.HARMONIC_MINOR-3] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_invalid[C4-ScaleType.MAJOR-0] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_invalid[C4-ScaleType.MAJOR-8] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_invalid[C4-ScaleType.CHROMATIC-13] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_invalid[D3-ScaleType.MINOR--1] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_invalid[A4-ScaleType.HARMONIC_MINOR-8] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_get_scale_degree_invalid[G2-ScaleType.DORIAN-0] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_type_degree_count - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_type_is_diatonic - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_type_validate_degree[ScaleType.MAJOR-3-8] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_type_validate_degree[ScaleType.MAJOR_PENTATONIC-4-6] - AttributeError: FULL_NOTE_REGEX
FAILED tests/models/test_scale.py::test_scale_type_validate_degree[ScaleType.CHROMATIC-10-13] - AttributeError: FULL_NOTE_REGEX
FAILED tests/test_chord_progression.py::test_chord_progression_with_string_scale_info - pydantic_core._pydantic_core.ValidationError: 1 validation error for Chord
root
  Input should be a valid dictionary or instance of Note [type=model_type, input_value='C', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/model_type
FAILED tests/test_chord_progression.py::test_chord_progression_with_scale_info_object - pydantic_core._pydantic_core.ValidationError: 1 validation error for ScaleInfo
root
  Field required [type=missing, input_value={'key': 'C', 'scale_type': 'MAJOR'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
FAILED tests/test_chord_progression.py::test_chord_progression_invalid_scale_info_string - AssertionError: Regex pattern did not match.
 Regex: 'Invalid scale info format'
 Input: "1 validation error for Chord\nroot\n  Input should be a valid dictionary or instance of Note [type=model_type, input_value='C', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.10/v/model_type"
FAILED tests/test_chord_progression.py::test_chord_progression_invalid_scale_info_type - AssertionError: Regex pattern did not match.
 Regex: 'scale_info must be either a string or ScaleInfo object'
 Input: "1 validation error for Chord\nroot\n  Input should be a valid dictionary or instance of Note [type=model_type, input_value='C', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.10/v/model_type"
FAILED tests/test_formatting.py::test_format_chord_progression_valid - AttributeError: COMMON_PROGRESSIONS
FAILED tests/test_formatting.py::test_format_chord_progression_invalid - AttributeError: COMMON_PROGRESSIONS
FAILED tests/test_formatting.py::test_format_chord_progression_empty - AttributeError: COMMON_PROGRESSIONS
FAILED tests/test_types.py::TestTypeSafety::test_type_annotations_present - AssertionError: Function asynccontextmanager is missing return type annotation
============================================= 130 failed, 85 passed, 1 xfailed, 7 warnings, 38 errors in 5.05s ==============================================
(venv) (base) bretbouchard@Brets-Mac-mini nick % 