# chord.pyi

class Chord:
    def __init__(self, root: str, quality: str) -> None:
        ...
    def transpose(self, steps: int) -> None:
        ...
