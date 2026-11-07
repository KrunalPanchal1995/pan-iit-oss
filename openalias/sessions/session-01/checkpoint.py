"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: 28 rev/s at 30 fps turns 336 degrees per frame, seen as -24",
                   abs(L.step_angle_deg(28, 30) - 336.0) < 1e-9 and abs(L.fold_deg(336.0) + 24.0) < 1e-9))
    checks.append(("worked example: 28 rev/s at 30 fps looks like -2 rev/s (backwards)",
                   abs(L.apparent_frequency(28, 30) + 2.0) < 1e-9 and L.direction(28, 30) == "backwards"))
    checks.append(("hand calculation: 33 rev/s at 24 fps is seen as +9 rev/s (135 degrees per frame)",
                   abs(L.fold_deg(L.step_angle_deg(33, 24)) - 135.0) < 1e-9 and abs(L.apparent_frequency(33, 24) - 9.0) < 1e-9))
    checks.append(("a slow wheel is seen correctly (3 rev/s at 30 fps)", abs(L.apparent_frequency(3, 30) - 3.0) < 1e-9))
    checks.append(("wheel turning exactly fs rev/s looks frozen", L.direction(30, 30) == "frozen" and abs(L.apparent_frequency(60, 30)) < 1e-9))
    checks.append(("exactly fs/2 is the flicker limit: |apparent| = 15 rev/s at 30 fps",
                   abs(abs(L.apparent_frequency(15, 30)) - 15.0) < 1e-9 and L.direction(15, 30) == "flicker"))
    seen = [L.apparent_frequency(x, 30) for x in np.linspace(0, 200, 401)]
    checks.append(("apparent speed never exceeds fs/2 in size", max(abs(s) for s in seen) <= 15.0 + 1e-9))
    checks.append(("speeds f and f + fs look the same", abs(L.apparent_frequency(7.0, 30) - L.apparent_frequency(37.0, 30)) < 1e-9))
    fr = L.marker_angles(25, 30, 4)
    checks.append(("25 rev/s at 30 fps: marker sits at 0, 300, 240, 180 degrees", np.allclose(fr, [0, 300, 240, 180])))
    checks.append(("design: 29 rev/s looks +1 rev/s at 28 fps, 0 at 29 fps, -1 at 30 fps",
                   abs(L.apparent_frequency(29, 28) - 1.0) < 1e-9 and L.direction(29, 29) == "frozen"
                   and abs(L.apparent_frequency(29, 30) + 1.0) < 1e-9))
    checks.append(("design: 29 rev/s looks +5, +4 and +29 rev/s at 24, 25 and 60 fps (60 fps is above 2 x 29 and shows the truth)",
                   [round(L.apparent_frequency(29, r), 9) for r in (24, 25, 60)] == [5.0, 4.0, 29.0]))
    checks.append(("a wheel at 25 rev/s filmed at 30 fps seems to turn at -5 rev/s: backwards", L.direction(25, 30) == "backwards"))
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
