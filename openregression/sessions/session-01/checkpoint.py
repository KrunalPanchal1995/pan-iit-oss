"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    x3, y3 = np.array([1.0, 2.0, 3.0]), np.array([2.0, 2.0, 5.0])
    a3, b3 = L.best_line(x3, y3)
    checks.append(("worked example: three dots (1,2), (2,2), (3,5) give y = 0 + 1.5 x", abs(a3) < 1e-9 and abs(b3 - 1.5) < 1e-9))
    checks.append(("worked example: its residuals are 0.5, -1, 0.5 and total squared miss 1.5",
                   np.allclose(L.residuals(a3, b3, x3, y3), [0.5, -1.0, 0.5]) and abs(L.sse(a3, b3, x3, y3) - 1.5) < 1e-9))
    a, b = L.best_line(L.RAIN, L.YIELD)
    checks.append((f"farm data: best line is 0.887 + 0.344 x (got {a:.3f} + {b:.3f} x)", abs(a - 0.887) < 5e-4 and abs(b - 0.3441) < 5e-4))
    checks.append(("the best line matches np.polyfit", np.allclose([b, a], np.polyfit(L.RAIN, L.YIELD, 1), atol=1e-9)))
    checks.append(("residuals of the best line add up to zero", abs(L.residuals(a, b, L.RAIN, L.YIELD).sum()) < 1e-9))
    checks.append(("best line: total squared miss is 0.378 (t/ha)^2", abs(L.sse(a, b, L.RAIN, L.YIELD) - 0.378) < 5e-4))
    checks.append(("guess line 1.0 + 0.30 x: total squared miss is 0.706 (t/ha)^2", abs(L.sse(1.0, 0.30, L.RAIN, L.YIELD) - 0.706) < 5e-4))
    checks.append(("brute-force scan finds the same slope, 0.344", abs(L.scan_best_slope(L.RAIN, L.YIELD) - b) < 2e-3))
    rng = np.random.default_rng(0)
    worse = all(L.sse(a + da, b + db, L.RAIN, L.YIELD) > L.sse(a, b, L.RAIN, L.YIELD)
                for da, db in rng.normal(0, 0.1, (200, 2)))
    checks.append(("200 random nudges of the best line all make the miss larger", worse))
    checks.append(("forecast: 600 mm of rain gives 2.95 t/ha", abs(float(L.predict(a, b, 6.0)) - 2.95) < 5e-3))
    checks.append(("edge: two dots are fitted exactly (zero miss)", L.sse(*L.best_line([1, 2], [3, 7]), [1, 2], [3, 7]) < 1e-18))
    a2, b2 = L.best_line([0, 1, 2], [2, 1, 6])
    checks.append(("question B: dots (0,2), (1,1), (2,6) give y = 1 + 2 x with total squared miss 6",
                   abs(a2 - 1) < 1e-9 and abs(b2 - 2) < 1e-9 and abs(L.sse(a2, b2, [0, 1, 2], [2, 1, 6]) - 6) < 1e-9))
    checks.append(("any line through (x-bar, y-bar) has residuals adding to zero, whatever the slope",
                   abs(L.residuals(L.YIELD.mean() - 0.1 * L.RAIN.mean(), 0.1, L.RAIN, L.YIELD).sum()) < 1e-9))
    checks.append(("question D: 3.5 t/ha needs rain (3.5 - 0.887) / 0.344 = 7.59, inside the data range 3.0 to 9.2",
                   abs((3.5 - a) / b - 7.59) < 0.01 and L.RAIN.min() <= 7.59 <= L.RAIN.max()))
    checks.append(("app challenge: a = 0.9, b = 0.34 gives a total squared miss below 0.45 (0.380)", abs(L.sse(0.9, 0.34, L.RAIN, L.YIELD) - 0.380) < 5e-4))
    checks.append(("bowl view: the lowest total miss over slopes is 0.378 at slope 0.344", abs(L.sse_for_slope(b, L.RAIN, L.YIELD) - 0.378) < 5e-4))
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
