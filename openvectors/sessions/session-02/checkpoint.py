"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    ho = L.heading_opposite(4.0, 2.0)
    checks.append(("worked example: boat 4 m/s, current 2 m/s, 60 m: heading 30 degrees, 17.32 s, drift 0",
                   abs(ho - 30.0) < 1e-9 and abs(L.crossing_time(4.0, 2.0, ho) - 17.32) < 0.01
                   and abs(L.drift(4.0, 2.0, ho)) < 1e-9))
    checks.append(("worked example: fastest crossing is straight across, 15 s, lands 30 m downstream",
                   abs(L.crossing_time(4.0, 2.0, 0.0) - 15.0) < 1e-9 and abs(L.drift(4.0, 2.0, 0.0) - 30.0) < 1e-9))
    hs = np.linspace(-60, 60, 1201)
    times = [L.crossing_time(4.0, 2.0, h) for h in hs]
    checks.append(("a grid search finds the minimum time at heading 0", abs(hs[int(np.argmin(times))]) < 1e-9))
    x = L.components(5.0, 36.8699)
    checks.append(("components of length 5 at 36.87 degrees are (4, 3)", np.allclose(x, [4.0, 3.0], atol=1e-3)))
    r, phi = L.polar(np.array([-1.0, 0.0]))
    checks.append(("polar form of (-1, 0) is length 1 at 180 degrees (arctan2 picks the quadrant)", abs(r - 1.0) < 1e-12 and abs(abs(phi) - 180.0) < 1e-9))
    checks.append(("polar and components undo each other",
                   np.allclose(L.components(*L.polar(np.array([-2.0, 3.0]))), [-2.0, 3.0], atol=1e-9)))
    checks.append(("dot product of perpendicular arrows is 0", abs(L.dot([2.0, 0.0], [0.0, 5.0])) < 1e-12))
    checks.append(("hand calculation: 20 N along x over (30, 60) m does 600 J",
                   abs(L.work(np.array([20.0, 0.0]), np.array([30.0, 60.0])) - 600.0) < 1e-9))
    checks.append(("angle between (1, 0) and (1, 1) is 45 degrees", abs(L.angle_between([1.0, 0.0], [1.0, 1.0]) - 45.0) < 1e-9))
    checks.append(("projection of (3, 4) on the x axis is 3", abs(L.projection_length([3.0, 4.0], [10.0, 0.0]) - 3.0) < 1e-12))
    # limits and edges
    checks.append(("current equal to the boat speed: no opposite heading", L.heading_opposite(3.0, 3.0) is None))
    checks.append(("just below the boat speed: heading close to 90 degrees", 80.0 < L.heading_opposite(3.0, 2.99) < 90.0))
    hb, db = L.smallest_drift(4.0, 5.0)
    hs2 = np.linspace(-80, 80, 3201)
    ds = [abs(L.drift(4.0, 5.0, h)) for h in hs2]
    checks.append(("current 5 > boat 4: smallest drift 45 m at 53.13 degrees, confirmed by grid search",
                   abs(db - 45.0) < 1e-9 and abs(hb - 53.1301) < 1e-3 and abs(min(ds) - 45.0) < 0.01))
    try:
        L.crossing_time(4.0, 2.0, 90.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("heading 90 degrees: error raised instead of dividing by zero", ok))
    ok1 = [h for h in np.arange(0, 60.0001, 0.001) if abs(L.drift(4.0, 2.0, h)) <= 5 and L.crossing_time(4.0, 2.0, h) <= 16]
    ok2 = [h for h in np.arange(0, 60.0001, 0.001) if abs(L.drift(4.0, 2.0, h)) <= 5 and L.crossing_time(4.0, 2.0, h) <= 17]
    checks.append(("design answer: no heading gives within 5 m and 16 s; allowing 17 s gives 25.1 to 28.1 degrees",
                   not ok1 and abs(min(ok2) - 25.1) < 0.05 and abs(max(ok2) - 28.1) < 0.05))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
