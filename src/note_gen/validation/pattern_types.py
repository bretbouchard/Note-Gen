"""Pattern-specific validation types."""
from typing import Protocol, runtime_checkable
from pydantic import BaseModel

@runtime_checkable
class PatternValidatable(Protocol):
    """Protocol for validatable patterns."""
    
    def validate_voice_leading(self) -> None:
        """Validate voice leading rules."""
        ...

    def validate_note_range(self) -> 'ValidationResult':
        """Validate note range."""
        ...

    def validate_consonance(self) -> None:
        """Validate consonance rules."""
        ...

    def validate_parallel_motion(self) -> None:
        """Validate parallel motion rules."""
        ...
