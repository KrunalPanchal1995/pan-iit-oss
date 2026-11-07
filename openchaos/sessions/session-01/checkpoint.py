"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    period = L.single_period(np.radians(2.0))
    hand = 2 * np.pi * np.sqrt(L.LEN / L.G)
    checks.append((f"worked example: small-swing period of a 1 m pendulum is 2 pi sqrt(L/g) = 2.006 s (got {period:.3f} s)",
                   abs(hand - 2.0061) < 1e-3 and abs(period - hand) < 0.005))

    # energy of the single pendulum (per kg, L = 1 m): E = omega^2 / 2 - g cos(theta)
    t, s = L.simulate(L.single_rate, [np.radians(120.0), 0.0], 20.0, 0.005)
    e = 0.5 * s[:, 1] ** 2 - L.G * np.cos(s[:, 0])
    checks.append(("single pendulum keeps its energy over 20 s (change below 1e-7 J/kg)", float(np.ptp(e)) < 1e-7))

    checks.append(("a double pendulum hanging at rest has zero acceleration",
                   bool(np.allclose(L.double_rate(np.array([0.0, 0.0, 0.0, 0.0])), 0.0))))

    # hand calculation of positions: both rods hanging, and both horizontal
    x1, y1, x2, y2 = L.tip_positions(np.array([[0.0, 0.0, 0.0, 0.0], [np.pi / 2, np.pi / 2, 0.0, 0.0]]))
    checks.append(("hand calculation: hanging balls at (0, -1) and (0, -2) m; horizontal balls at (1, 0) and (2, 0) m",
                   bool(np.allclose([x1[0], y1[0], x2[0], y2[0]], [0, -1, 0, -2]) and np.allclose([x1[1], y1[1], x2[1], y2[1]], [1, 0, 2, 0]))))
    _, s = L.simulate(L.double_rate, [2.0, 1.0, 0.0, 0.0], 5.0, 0.005)
    xa, ya, xb, yb = L.tip_positions(s)
    checks.append(("rods keep their 1 m length", bool(np.allclose(np.hypot(xa, ya), 1.0) and np.allclose(np.hypot(xb - xa, yb - ya), 1.0))))

    # predictable versus chaotic
    d = 1e-8
    t1, g1, _ = L.twin_gap(L.single_rate, [L.START, 0.0], d, 20.0)
    checks.append(("single pendulum: a 1e-8 rad difference stays below 1e-5 rad after 20 s", float(g1.max()) < 1e-5))
    t2, g2, _ = L.twin_gap(L.double_rate, [L.START, L.START, 0.0, 0.0], d, 20.0, index=1)
    first = L.first_time_above(t2, g2, 0.1)
    checks.append((f"double pendulum: the 1e-8 rad difference passes 0.1 rad between 10 and 16 s (got {first} s)",
                   first is not None and 10.0 < first < 16.0))
    checks.append(("double pendulum: the gap has grown by more than a factor of 1e7 by 20 s", float(g2[-1]) > 1e7 * d))

    # edge cases
    checks.append(("edge: first_time_above returns None when the limit is never reached", L.first_time_above(t1, g1, 1.0) is None))
    t0, g0, _ = L.twin_gap(L.double_rate, [0.0, 0.0, 0.0, 0.0], 0.0, 2.0)
    checks.append(("edge: zero difference gives zero gap", float(g0.max()) == 0.0))
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
