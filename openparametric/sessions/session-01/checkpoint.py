"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    tau = L.allowable_shear(350, 2.5)
    checks.append((f"worked example: allowable shear stress 80.8 MPa (got {tau:.1f})", abs(tau - 80.78) < 0.01))
    s = L.design_shaft(200.0)
    checks.append((f"worked example: minimum diameter 23.28 mm (got {s['d_min']:.2f})", abs(s["d_min"] - 23.28) < 0.01))
    checks.append((f"worked example: standard size 25 mm (got {s['d']:g})", s["d"] == 25.0))
    checks.append((f"worked example: stress in the 25 mm shaft is 65.2 MPa (got {s['tau']:.1f})", abs(s["tau"] - 65.19) < 0.05))
    checks.append((f"worked example: actual safety factor 3.10 (got {s['sf_actual']:.2f})", abs(s["sf_actual"] - 3.098) < 0.005))
    checks.append((f"worked example: 15 kW at 1450 rpm is 98.8 N m (got {L.torque_from_power(15, 1450):.1f})", abs(L.torque_from_power(15, 1450) - 98.78) < 0.01))
    ok = True
    for t, sy, sf in ((50, 250, 1.5), (200, 350, 2.5), (1000, 600, 4.0), (5, 200, 3.0)):
        d = L.min_diameter(t, sy, sf)
        ok &= abs(L.shear_stress(t, d) - L.allowable_shear(sy, sf)) < 1e-9 * L.allowable_shear(sy, sf)
    checks.append(("validation: the stress in a shaft of exactly d_min equals the allowable stress (the rule inverts the stress formula)", ok))
    checks.append(("validation: doubling the torque multiplies d_min by 2^(1/3) = 1.26", abs(L.min_diameter(400, 350, 2.5) / L.min_diameter(200, 350, 2.5) - 2 ** (1 / 3)) < 1e-12))
    expected = [10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0]
    checks.append(("the R10 sizes from 10 to 100 mm are 10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100", L.preferred_sizes(10, 100) == expected))
    sizes = L.preferred_sizes(1, 1000)
    ratios = [b / a for a, b in zip(sizes, sizes[1:])]
    checks.append(("validation: neighbouring R10 sizes differ by a factor of about 1.26 (between 1.18 and 1.30)", all(1.18 < r < 1.30 for r in ratios)))
    checks.append(("a size that is exactly on the list stays: next_preferred(25) = 25 and next_preferred(25.01) = 31.5", L.next_preferred(25.0) == 25.0 and L.next_preferred(25.01) == 31.5))
    checks.append(("rounding goes up, not to the nearest: d_min = 20.4 gives 25 mm although 20 is nearer", L.next_preferred(20.4) == 25.0))
    ok = True
    for t in range(10, 1500, 37):
        r = L.design_shaft(float(t))
        ok &= r["d"] >= r["d_min"] and r["sf_actual"] >= 2.5 - 1e-9 and r["margin"] < 0.27
    checks.append(("for 40 torques, the standard shaft is never smaller than d_min, its safety factor is at least the one asked for and it is less than 27 percent oversize", ok))
    checks.append(("a stronger steel needs a smaller shaft", L.min_diameter(200, 500, 2.5) < L.min_diameter(200, 350, 2.5)))
    for bad, label in ((lambda: L.min_diameter(0, 350, 2.5), "zero torque"), (lambda: L.min_diameter(100, 350, 0.9), "a safety factor below 1"),
                       (lambda: L.shear_stress(100, 0), "a zero diameter"), (lambda: L.next_preferred(-5), "a negative diameter"),
                       (lambda: L.torque_from_power(15, 0), "a speed of zero"), (lambda: L.allowable_shear(-1, 2), "a negative yield strength")):
        try:
            bad()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
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
