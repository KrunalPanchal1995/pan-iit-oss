"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("unit factor: 1 mm/h on 1 km2 is 1000 m3/h = 0.2778 m3/s",
                   abs(L.to_flow(1.0, 1.0) - 1000.0 / 3600.0) < 1e-9 and abs(L.to_flow(1.0, 1.0) - 0.2778) < 1e-4))
    checks.append(("rain slower than the soak-in rate gives no run-off", L.runoff_rate(4.0, 5.0) == 0.0))
    checks.append(("rain 10 mm/h on ground that swallows 5 mm/h gives 5 mm/h", L.runoff_rate(10.0, 5.0) == 5.0))
    # worked example: 60 mm in 1 h, f = 5 mm/h, 20 km2, K = 2 h
    q = L.to_flow(L.runoff_rate(60.0, 5.0), 20.0)
    pk = L.storm_peak(60.0, 1.0, 5.0)
    checks.append((f"worked example: run-off flow 305.6 m3/s and river peak 120.2 m3/s (got {q:.1f}, {pk:.1f})",
                   abs(q - 305.6) < 0.05 and abs(pk - 120.2) < 0.05 and abs(1 - np.exp(-0.5) - 0.3935) < 5e-5))
    q6 = L.to_flow(L.runoff_rate(10.0, 5.0), 20.0)
    pk6 = L.storm_peak(60.0, 6.0, 5.0)
    checks.append((f"hand calculation: the 6 h storm gives 27.78 m3/s * 0.9502 = 26.4 m3/s (got {pk6:.1f})",
                   abs(q6 - 27.78) < 0.005 and abs(1 - np.exp(-3) - 0.9502) < 5e-5 and abs(pk6 - 26.4) < 0.05))
    checks.append(("short intense storm beats long gentle storm with the same rain depth", pk > pk6))
    checks.append(("run-off volumes: 55 mm gives 1100 thousand m3, 30 mm gives 600 thousand m3",
                   abs(L.runoff_volume(60.0, 1.0, 5.0) - 1.1e6) < 1 and abs(L.runoff_volume(60.0, 6.0, 5.0) - 6.0e5) < 1))
    t, qs = L.simulate(60.0, 1.0, 5.0)
    checks.append(("time stepping agrees with the exact formula (peak within 0.5 percent)",
                   abs(qs.max() - pk) / pk < 0.005))
    checks.append(("all the run-off water reaches the river (mass kept, within 0.1 percent)",
                   abs(qs.sum() * 0.005 * 3600.0 - L.runoff_volume(60.0, 1.0, 5.0)) / 1.1e6 < 1e-3))
    checks.append(("ground that swallows everything gives zero flood", L.storm_peak(60.0, 6.0, 10.0) == 0.0))
    ds = np.linspace(0.5, 12, 40)
    pks = [L.storm_peak(60.0, d, 5.0) for d in ds]
    checks.append(("peak falls steadily as the same rain is spread over longer durations", bool(np.all(np.diff(pks) < 0))))
    checks.append(("exact hydrograph is continuous at the end of the storm",
                   abs(float(L.hydrograph(60.0, 1.0, 5.0, 1.0 + 1e-9)) - pk) < 1e-5))
    got = [L.storm_peak(60.0, 2.0, 5.0), L.storm_peak(60.0, 0.5, 5.0), L.storm_peak(60.0, 1.0, 0.0),
           L.storm_peak(60.0, 6.0, 0.0), L.storm_peak(60.0, 1.0, 10.0)]
    checks.append(("more peaks: 60 mm in 2 h gives 87.8, in 0.5 h gives 141.3; with f = 0 the 1 h and 6 h storms give 131.2 and 52.8; f = 10 turns the 1 h peak into 109.3 m3/s",
                   np.allclose(got, [87.8, 141.3, 131.2, 52.8, 109.3], atol=0.05)))
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
