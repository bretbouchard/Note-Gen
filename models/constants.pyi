"""Module defining musical constants, including scale intervals."""

from typing import Dict, List

SCALE_INTERVALS: Dict[str, List[int]] = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'natural_minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'locrian': [0, 1, 3, 5, 6, 8, 10],
    'ionian': [0, 2, 4, 5, 7, 9, 11],
    'aeolian': [0, 2, 3, 5, 7, 8, 10],
    'harmonic_major': [0, 2, 4, 5, 7, 8, 11],
    'double_harmonic_major': [0, 1, 4, 5, 7, 8, 11],
    'whole_tone': [0, 2, 4, 6, 8, 10, 10],
    'octatonic_half_whole': [0, 1, 3, 4, 6, 7, 9, 10],
    'octatonic_whole_half': [0, 2, 3, 5, 6, 8, 9, 11]
}