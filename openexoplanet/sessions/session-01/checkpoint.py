"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("a planet with Rp/Rs = 0.1 blocks 1 percent", abs(L.transit_depth(0.1) - 0.01) < 1e-12))
    checks.append(("worked example: Rp/Rs = 0.05 blocks 0.25 percent (0.0025)", abs(L.transit_depth(0.05) - 0.0025) < 1e-12))
    checks.append(("hand calculation: a planet half the star's radius covers 25 percent", abs(L.transit_depth(0.5) - 0.25) < 1e-12))
    checks.append(("worked example: dips at days 2, 7, 12 give a 5 day period", abs(L.period_from_dips(np.array([2.0, 7.0, 12.0])) - 5.0) < 1e-12))
    checks.append(("worked example: depth 0.0025 gives Rp/Rs = 0.05", abs(np.sqrt(0.0025) - 0.05) < 1e-12))

    t = np.arange(0.0, 12.0, 0.025)
    flat = L.box_dips(t, 3.0, 1.0, 0.15, 0.01)
    checks.append(("noise-free box light curve: brightest value is exactly 1.0", abs(flat.max() - 1.0) < 1e-12))
    checks.append(("noise-free box light curve: lowest value is 1 - depth = 0.99", abs(flat.min() - 0.99) < 1e-12))
    checks.append(("noise-free curve has 4 dips", len(L.find_dips(t, flat, 0.995)) == 4))

    t, flux = L.light_curve()
    checks.append(("the light curve has 480 measurements over 12 days", len(t) == 480))
    c = L.find_dips(t, flux, 0.995)
    checks.append(("noisy curve (seed 7): 4 dips found", len(c) == 4))
    checks.append(("dip centres are near days 1, 4, 7, 10", bool(np.allclose(c, [1.0, 4.0, 7.0, 10.0], atol=0.05))))
    checks.append(("period from the gaps is 3.00 days (within 0.02)", abs(L.period_from_dips(c) - 3.0) < 0.02))
    depth = L.depth_from_curve(t, flux, c, 0.15)
    checks.append((f"measured depth is about 0.01 (got {depth:.4f})", abs(depth - 0.01) < 0.0007))
    checks.append(("radius ratio from the measured depth is about 0.1", abs(np.sqrt(depth) - 0.1) < 0.004))

    # edge cases
    rng = np.random.default_rng(3)
    quiet = 1.0 + rng.normal(0.0, 0.0015, 480)
    checks.append(("pure noise: no dips found", len(L.find_dips(np.arange(480) * 0.025, quiet, 0.995)) == 0))
    checks.append(("a single dip gives no period (nan)", np.isnan(L.period_from_dips(np.array([4.0])))))
    checks.append(("a dip of only 2 points is ignored", len(L.find_dips(np.arange(10.0), np.array([1, 1, 0.9, 0.9, 1, 1, 1, 1, 1, 1.0]), 0.95)) == 0))
    checks.append(("a dip that runs to the end of the data is still found", len(L.find_dips(np.arange(6.0), np.array([1, 1, 1, 0.9, 0.9, 0.9]), 0.95)) == 1))
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
