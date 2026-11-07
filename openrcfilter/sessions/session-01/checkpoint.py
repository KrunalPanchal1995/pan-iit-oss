"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("tau = R * C: 10 kohm and 3.2 uF give 32 ms", abs(L.time_constant(10e3, 3.2e-6) - 0.032) < 1e-12))
    slow, jit = L.survivors(10e3, 3.2e-6)
    checks.append(("worked example: R = 10 kohm, C = 3.2 uF keeps 0.93 of the slow signal and 0.12 of the jitter",
                   abs(slow - 0.928) < 0.01 and abs(jit - 0.123) < 0.01))
    d = L.delay_seconds(10e3, 3.2e-6)
    checks.append(("worked example: the slow wave is about 30 ms late", abs(d - 0.030) < 0.002))
    t = L.make_time(1.0)
    x = L.noisy_signal(t)
    y = L.rc_smooth(x, 1.0 / L.FS, 0.0001)
    checks.append(("a tiny tau changes almost nothing (output follows input)", float(np.max(np.abs(y - x))) < 0.05))
    flat = L.rc_smooth(np.full(2000, 3.0), 1.0 / L.FS, 0.05)
    checks.append(("a constant input stays constant (a filter does not invent a signal)", np.allclose(flat, 3.0)))
    s1, j1 = L.survivors(10e3, 1e-6)
    s2, j2 = L.survivors(10e3, 10e-6)
    checks.append(("a bigger C keeps less jitter and less slow signal", j2 < j1 and s2 < s1))
    checks.append(("jitter always suffers more than the slow signal", j1 < s1 and j2 < s2))
    checks.append(("more smoothing means more delay", L.delay_seconds(10e3, 10e-6) > L.delay_seconds(10e3, 1e-6)))
    checks.append(("no smoothing for a very small tau: nothing lost, no delay",
                   L.survivors(1e3, 0.1e-6)[0] > 0.999 and L.delay_seconds(1e3, 0.1e-6) < 1e-3))
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
