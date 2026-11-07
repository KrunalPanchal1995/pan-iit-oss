"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # hand calculation and worked example
    f1 = L.field([1.0, 0.0])
    checks.append(("hand calculation: at x = 1 m, v = 0 the arrow is (0, -4)", np.allclose(f1, [0.0, -4.0])))
    f2 = L.field([0.0, 2.0])
    checks.append(("hand calculation: at x = 0, v = 2 the arrow is (2, -0.8)", np.allclose(f2, [2.0, -0.8])))
    nx2 = np.array([0.0, 2.0]) + 0.1 * L.field([0.0, 2.0])
    checks.append(("hand calculation: from (0, 2) one step of 0.1 s along the arrow lands at (0.2, 1.92)", np.allclose(nx2, [0.2, 1.92])))
    nxt = np.array([1.0, 0.0]) + 0.1 * L.field([1.0, 0.0])
    checks.append(("worked example: from (1, 0) one step of 0.1 s along the arrow lands at (1.0, -0.4)", np.allclose(nxt, [1.0, -0.4])))
    p = L.follow_arrows([1.0, 0.0], dt=0.1, n=1)
    checks.append(("follow_arrows with one step of 0.1 s gives the same point", np.allclose(p[1], nxt)))

    # the exact formula really solves the rule
    e = 1e-6
    wd = np.sqrt(4.0 - 0.4 ** 2 / 4)
    checks.append((f"the wobble frequency sqrt(k - c^2 / 4) is {wd:.2f} rad/s and the first zero crossing of x is at t = {(np.pi - np.arctan2(2 * wd, 0.4)) / wd:.3f} s",
                   abs(wd - 1.99) < 0.001 and abs(float(L.exact_position((np.pi - np.arctan2(2 * wd, 0.4)) / wd))) < 1e-12))
    checks.append(("the exact formula obeys the rule: its slope equals the arrow at every tested time",
                   all(np.allclose((L.exact_state(tt + e) - L.exact_state(tt - e)) / (2 * e), L.field(L.exact_state(tt)), atol=1e-6) for tt in (0.2, 1.3, 4.0))))
    checks.append(("the exact motion starts at (1, 0)", np.allclose(L.exact_state(0.0), [1.0, 0.0])))

    # following the arrows
    path = L.follow_arrows([1.0, 0.0])
    gap = abs(path[600, 0] - L.exact_position(3.0))
    checks.append((f"following the arrows with dt = 0.005 s is within 0.03 m of the exact position at 3 s (gap {gap:.3f})", gap < 0.03))
    checks.append(("friction makes the energy fall below a fifth of its start over 6 s", float(L.energy(path[-1])) < 0.2 * float(L.energy(path[0]))))
    checks.append(("edge: with no friction the exact energy stays 2.0 at all times",
                   all(abs(float(L.energy(L.exact_state(tt, c=0.0))) - 2.0) < 1e-12 for tt in (0.0, 0.7, 3.1))))
    checks.append(("edge: with no friction the mass is at x = -1 after half a swing (t = pi/2 s for k = 4)", abs(float(L.exact_position(np.pi / 2, c=0.0)) + 1.0) < 1e-12))
    try:
        L.exact_position(1.0, k=4.0, c=4.5)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: too much friction (c above 2 sqrt(k)) is refused with an error", raised))
    tt = np.linspace(0, 10, 400)
    env = np.exp(-0.2 * tt) * np.sqrt(1 + (0.4 / (2 * wd)) ** 2)
    checks.append(("the wobble never exceeds its envelope exp(-c t / 2) times a constant", bool(np.all(np.abs(L.exact_position(tt)) <= env + 1e-12))))

    # reading the rule from observations
    e25, e10 = L.arrow_error(0.25), L.arrow_error(0.1)
    checks.append((f"arrows read from points recorded every 0.25 s are within 3 percent of the rule (got {100 * e25:.1f} percent)", e25 < 0.03))
    checks.append((f"recording every 0.1 s is better still (got {100 * e10:.2f} percent)", e10 < 0.01 and e10 < e25))
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
