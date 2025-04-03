"""Model for scale degree representation."""
from typing import Optional, Dict, Any
from pydantic import Field, model_validator
from note_gen.models.base import BaseModelWithConfig
from note_gen.core.enums import ChordQuality, ValidationLevel
from note_gen.core.constants import (
    SCALE_DEGREE_QUALITIES,
    INT_TO_ROMAN,
    ROMAN_TO_INT,
    DEFAULT_SCALE_DEGREE_QUALITIES
)
from note_gen.validation.base_validation import ValidationResult
from note_gen.validation.scale_degree_validation import validate_scale_degree

class ScaleDegree(BaseModelWithConfig):
    """Model for scale degrees."""

    value: int = Field(
        ...,
        ge=1,
        le=7,
        description="Scale degree value (1-7)"
    )
    quality: Optional[ChordQuality] = Field(
        default=ChordQuality.MAJOR,
        description="Chord quality for this scale degree"
    )

    def __init__(self, **data):
        """Initialize with default quality if not provided."""
        if 'quality' not in data and 'value' in data:
            data['quality'] = DEFAULT_SCALE_DEGREE_QUALITIES.get(
                data['value'],
                ChordQuality.MAJOR
            )
        super().__init__(**data)

    def to_roman(self) -> str:
        """Convert to roman numeral representation."""
        roman = INT_TO_ROMAN[self.value]
        return roman.lower() if self.quality == ChordQuality.MINOR else roman

    @classmethod
    def from_roman(cls, roman: str, quality: Optional[ChordQuality] = None) -> 'ScaleDegree':
        """
        Create from roman numeral.

        Args:
            roman: Roman numeral (I-VII or i-vii)
            quality: Optional chord quality (defaults to standard quality for the degree)

        Returns:
            ScaleDegree instance

        Raises:
            ValueError: If roman numeral is invalid
        """
        roman_upper = roman.upper()
        value = ROMAN_TO_INT.get(roman_upper)
        if value is None:
            raise ValueError(f"Invalid roman numeral: {roman}")

        # If quality not specified, infer from case
        if quality is None:
            quality = (
                ChordQuality.MINOR if roman.islower()
                else DEFAULT_SCALE_DEGREE_QUALITIES.get(value, ChordQuality.MAJOR)
            )

        return cls(value=value, quality=quality)

    def validate_with_rules(self, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate scale degree using validation rules.

        Args:
            level: Validation level to apply

        Returns:
            ValidationResult containing validation status and any errors/warnings
        """
        data = dict(value=self.value, quality=self.quality)
        return validate_scale_degree(data, level)

    @classmethod
    def validate_data(cls, data: Dict[str, Any], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate raw scale degree data.

        Args:
            data: Dictionary containing scale degree data
            level: Validation level to apply

        Returns:
            ValidationResult containing validation status and any errors/warnings
        """
        return validate_scale_degree(data, level)
