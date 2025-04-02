"""
Presenter for chord progression data.

This presenter formats chord progression data for API responses,
ensuring a clean separation between the business logic and the presentation layer.
"""

from typing import List, Dict, Any, Optional

from note_gen.models.chord_progression import ChordProgression
from note_gen.models.chord import Chord


class ChordProgressionPresenter:
    """Presenter for chord progression data."""

    @staticmethod
    def present(progression: ChordProgression) -> Dict[str, Any]:
        """
        Format a chord progression for API response.

        Args:
            progression: The chord progression to format

        Returns:
            Formatted chord progression data
        """
        return {
            "id": str(progression.id) if hasattr(progression, "id") else None,
            "name": progression.name,
            "key": progression.key,
            "scale_type": progression.scale_type,
            "chords": ChordProgressionPresenter._format_chords(progression.chords),
        }

    @staticmethod
    def present_many(progressions: List[ChordProgression]) -> List[Dict[str, Any]]:
        """
        Format multiple chord progressions for API response.

        Args:
            progressions: The chord progressions to format

        Returns:
            List of formatted chord progression data
        """
        return [ChordProgressionPresenter.present(prog) for prog in progressions]

    @staticmethod
    def _format_chords(chords: List[Chord]) -> List[Dict[str, Any]]:
        """
        Format chord data for API response.

        Args:
            chords: The chords to format

        Returns:
            List of formatted chord data
        """
        return [
            {
                "root": chord.root,
                "quality": chord.quality,
                "duration": chord.duration,
                "position": chord.position if hasattr(chord, "position") else None,
            }
            for chord in chords
        ]
