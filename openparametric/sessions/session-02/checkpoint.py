"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    import math
    checks = []
    steel = L.MATERIALS["steel"]
    allow = steel["yield"] / 1.5
    ts = L.t_strength(500, 200, 40, allow)
    tf = L.t_stiffness(500, 200, 40, steel["E"], 1.0)
    checks.append((f"worked example: strength gives t = 9.78 mm (got {ts:.2f})", abs(ts - 9.78) < 0.01))
    checks.append((f"worked example: stiffness gives t = 12.40 mm (got {tf:.2f})", abs(tf - 12.40) < 0.01))
    d = L.design(500, 200, 40, 1.0, "steel")
    checks.append((f"worked example: stiffness governs and the plate is 15 mm (got {d['governing']}, {d['t']} mm)", d["governing"] == "stiffness" and d["t"] == 15))
    checks.append((f"worked example: mass 0.942 kg (got {d['mass']:.3f})", abs(d["mass"] - 0.942) < 0.001))
    checks.append((f"worked example: stress {d['stress']:.0f} MPa is within {allow:.0f} MPa and the sag {d['delta']:.2f} mm within 1 mm", d["stress"] <= allow and d["delta"] <= 1.0))
    da = L.design(500, 200, 40, 1.0, "aluminium")
    checks.append((f"worked example: aluminium needs 20 mm but weighs only 0.432 kg (got {da['t']} mm, {da['mass']:.3f} kg)", da["t"] == 20 and abs(da["mass"] - 0.432) < 0.001))
    checks.append(("the lightest material for this bracket is aluminium", L.lightest(500, 200, 40, 1.0)[0]["material"] == "aluminium"))
    lc = L.critical_length(500, 40, steel["E"], allow, 1.0)
    lo, hi = 10.0, 1000.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if L.t_strength(500, mid, 40, allow) > L.t_stiffness(500, mid, 40, steel["E"], 1.0):
            lo = mid                      # strength still asks for more: the crossing is at a longer length
        else:
            hi = mid
    checks.append((f"validation: the critical length 124.6 mm agrees with a bisection search (got {lc:.1f} and {hi:.1f})", abs(lc - hi) < 1e-6 * lc))
    checks.append(("below the critical length strength governs, above it stiffness governs",
                   L.design(500, 0.8 * lc, 40, 1.0)["governing"] == "strength" and L.design(500, 1.25 * lc, 40, 1.0)["governing"] == "stiffness"))
    ok = True
    for f, l, b, t, e in ((500, 200, 40, 12, 210000), (1200, 150, 30, 8, 69000), (80, 400, 60, 5, 210000)):
        ok &= abs(L.tip_deflection_numeric(f, l, b, t, e) - L.tip_deflection(f, l, b, t, e)) < 1e-5 * L.tip_deflection(f, l, b, t, e)
    checks.append(("validation: integrating the beam equation twice numerically gives the deflection formula to 0.001 percent for three plates", ok))
    checks.append(("doubling the load multiplies the strength thickness by sqrt(2) and the stiffness thickness by 2^(1/3)",
                   abs(L.t_strength(1000, 200, 40, allow) / L.t_strength(500, 200, 40, allow) - math.sqrt(2)) < 1e-12 and abs(L.t_stiffness(1000, 200, 40, 210000, 1) / L.t_stiffness(500, 200, 40, 210000, 1) - 2 ** (1 / 3)) < 1e-12))
    ok = True
    for f, l, b, dm in ((300, 100, 30, 0.5), (800, 180, 50, 2.0), (1500, 120, 60, 3.0), (200, 300, 40, 1.5)):
        for mat in ("steel", "aluminium"):
            try:
                r = L.design(f, l, b, dm, mat)
            except ValueError:
                continue
            m = L.MATERIALS[mat]
            ok &= r["t"] >= r["t_required"] - 1e-9 and r["t"] in L.PLATES and r["stress"] <= m["yield"] / 1.5 + 1e-9 and r["delta"] <= dm + 1e-9
    checks.append(("for 8 cases, the chosen plate is one that is sold, it is not thinner than required, and its stress and sag are within the limits", ok))
    for bad, label in ((lambda: L.design(500, 200, 40, 1.0, "wood"), "an unknown material"), (lambda: L.design(0, 200, 40, 1.0), "a load of zero"),
                       (lambda: L.design(500, 200, 40, 1.0, safety_factor=0.5), "a safety factor below 1"), (lambda: L.design(5000, 500, 20, 0.5, "aluminium"), "a requirement no plate can meet"),
                       (lambda: L.t_stiffness(500, 200, 40, 210000, 0), "an allowed sag of zero")):
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
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
