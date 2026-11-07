"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    lo, hi = L.interval(12.3, 0.1)
    checks.append(("12.3 +- 0.1 is the interval 12.2 to 12.4", abs(lo - 12.2) < 1e-12 and abs(hi - 12.4) < 1e-12))
    area = L.rect_area(12.3, 8.4)
    amin, amax = L.area_extremes(12.3, 0.1, 8.4, 0.1)
    checks.append(("worked example: area 103.32, smallest 101.26, largest 105.40 cm^2",
                   abs(area - 103.32) < 5e-3 and abs(amin - 101.26) < 5e-3 and abs(amax - 105.40) < 5e-3))
    checks.append(("worked example: area error is about +-2.07 cm^2 (half-range)", abs((amax - amin) / 2 - 2.07) < 5e-3))
    rl, rw = L.relative_error(12.3, 0.1), L.relative_error(8.4, 0.1)
    checks.append(("relative errors are 0.81 % and 1.19 %", abs(100 * rl - 0.81) < 0.005 and abs(100 * rw - 1.19) < 0.005))
    checks.append(("relative error of the area is about the sum 2.0 % (hand calculation)",
                   abs((amax - amin) / 2 / area - (rl + rw)) < 5e-4 and abs(100 * (rl + rw) - 2.0) < 0.01))
    checks.append(("half-range of readings 12.2, 12.4, 12.3, 12.3 is 0.1", abs(L.half_range([12.2, 12.4, 12.3, 12.3]) - 0.1) < 1e-12))
    z_lo, z_hi = L.area_extremes(5.0, 0.0, 4.0, 0.0)
    checks.append(("edge: zero error gives a single value 20", z_lo == z_hi == 20.0))
    checks.append(("worst case is wider than the typical (quadrature) error 1.49 cm^2",
                   abs(np.hypot(8.4 * 0.1, 12.3 * 0.1) - 1.489) < 1e-3 and (amax - amin) / 2 > 1.489))
    b_lo, b_hi = L.area_extremes(20.0, 0.1, 5.0, 0.1)
    checks.append(("question B: 20.0 by 5.0 gives 97.51 to 102.51, half-range 2.50, relative 2.5 %",
                   abs(b_lo - 97.51) < 5e-3 and abs(b_hi - 102.51) < 5e-3 and abs((b_hi - b_lo) / 2 - 2.5) < 5e-3
                   and abs(100 * (b_hi - b_lo) / 2 / 100.0 - 2.5) < 5e-3))
    checks.append(("question C: the area band at W = 8.4 is 102.48 to 104.16, 1.68 tall",
                   abs(L.rect_area(12.2, 8.4) - 102.48) < 5e-3 and abs(L.rect_area(12.4, 8.4) - 104.16) < 5e-3
                   and abs(L.rect_area(12.4, 8.4) - L.rect_area(12.2, 8.4) - 1.68) < 5e-3))
    h = lambda dl, dw: (lambda e: (e[1] - e[0]) / 2)(L.area_extremes(12.3, dl, 8.4, dw))
    checks.append(("question D: halving the width error gives 1.455, halving the length error 1.65 (width first)",
                   abs(h(0.1, 0.05) - 1.455) < 5e-3 and abs(h(0.05, 0.1) - 1.65) < 5e-3 and h(0.1, 0.05) < h(0.05, 0.1)))
    checks.append(("app challenge: errors of 0.04 cm on both sides give 0.83 cm^2, below 1", abs(h(0.04, 0.04) - 0.828) < 5e-3))
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
