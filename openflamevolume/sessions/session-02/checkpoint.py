"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: ZNCC([2, 4, 6], [11, 12, 13]) = 1 (same pattern, different brightness)",
                   abs(L.zncc([2, 4, 6], [11, 12, 13]) - 1.0) < 1e-12))
    checks.append(("worked example: parabola through 0.80, 0.95, 0.90 peaks at +0.25 px",
                   abs(L.subpixel_peak(0.80, 0.95, 0.90) - 0.25) < 1e-12))
    checks.append(("worked example: d = 40.25 px gives Z = 800 x 0.10 / 40.25 = 1.988 m",
                   abs(800 * 0.10 / (40 + L.subpixel_peak(0.80, 0.95, 0.90)) - 1.98758) < 1e-4))
    checks.append(("hand calculation: ZNCC([1, 2, 3], [3, 2, 1]) = -1 (a negative image)",
                   abs(L.zncc([1, 2, 3], [3, 2, 1]) + 1.0) < 1e-12))
    rng = np.random.default_rng(3)
    f = rng.random((9, 9))
    checks.append(("ZNCC ignores gain and offset: ZNCC(f, 2.5 f + 7) = 1", abs(L.zncc(f, 2.5 * f + 7.0) - 1.0) < 1e-12))
    checks.append(("ZNCC is symmetric and lies between -1 and 1",
                   abs(L.zncc(f, f.T) - L.zncc(f.T, f)) < 1e-12 and -1 <= L.zncc(f, f.T) <= 1))
    q = lambda s: 1.0 - 0.1 * (s - 0.3) ** 2
    checks.append(("an exact parabola is refined exactly: peak at 0.3 px", abs(L.subpixel_peak(q(-1), q(0), q(1)) - 0.3) < 1e-12))
    left = L.speckle_image((48, 96), seed=3)
    right = L.speckle_image((48, 96), shift=-5.3, seed=3)
    d, scores = L.match(left, right, 24, 50, 8, range(0, 11))
    checks.append((f"noise-free speckle pair: measured shift {d:.3f} px is within 0.05 px of the true 5.3 px", abs(d - 5.3) < 0.05))
    checks.append(("the best whole-pixel score is near 1 for a true match", scores.max() > 0.95))
    b0, s0 = L.shift_statistics(0.3, 0.0, half=7, trials=12)
    checks.append((f"no noise: bias {b0:+.4f} px is below 0.02 px (peak locking is small)", abs(b0) < 0.02))
    s_small = L.shift_statistics(0.3, 0.05, half=4, trials=30)[1]
    s_big = L.shift_statistics(0.3, 0.05, half=9, trials=30)[1]
    checks.append((f"statistics: a 19 px window has less spread ({s_big:.3f} px) than a 9 px window ({s_small:.3f} px)", s_big < s_small))
    s_lo = L.shift_statistics(0.3, 0.02, half=7, trials=30)[1]
    s_hi = L.shift_statistics(0.3, 0.08, half=7, trials=30)[1]
    checks.append((f"statistics: more noise gives more spread ({s_lo:.3f} px -> {s_hi:.3f} px)", s_hi > s_lo))
    bad = 0
    for call in (lambda: L.zncc(np.ones(9), f.ravel()[:9]), lambda: L.zncc([1, 2], [1, 2, 3]),
                 lambda: L.subpixel_peak(0.9, 0.5, 0.9)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs (flat window, size mismatch, no peak) raise ValueError", bad == 3))
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
