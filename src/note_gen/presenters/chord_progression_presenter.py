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
        result = {
            "id": str(progression.id) if hasattr(progression, "id") else None,
            "name": progression.name,
            "key": progression.key,
            "scale_type": progression.scale_type.value if hasattr(progression.scale_type, "value") else progression.scale_type,
        }

        # Add chords if available
        if progression.chords:
            result["chords"] = ChordProgressionPresenter._format_chords(progression.chords)

        # Add items if available
        if progression.items:
            result["items"] = ChordProgressionPresenter._format_items(progression.items)

        # Add description if available
        if progression.description:
            result["description"] = progression.description

        # Add tags if available
        if progression.tags:
            result["tags"] = progression.tags

        return result

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
                "quality": chord.quality.value if hasattr(chord.quality, "value") else chord.quality,
                "duration": chord.duration,
                "position": chord.position if hasattr(chord, "position") else None,
            }
            for chord in chords
        ]

    @staticmethod
    def _format_items(items: List[Any]) -> List[Dict[str, Any]]:
        """
        Format chord progression items for API response.

        Args:
            items: The chord progression items to format

        Returns:
            List of formatted chord progression item data
        """
        result = []
        for item in items:
            item_dict = {
                "chord_symbol": item.chord_symbol,
                "position": item.position,
            }

            # Add duration if available
            if hasattr(item, "duration"):
                item_dict["duration"] = item.duration

            # Add chord if available
            if hasattr(item, "chord") and item.chord:
                if hasattr(item.chord, "root") and hasattr(item.chord, "quality"):
                    item_dict["chord"] = {
                        "root": item.chord.root,
                        "quality": item.chord.quality.value if hasattr(item.chord.quality, "value") else item.chord.quality,
                    }
                else:
                    item_dict["chord"] = str(item.chord)

            result.append(item_dict)

        return result
