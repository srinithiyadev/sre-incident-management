import pytest
from datetime import datetime
from app.services.state_machine import WorkItemStateMachine, InvalidTransitionError

# ─── State Machine Tests ───────────────────────────────────────────────────────

def test_valid_transition_open_to_investigating():
    sm = WorkItemStateMachine("OPEN")
    result = sm.transition("INVESTIGATING")
    assert result == "INVESTIGATING"

def test_valid_transition_investigating_to_resolved():
    sm = WorkItemStateMachine("INVESTIGATING")
    result = sm.transition("RESOLVED")
    assert result == "RESOLVED"

def test_valid_transition_resolved_to_closed():
    sm = WorkItemStateMachine("RESOLVED")
    result = sm.transition("CLOSED")
    assert result == "CLOSED"

def test_invalid_transition_open_to_closed():
    sm = WorkItemStateMachine("OPEN")
    with pytest.raises(InvalidTransitionError):
        sm.transition("CLOSED")

def test_invalid_transition_open_to_resolved():
    sm = WorkItemStateMachine("OPEN")
    with pytest.raises(InvalidTransitionError):
        sm.transition("RESOLVED")

def test_invalid_transition_closed_to_open():
    sm = WorkItemStateMachine("CLOSED")
    with pytest.raises(InvalidTransitionError):
        sm.transition("OPEN")

def test_cannot_transition_from_closed():
    sm = WorkItemStateMachine("CLOSED")
    with pytest.raises(InvalidTransitionError):
        sm.transition("INVESTIGATING")

# ─── RCA Validation Tests ──────────────────────────────────────────────────────

def validate_rca(rca: dict) -> tuple[bool, str]:
    required = ["root_cause", "category", "fix_applied", "prevention_steps", "incident_start", "incident_end"]
    for field in required:
        if not rca.get(field):
            return False, f"Missing field: {field}"
    if rca["incident_end"] <= rca["incident_start"]:
        return False, "incident_end must be after incident_start"
    return True, "valid"

def test_valid_rca():
    rca = {
        "root_cause":       "DB connection pool exhausted",
        "category":         "Database Failure",
        "fix_applied":      "Restarted connection pool",
        "prevention_steps": "Add monitoring alert",
        "incident_start":   datetime(2026, 5, 1, 9, 0),
        "incident_end":     datetime(2026, 5, 1, 9, 45),
    }
    valid, msg = validate_rca(rca)
    assert valid is True

def test_rca_missing_root_cause():
    rca = {
        "root_cause":       "",
        "category":         "Database Failure",
        "fix_applied":      "Restarted connection pool",
        "prevention_steps": "Add monitoring alert",
        "incident_start":   datetime(2026, 5, 1, 9, 0),
        "incident_end":     datetime(2026, 5, 1, 9, 45),
    }
    valid, msg = validate_rca(rca)
    assert valid is False
    assert "root_cause" in msg

def test_rca_missing_fix_applied():
    rca = {
        "root_cause":       "DB failure",
        "category":         "Database Failure",
        "fix_applied":      "",
        "prevention_steps": "Add monitoring",
        "incident_start":   datetime(2026, 5, 1, 9, 0),
        "incident_end":     datetime(2026, 5, 1, 9, 45),
    }
    valid, msg = validate_rca(rca)
    assert valid is False

def test_rca_end_before_start():
    rca = {
        "root_cause":       "DB failure",
        "category":         "Database Failure",
        "fix_applied":      "Fixed it",
        "prevention_steps": "Add monitoring",
        "incident_start":   datetime(2026, 5, 1, 10, 0),
        "incident_end":     datetime(2026, 5, 1, 9, 0),
    }
    valid, msg = validate_rca(rca)
    assert valid is False
    assert "incident_end" in msg

def test_mttr_calculation():
    start = datetime(2026, 5, 1, 9, 0)
    end   = datetime(2026, 5, 1, 9, 45)
    mttr  = (end - start).total_seconds() / 60
    assert mttr == 45.0
