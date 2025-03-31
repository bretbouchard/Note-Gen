"""Validation module for enum consistency."""
from typing import Dict, Set, Type, Any, Optional
from enum import Enum
from src.note_gen.core.enums import (
    ScaleType, ChordQuality, TimeSignatureType, PatternDirection,
    AccentType, ValidationLevel, VoiceLeadingRule, PatternType,
    TransformationType, NoteModificationType
)
from src.note_gen.core.constants import (
    SCALE_INTERVALS, CHORD_INTERVALS, PATTERN_VALIDATION_LIMITS,
    PATTERN_DEFAULTS
)

class EnumValidator:
    """Validator for enum types and their relationships."""
    
    @staticmethod
    def validate_scale_type_intervals() -> None:
        """Validate that all scale types have corresponding intervals."""
        for scale_type in ScaleType:
            if scale_type not in SCALE_INTERVALS:
                raise ValueError(f"Missing intervals for scale type: {scale_type}")

    @staticmethod
    def validate_chord_quality_intervals() -> None:
        """Validate that all chord qualities have corresponding intervals."""
        for quality in ChordQuality:
            if quality.value not in CHORD_INTERVALS:
                raise ValueError(f"Missing intervals for chord quality: {quality}")

    @staticmethod
    def validate_time_signatures() -> None:
        """Validate time signature configurations."""
        valid_signatures = TimeSignatureType.get_valid_signatures()
        for signature, sig_type in valid_signatures.items():
            try:
                calculated_type = TimeSignatureType.validate(signature)
                if calculated_type != sig_type:
                    raise ValueError(f"Inconsistent time signature type for {signature}")
            except ValueError as e:
                raise ValueError(f"Invalid time signature configuration: {str(e)}")

    @staticmethod
    def validate_pattern_direction(direction: str) -> None:
        """Validate pattern direction."""
        if direction not in [d.value for d in PatternDirection]:
            raise ValueError(f"Invalid pattern direction: {direction}")

    @staticmethod
    def validate_pattern_type(pattern_type: str) -> None:
        """Validate pattern type."""
        if not PatternType.validate_pattern_type(pattern_type):
            raise ValueError(f"Invalid pattern type: {pattern_type}")

    @staticmethod
    def validate_transformation_type(transform_type: str) -> None:
        """Validate transformation type."""
        if transform_type not in [t.value for t in TransformationType]:
            raise ValueError(f"Invalid transformation type: {transform_type}")

    @staticmethod
    def validate_note_modification(mod_type: str, value: Any) -> None:
        """Validate note modification type and value."""
        try:
            enum_type = NoteModificationType(mod_type)
            if not NoteModificationType.validate_modification(enum_type, value):
                raise ValueError(f"Invalid modification value for type {mod_type}")
        except ValueError:
            raise ValueError(f"Invalid note modification type: {mod_type}")

    @staticmethod
    def validate_all_enums() -> None:
        """Validate all enum configurations."""
        EnumValidator.validate_scale_type_intervals()
        EnumValidator.validate_chord_quality_intervals()
        EnumValidator.validate_time_signatures()
