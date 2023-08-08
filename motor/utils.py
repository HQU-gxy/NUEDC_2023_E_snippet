from datetime import datetime

class Instant:
    time: datetime

    def __init__(self) -> None:
        self.time = datetime.now()

    def elapsed(self) -> float:
        return (datetime.now() - self.time).total_seconds()

    def reset(self) -> None:
        self.time = datetime.now()

    def elapsed_reset(self) -> float:
        elapsed = self.elapsed()
        self.reset()
        return elapsed


def hex_bytes(b: bytes) -> str:
    return " ".join('{:02x}'.format(x) for x in b)
