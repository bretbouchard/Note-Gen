"""
Presenter for pattern data.

This presenter formats pattern data for API responses,
ensuring a clean separation between the business logic and the presentation layer.
"""

from typing import List, Dict, Any, Union

from note_gen.models.patterns import NotePattern
from note_gen.models.rhythm import RhythmPattern


class PatternPresenter:
    """Presenter for pattern data."""

    @staticmethod
    def present_note_pattern(pattern: NotePattern) -> Dict[str, Any]:
        """
        Format a note pattern for API response.

        Args:
            pattern: The note pattern to format

        Returns:
            Formatted note pattern data
        """
        return {
            "id": str(pattern.id) if hasattr(pattern, "id") else None,
            "name": pattern.name,
            "description": pattern.description if hasattr(pattern, "description") else None,
            "pattern": [note.model_dump() if hasattr(note, 'model_dump') else str(note) for note in pattern.pattern] if pattern.pattern else [],
            "tags": pattern.tags if hasattr(pattern, "tags") else [],
            "type": "note",
        }

    @staticmethod
    def present_rhythm_pattern(pattern: RhythmPattern) -> Dict[str, Any]:
        """
        Format a rhythm pattern for API response.

        Args:
            pattern: The rhythm pattern to format

        Returns:
            Formatted rhythm pattern data
        """
        return {
            "id": str(pattern.id) if hasattr(pattern, "id") else None,
            "name": pattern.name,
            "description": pattern.description if hasattr(pattern, "description") else None,
            "pattern": [note.model_dump() if hasattr(note, 'model_dump') else str(note) for note in pattern.pattern] if pattern.pattern else [],
            "tags": pattern.tags if hasattr(pattern, "tags") else [],
            "type": "rhythm",
        }

    @staticmethod
    def present_pattern(
        pattern: Union[NotePattern, RhythmPattern]
    ) -> Dict[str, Any]:
        """
        Format a pattern for API response.

        Args:
            pattern: The pattern to format

        Returns:
            Formatted pattern data
        """
        if isinstance(pattern, NotePattern):
            return PatternPresenter.present_note_pattern(pattern)
        elif isinstance(pattern, RhythmPattern):
            return PatternPresenter.present_rhythm_pattern(pattern)
        else:
            raise ValueError(f"Unknown pattern type: {type(pattern)}")

    @staticmethod
    def present_many_note_patterns(patterns: List[NotePattern]) -> List[Dict[str, Any]]:
        """
        Format multiple note patterns for API response.

        Args:
            patterns: The note patterns to format

        Returns:
            List of formatted note pattern data
        """
        return [PatternPresenter.present_note_pattern(pattern) for pattern in patterns]

    @staticmethod
    def present_many_rhythm_patterns(
        patterns: List[RhythmPattern]
    ) -> List[Dict[str, Any]]:
        """
        Format multiple rhythm patterns for API response.

        Args:
            patterns: The rhythm patterns to format

        Returns:
            List of formatted rhythm pattern data
        """
        return [PatternPresenter.present_rhythm_pattern(pattern) for pattern in patterns]

    @staticmethod
    def present_many_patterns(
        patterns: List[Union[NotePattern, RhythmPattern]]
    ) -> List[Dict[str, Any]]:
        """
        Format multiple patterns for API response.

        Args:
            patterns: The patterns to format

        Returns:
            List of formatted pattern data
        """
        return [PatternPresenter.present_pattern(pattern) for pattern in patterns]
