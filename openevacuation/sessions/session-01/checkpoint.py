"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("flow = density x speed x width: 2.0 persons/m2 x 0.65 m/s x 1 m = 1.3 persons/s",
                   abs(L.crowd_flow(2.0, 0.65, 1.0) - 1.3) < 1e-12))
    checks.append(("units: doubling the width doubles the flow", abs(L.crowd_flow(2.0, 0.65, 2.0) - 2 * L.crowd_flow(2.0, 0.65, 1.0)) < 1e-12))
    checks.append(("effective width of a 1.2 m door is 0.9 m", abs(L.effective_width(1.2) - 0.9) < 1e-12))
    checks.append(("worked example: a 1.2 m door passes 1.3 x 0.9 = 1.17 persons/s", abs(L.door_flow(1.2) - 1.17) < 1e-12))
    te = L.evacuation_time(240, 1.2)
    hand = 60 + 20 / 1.2 + 240 / 1.17
    checks.append((f"worked example: 240 people, one 1.2 m door: {te:.1f} s = 60 + 16.7 + 205.1 s", abs(te - hand) < 1e-9 and abs(te - 281.8) < 0.1))
    te2 = L.evacuation_time(240, 1.2, n_doors=2)
    checks.append((f"two doors halve only the queue time: {te2:.1f} s", abs((te - te2) - 240 / 1.17 / 2) < 1e-9))
    checks.append(("limit: with nobody inside only pre-movement and walking remain", abs(L.evacuation_time(0, 1.2) - (60 + 20 / 1.2)) < 1e-12))
    checks.append(("a wider door never makes the evacuation slower",
                   all(L.evacuation_time(240, w + 0.1) < L.evacuation_time(240, w) for w in np.arange(0.4, 3.0, 0.1))))
    t = np.linspace(0, 400, 801)
    left = L.people_left(t, 240, 1.2)
    checks.append(("people inside never increase and start at 240", left[0] == 240 and np.all(np.diff(left) <= 1e-12)))
    checks.append(("everyone is out exactly at the evacuation time",
                   L.people_left(te + 1e-6, 240, 1.2) < 1e-4 and L.people_left(te - 1.0, 240, 1.2) > 1.0))
    checks.append(("the queue empties at the door flow (slope -1.17 persons/s)",
                   abs((L.people_left(150, 240, 1.2) - L.people_left(100, 240, 1.2)) / 50 + 1.17) < 1e-9))
    bad = 0
    for call in (lambda: L.effective_width(0.3), lambda: L.door_flow(1.2, 0), lambda: L.walk_time(10, 0),
                 lambda: L.crowd_flow(-1, 1, 1)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 4))
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
