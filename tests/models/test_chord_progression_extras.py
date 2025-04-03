"""Tests for chord progression extras models."""
import pytest
from unittest.mock import MagicMock, patch
from note_gen.models.chord_progression_extras import (
    ChordProgressionResponse,
    valid_qualities
)
from dataclasses import dataclass

@dataclass
class MidiRange:
    min_midi: int = 0
    max_midi: int = 127

MIDI_LIMITS = MidiRange()
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.chord_progression_item import ChordProgressionItem
from note_gen.core.enums import ScaleType, ChordQuality
from bson import ObjectId


def test_midi_range():
    """Test MidiRange dataclass."""
    # Test default values
    assert MIDI_LIMITS.min_midi == 0
    assert MIDI_LIMITS.max_midi == 127

    # Test creating a custom range
    custom_range = MidiRange(min_midi=24, max_midi=96)
    assert custom_range.min_midi == 24
    assert custom_range.max_midi == 96


def test_valid_qualities():
    """Test valid_qualities set."""
    # Verify it contains all chord qualities
    assert isinstance(valid_qualities, set)
    assert len(valid_qualities) > 0
    assert ChordQuality.MAJOR in valid_qualities
    assert ChordQuality.MINOR in valid_qualities


def test_chord_progression_response_init():
    """Test ChordProgressionResponse initialization."""
    # Create a scale info
    scale_info = ScaleInfo(
        key="C",
        scale_type=ScaleType.MAJOR
    )

    # Create a chord progression item
    chord_item = ChordProgressionItem(
        chord_symbol="C",
        duration=1.0
    )

    # Create a response
    response = ChordProgressionResponse(
        name="Test Progression",
        chords=[chord_item],
        scale_info=scale_info,
        key="C",
        scale_type=ScaleType.MAJOR,
        complexity=0.5,
        duration=4.0
    )

    # Verify fields
    assert response.name == "Test Progression"
    assert len(response.chords) == 1
    assert response.chords[0] == chord_item
    assert response.scale_info == scale_info
    assert response.key == "C"
    assert response.scale_type == ScaleType.MAJOR
    assert response.complexity == 0.5
    assert response.duration == 4.0


def test_chord_progression_response_from_db_model():
    """Test creating a response from a database model."""
    # Create a mock database model
    db_model = {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "name": "Test Progression",
        "chords": [
            {
                "chord_symbol": "C",
                "duration": 1.0
            }
        ],
        "scale_info": {
            "key": "C",
            "scale_type": "MAJOR"
        },
        "key": "C",
        "scale_type": "MAJOR",
        "complexity": 0.5,
        "duration": 4.0
    }

    # Create a response from the database model
    response = ChordProgressionResponse.from_db_model(db_model)

    # Verify fields
    assert response.id == "507f1f77bcf86cd799439011"
    assert response.name == "Test Progression"
    assert len(response.chords) == 1
    assert response.chords[0].chord_symbol == "C"
    assert response.chords[0].duration == 1.0
    assert response.scale_info.key == "C"
    assert response.scale_info.scale_type == ScaleType.MAJOR
    assert response.key == "C"
    assert response.scale_type == ScaleType.MAJOR
    assert response.complexity == 0.5
    assert response.duration == 4.0


def test_chord_progression_response_to_json():
    """Test converting a response to JSON."""
    # Create a scale info
    scale_info = ScaleInfo(
        key="C",
        scale_type=ScaleType.MAJOR
    )

    # Create a chord progression item
    chord_item = ChordProgressionItem(
        chord_symbol="C",
        duration=1.0
    )

    # Create a response
    response = ChordProgressionResponse(
        id="507f1f77bcf86cd799439011",
        name="Test Progression",
        chords=[chord_item],
        scale_info=scale_info,
        key="C",
        scale_type=ScaleType.MAJOR,
        complexity=0.5,
        duration=4.0
    )

    # Convert to JSON
    json_data = response.to_json()

    # Verify JSON data
    assert json_data["id"] == "507f1f77bcf86cd799439011"
    assert json_data["name"] == "Test Progression"
    assert len(json_data["chords"]) == 1
    assert json_data["chords"][0]["chord_symbol"] == "C"
    assert json_data["chords"][0]["duration"] == 1.0
    assert json_data["scale_info"]["key"] == "C"
    assert json_data["scale_info"]["scale_type"] == "MAJOR"
    assert json_data["key"] == "C"
    assert json_data["scale_type"] == "MAJOR"
    assert json_data["complexity"] == 0.5
    assert json_data["duration"] == 4.0
