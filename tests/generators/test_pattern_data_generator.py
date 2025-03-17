from typing import Dict, Any


def generate_test_data() -> Dict[str, Any]:
    """Generate sample test data for patterns."""
    return {
        "pattern_name": "Test Pattern",
        "notes": ["C4", "E4", "G4"],  # Ensure notes field is included
        "intervals": [0, 4, 7],
        "description": "Test pattern description",
        "tags": ["test", "triad"],
        "complexity": 1.0
    }
