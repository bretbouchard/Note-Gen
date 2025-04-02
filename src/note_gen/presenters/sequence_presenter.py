"""
Presenter for sequence data.

This presenter formats sequence data for API responses,
ensuring a clean separation between the business logic and the presentation layer.
"""

from typing import List, Dict, Any, Union

from src.note_gen.models.sequence import Sequence
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.note import Note


class SequencePresenter:
    """Presenter for sequence data."""

    @staticmethod
    def present_sequence(sequence: Sequence) -> Dict[str, Any]:
        """
        Format a sequence for API response.

        Args:
            sequence: The sequence to format

        Returns:
            Formatted sequence data
        """
        return {
            "id": str(sequence.id) if hasattr(sequence, "id") else None,
            "name": sequence.name,
            "metadata": sequence.metadata if hasattr(sequence, "metadata") else {},
        }

    @staticmethod
    def present_note_sequence(sequence: NoteSequence) -> Dict[str, Any]:
        """
        Format a note sequence for API response.

        Args:
            sequence: The note sequence to format

        Returns:
            Formatted note sequence data
        """
        base_data = SequencePresenter.present_sequence(sequence)
        
        # Add note sequence specific data
        base_data.update({
            "notes": SequencePresenter._format_notes(sequence.notes),
            "type": "note_sequence",
        })
        
        return base_data

    @staticmethod
    def present_many_sequences(sequences: List[Sequence]) -> List[Dict[str, Any]]:
        """
        Format multiple sequences for API response.

        Args:
            sequences: The sequences to format

        Returns:
            List of formatted sequence data
        """
        return [SequencePresenter.present_sequence(seq) for seq in sequences]

    @staticmethod
    def present_many_note_sequences(sequences: List[NoteSequence]) -> List[Dict[str, Any]]:
        """
        Format multiple note sequences for API response.

        Args:
            sequences: The note sequences to format

        Returns:
            List of formatted note sequence data
        """
        return [SequencePresenter.present_note_sequence(seq) for seq in sequences]

    @staticmethod
    def _format_notes(notes: List[Note]) -> List[Dict[str, Any]]:
        """
        Format note data for API response.

        Args:
            notes: The notes to format

        Returns:
            List of formatted note data
        """
        return [
            {
                "note_name": note.note_name,
                "octave": note.octave,
                "duration": note.duration,
                "velocity": note.velocity,
                "position": note.position,
            }
            for note in notes
        ]
