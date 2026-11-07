"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c = L.molar_concentration(35.0)
    checks.append(("worked example: 35 g/L of NaCl is 598.9 mol/m3", abs(c - 598.9) < 0.1))
    p = L.osmotic_pressure(35.0, 25.0)
    checks.append((f"worked example: seawater at 25 C has pi = {p:.0f} kPa (hand value 2969 kPa)", abs(p - 2969.2) < 1.0))
    checks.append(("hand calculation: pi = 2 x 598.9 x 8.314 x 298.15 / 1000",
                   abs(p - 2 * 35.0 / 58.44 * 1000 * 8.314 * 298.15 / 1000) < 1e-9))
    checks.append(("worked example: minimum energy 0.825 kWh/m3", abs(L.minimum_energy(35.0) - 0.8248) < 1e-3))
    checks.append(("units: 3600 kPa pushes 1 m3 with exactly 1 kWh", abs(L.kwh_per_m3(3600.0) - 1.0) < 1e-12))
    checks.append(("pure water has zero osmotic pressure and needs no energy",
                   L.osmotic_pressure(0.0) == 0.0 and L.minimum_energy(0.0) == 0.0))
    ratio = L.osmotic_pressure(70.0) / L.osmotic_pressure(35.0)
    checks.append(("doubling the salt doubles the osmotic pressure (linear law)", abs(ratio - 2.0) < 1e-12))
    tr = L.osmotic_pressure(35.0, 50.0) / L.osmotic_pressure(35.0, 0.0)
    checks.append(("osmotic pressure is proportional to absolute temperature (kelvin, not Celsius)",
                   abs(tr - 323.15 / 273.15) < 1e-12))
    checks.append(("a non-dissociating solute (i = 1) gives half the pressure",
                   abs(L.osmotic_pressure(35.0, 25.0, i=1) - p / 2) < 1e-9))
    checks.append(("seawater pi equals a water column of about 303 m", abs(L.column_height(p) - 302.7) < 0.5))
    checks.append(("boiling 1 m3 once needs 627 kWh, about 760 times the minimum",
                   abs(L.boiling_energy() - 626.9) < 0.1 and 740 < L.boiling_energy() / L.minimum_energy(35.0) < 780))
    checks.append(("lifting 1 m3 by 100 m needs 0.273 kWh", abs(L.lifting_energy(100.0) - 0.2725) < 1e-3))
    s = np.linspace(0, 70, 8)
    checks.append(("minimum energy never decreases with salinity",
                   bool(np.all(np.diff([L.minimum_energy(x) for x in s]) >= 0))))
    bad = 0
    for call in (lambda: L.molar_concentration(-1.0), lambda: L.osmotic_pressure(35.0, -300.0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 2))
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
