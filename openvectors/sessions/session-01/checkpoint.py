"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    x, t = L.crossing(4.0, 0.0, 2.0)
    checks.append(("worked example: boat 4 m/s straight across, current 2 m/s, 60 m: lands 30 m downstream after 15 s",
                   abs(x - 30.0) < 1e-9 and abs(t - 15.0) < 1e-9))
    a = L.add([3.0, 0.0], [0.0, 4.0])
    checks.append(("(3, 0) + (0, 4) = (3, 4) with length 5", np.allclose(a, [3.0, 4.0]) and abs(L.length(a) - 5.0) < 1e-12))
    p, q = np.array([1.0, 2.0]), np.array([-3.0, 0.5])
    checks.append(("a + b = b + a", np.allclose(L.add(p, q), L.add(q, p))))
    h = L.heading_to_land_opposite(4.0, 2.0)
    checks.append(("heading 30 degrees upstream lands exactly opposite", abs(h - 30.0) < 1e-9 and abs(L.crossing(4.0, h, 2.0)[0]) < 1e-9))
    x30, t30 = L.crossing(4.0, 30.0, 2.0)
    checks.append(("that crossing takes 17.32 s (= 60 / (4 cos 30))", abs(t30 - 60.0 / (4.0 * np.cos(np.radians(30)))) < 1e-9 and abs(t30 - 17.32) < 0.01))
    checks.append(("boat arrow keeps the boat speed for every heading",
                   all(abs(L.length(L.boat_velocity(4.0, d)) - 4.0) < 1e-12 for d in range(-60, 61, 15))))
    checks.append(("no current: straight heading lands straight across", abs(L.crossing(4.0, 0.0, 0.0)[0]) < 1e-12))
    checks.append(("current equal to boat speed: no heading cancels it", L.heading_to_land_opposite(2.0, 2.0) is None))
    try:
        L.crossing(4.0, 90.0, 2.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("heading 90 degrees (along the bank) never crosses: error raised", ok))
    x15, t15 = L.crossing(4.0, 15.0, 2.0)
    checks.append(("design answer: heading 15 degrees lands about 15 m downstream (14.98 m) after 15.53 s", abs(x15 - 14.98) < 0.01 and abs(t15 - 15.53) < 0.01))
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
