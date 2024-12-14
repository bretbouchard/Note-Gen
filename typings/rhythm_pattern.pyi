# rhythm_pattern.pyi


class RhythmNote:
    position: float
    duration: float
    velocity: float
    is_rest: bool
    accent: str | None
    swing_ratio: float | None

class RhythmPatternData:
    notes: list[RhythmNote]
    duration: float
    time_signature: str
    swing_enabled: bool
    swing_ratio: float
    groove_type: str | None
    variation_probability: float
    humanize_amount: float
    accent_pattern: list[str] | None

class RhythmPattern:
    name: str
    data: RhythmPatternData
    description: str | None
    tags: list[str]
    complexity: float
    style: str | None
    default_duration: float
    swing_enabled: bool
    swing_ratio: float