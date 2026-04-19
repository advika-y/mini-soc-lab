from typing import TypedDict, Literal

# Structural aliases for the activity tracking dicts in detector.py.
ActivityRecord = tuple[float, int | None]   # (timestamp, dest_port)
AttackRecord = tuple[str, float]            # (attack_type, timestamp)

ActionLiteral = Literal[
    "BLOCKED",
    "ALERT",
    "Repeat Offender Detected",
    "Stealthy Attack Detected",
    "Distributed Attack Detected",
    "Multi-Stage Attack Detected",
]

class Alert(TypedDict):
    ip: str
    type: str
    score: int
    country: str
    action: ActionLiteral
    timestamp: int