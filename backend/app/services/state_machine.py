from typing import Dict

# Valid transitions map
TRANSITIONS: Dict[str, list] = {
    "OPEN":          ["INVESTIGATING"],
    "INVESTIGATING": ["RESOLVED"],
    "RESOLVED":      ["CLOSED"],
    "CLOSED":        []
}

class InvalidTransitionError(Exception):
    pass

class WorkItemStateMachine:
    def __init__(self, current_status: str):
        self.current = current_status

    def can_transition(self, new_status: str) -> bool:
        return new_status in TRANSITIONS.get(self.current, [])

    def transition(self, new_status: str) -> str:
        if not self.can_transition(new_status):
            raise InvalidTransitionError(
                f"Cannot move from {self.current} → {new_status}. "
                f"Allowed: {TRANSITIONS.get(self.current, [])}"
            )
        self.current = new_status
        return self.current