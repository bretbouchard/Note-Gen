"""
Controller for import/export operations.

This controller handles importing and exporting data from the application.
It provides methods to export data to various formats and import data from files.
"""

import json
import csv
import io
from typing import Dict, Any, List, Union, Optional, BinaryIO, TextIO
from fastapi import UploadFile

from note_gen.database.repositories.base import BaseRepository
from note_gen.database.repositories.chord_progression_repository import ChordProgressionRepository
from note_gen.database.repositories.note_pattern_repository import NotePatternRepository
from note_gen.database.repositories.rhythm_pattern_repository import RhythmPatternRepository
from note_gen.database.repositories.sequence_repository import SequenceRepository
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.patterns import NotePattern, Pattern
from note_gen.models.rhythm import RhythmPattern
from note_gen.models.note_sequence import NoteSequence
from note_gen.models.sequence import Sequence


class ImportExportController:
    """Controller for import/export operations."""

    def __init__(
        self,
        chord_progression_repository: BaseRepository,
        note_pattern_repository: BaseRepository,
        rhythm_pattern_repository: BaseRepository,
        sequence_repository: BaseRepository
    ):
        """
        Initialize the import/export controller.

        Args:
            chord_progression_repository: Repository for chord progressions
            note_pattern_repository: Repository for note patterns
            rhythm_pattern_repository: Repository for rhythm patterns
            sequence_repository: Repository for sequences
        """
        self.chord_progression_repository = chord_progression_repository
        self.note_pattern_repository = note_pattern_repository
        self.rhythm_pattern_repository = rhythm_pattern_repository
        self.sequence_repository = sequence_repository

    async def export_chord_progressions(self, format: str = "json") -> Union[str, bytes]:
        """
        Export all chord progressions.

        Args:
            format: The export format (json or csv)

        Returns:
            Union[str, bytes]: The exported data
        """
        progressions = await self.chord_progression_repository.find_all()

        if format.lower() == "json":
            return self._export_to_json(progressions)
        elif format.lower() == "csv":
            return self._export_to_csv(progressions)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def export_note_patterns(self, format: str = "json") -> Union[str, bytes]:
        """
        Export all note patterns.

        Args:
            format: The export format (json or csv)

        Returns:
            Union[str, bytes]: The exported data
        """
        patterns = await self.note_pattern_repository.find_all()

        if format.lower() == "json":
            return self._export_to_json(patterns)
        elif format.lower() == "csv":
            return self._export_to_csv(patterns)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def export_rhythm_patterns(self, format: str = "json") -> Union[str, bytes]:
        """
        Export all rhythm patterns.

        Args:
            format: The export format (json or csv)

        Returns:
            Union[str, bytes]: The exported data
        """
        patterns = await self.rhythm_pattern_repository.find_all()

        if format.lower() == "json":
            return self._export_to_json(patterns)
        elif format.lower() == "csv":
            return self._export_to_csv(patterns)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def export_sequences(self, format: str = "json") -> Union[str, bytes]:
        """
        Export all sequences.

        Args:
            format: The export format (json or csv)

        Returns:
            Union[str, bytes]: The exported data
        """
        sequences = await self.sequence_repository.find_all()

        if format.lower() == "json":
            return self._export_to_json(sequences)
        elif format.lower() == "csv":
            return self._export_to_csv(sequences)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def import_chord_progressions(self, file: UploadFile) -> int:
        """
        Import chord progressions from a file.

        Args:
            file: The file to import from

        Returns:
            int: The number of imported items
        """
        content = await file.read()

        if file.filename.endswith(".json"):
            data = json.loads(content)
            return await self._import_from_json(data, ChordProgression, self.chord_progression_repository)
        elif file.filename.endswith(".csv"):
            return await self._import_from_csv(content.decode(), ChordProgression, self.chord_progression_repository)
        else:
            raise ValueError(f"Unsupported file format: {file.filename}")

    async def import_note_patterns(self, file: UploadFile) -> int:
        """
        Import note patterns from a file.

        Args:
            file: The file to import from

        Returns:
            int: The number of imported items
        """
        content = await file.read()

        if file.filename.endswith(".json"):
            data = json.loads(content)
            return await self._import_from_json(data, NotePattern, self.note_pattern_repository)
        elif file.filename.endswith(".csv"):
            return await self._import_from_csv(content.decode(), NotePattern, self.note_pattern_repository)
        else:
            raise ValueError(f"Unsupported file format: {file.filename}")

    async def import_rhythm_patterns(self, file: UploadFile) -> int:
        """
        Import rhythm patterns from a file.

        Args:
            file: The file to import from

        Returns:
            int: The number of imported items
        """
        content = await file.read()

        if file.filename.endswith(".json"):
            data = json.loads(content)
            return await self._import_from_json(data, RhythmPattern, self.rhythm_pattern_repository)
        elif file.filename.endswith(".csv"):
            return await self._import_from_csv(content.decode(), RhythmPattern, self.rhythm_pattern_repository)
        else:
            raise ValueError(f"Unsupported file format: {file.filename}")

    async def import_sequences(self, file: UploadFile) -> int:
        """
        Import sequences from a file.

        Args:
            file: The file to import from

        Returns:
            int: The number of imported items
        """
        content = await file.read()

        if file.filename.endswith(".json"):
            data = json.loads(content)
            return await self._import_from_json(data, NoteSequence, self.sequence_repository)
        elif file.filename.endswith(".csv"):
            return await self._import_from_csv(content.decode(), NoteSequence, self.sequence_repository)
        else:
            raise ValueError(f"Unsupported file format: {file.filename}")

    def _export_to_json(self, items: List[Any]) -> str:
        """
        Export items to JSON.

        Args:
            items: The items to export

        Returns:
            str: The JSON string
        """
        # Convert items to dictionaries
        item_dicts = [item.model_dump() for item in items]
        return json.dumps(item_dicts, indent=2)

    def _export_to_csv(self, items: List[Any]) -> bytes:
        """
        Export items to CSV.

        Args:
            items: The items to export

        Returns:
            bytes: The CSV data
        """
        if not items:
            return b""

        # Convert items to dictionaries
        item_dicts = [item.model_dump() for item in items]

        # Flatten nested dictionaries
        flattened_dicts = []
        for item in item_dicts:
            flattened = {}
            for key, value in item.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flattened[f"{key}_{sub_key}"] = sub_value
                elif isinstance(value, list):
                    flattened[key] = json.dumps(value)
                else:
                    flattened[key] = value
            flattened_dicts.append(flattened)

        # Handle empty list case
        if not flattened_dicts:
            return b""

        # Write to CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=flattened_dicts[0].keys())
        writer.writeheader()
        writer.writerows(flattened_dicts)

        return output.getvalue().encode()

    async def _import_from_json(self, data: List[Dict[str, Any]], model_class: Any, repository: BaseRepository) -> int:
        """
        Import items from JSON.

        Args:
            data: The JSON data
            model_class: The model class to use
            repository: The repository to save to

        Returns:
            int: The number of imported items
        """
        count = 0
        for item_data in data:
            try:
                # Create model instance
                item = model_class.model_validate(item_data)

                # Save to repository
                await repository.save(item)
                count += 1
            except Exception as e:
                print(f"Error importing item: {str(e)}")

        return count

    async def _import_from_csv(self, csv_data: str, model_class: Any, repository: BaseRepository) -> int:
        """
        Import items from CSV.

        Args:
            csv_data: The CSV data
            model_class: The model class to use
            repository: The repository to save to

        Returns:
            int: The number of imported items
        """
        count = 0
        reader = csv.DictReader(io.StringIO(csv_data))

        for row in reader:
            try:
                # Unflatten nested dictionaries
                item_data = {}
                for key, value in row.items():
                    if "_" in key:
                        main_key, sub_key = key.split("_", 1)
                        if main_key not in item_data:
                            item_data[main_key] = {}
                        item_data[main_key][sub_key] = value
                    else:
                        # Try to parse JSON for list fields
                        try:
                            if value.startswith("[") and value.endswith("]"):
                                item_data[key] = json.loads(value)
                            else:
                                item_data[key] = value
                        except:
                            item_data[key] = value

                # Create model instance
                item = model_class.model_validate(item_data)

                # Save to repository
                await repository.save(item)
                count += 1
            except Exception as e:
                print(f"Error importing item: {str(e)}")

        return count

    @classmethod
    async def create(
        cls,
        chord_progression_repository: BaseRepository,
        note_pattern_repository: BaseRepository,
        rhythm_pattern_repository: BaseRepository,
        sequence_repository: BaseRepository
    ) -> 'ImportExportController':
        """
        Factory method to create an import/export controller.

        Args:
            chord_progression_repository: Repository for chord progressions
            note_pattern_repository: Repository for note patterns
            rhythm_pattern_repository: Repository for rhythm patterns
            sequence_repository: Repository for sequences

        Returns:
            ImportExportController: A new import/export controller instance
        """
        return cls(
            chord_progression_repository,
            note_pattern_repository,
            rhythm_pattern_repository,
            sequence_repository
        )
