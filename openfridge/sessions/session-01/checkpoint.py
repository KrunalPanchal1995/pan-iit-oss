"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    qh = L.heat_to_room(300.0, 100.0)
    checks.append((f"worked example: 300 J removed with 100 J of work gives Q_hot = 400 J (got {qh:.0f})", abs(qh - 400.0) < 1e-9))
    checks.append(("worked example: COP of that cycle is 3", abs(L.cop(300.0, 100.0) - 3.0) < 1e-9))
    checks.append(("Q_hot is always larger than Q_cold when work is used", all(L.heat_to_room(q, w) > q for q in (1, 5, 40) for w in (0.1, 1, 3))))
    checks.append(("heat removed = COP x work", abs(L.cooling_from_work(2.0, 3.0) - 6.0) < 1e-12))
    checks.append(("round trip: cop(cooling_from_work(w, c), w) = c", abs(L.cop(L.cooling_from_work(1.5, 2.5), 1.5) - 2.5) < 1e-12))
    checks.append(("hand calculation: leak of 2.0 W/K over 21 K is 42 W", abs(L.wall_leak_watts(2.0, 25.0, 4.0) - 42.0) < 1e-9))
    checks.append(("no leak when the room is as cold as the inside", L.wall_leak_watts(2.0, 4.0, 4.0) == 0.0))
    try:
        L.cop(10.0, 0.0)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge case: zero work gives an error, not a number", raised))
    try:
        L.heat_to_room(-1.0, 1.0)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge case: negative amounts are rejected", raised))
    checks.append(("four parts are listed", len(L.PARTS) == 4))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
