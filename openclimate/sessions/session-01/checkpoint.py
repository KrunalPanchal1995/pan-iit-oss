"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: Earth absorbs 1361 x (1 - 0.30) / 4 = 238.2 W/m2",
                   abs(L.absorbed_solar(1361.0, 0.30) - 238.175) < 1e-9))
    te = L.equilibrium_temperature(1361.0, 0.30)
    checks.append((f"worked example: bare Earth temperature {te:.1f} K (hand value 254.6 K)", abs(te - 254.58) < 0.05))
    checks.append(("worked example: a surface at 288 K radiates 390.1 W/m2", abs(float(L.emitted(288.0)) - 390.1) < 0.1))
    checks.append(("worked example: greenhouse warming 288 - 254.6 = 33.4 K", abs(L.greenhouse_warming(288.0) - 33.4) < 0.05))
    checks.append(("balance: at T_e the planet radiates exactly what it absorbs",
                   abs(float(L.emitted(te)) - L.absorbed_solar()) < 1e-9 and abs(float(L.net_flux(te))) < 1e-9))
    checks.append(("below T_e the planet warms (net > 0), above it it cools (net < 0)",
                   float(L.net_flux(te - 10)) > 0 and float(L.net_flux(te + 10)) < 0))
    checks.append(("doubling T multiplies the radiation by 16 (T^4 law)",
                   abs(float(L.emitted(400.0)) / float(L.emitted(200.0)) - 16.0) < 1e-12))
    checks.append(("a perfect radiator at 0 K emits nothing", float(L.emitted(0.0)) == 0.0))
    checks.append(("limit: albedo 1 (perfect mirror) gives 0 K", L.equilibrium_temperature(1361.0, 1.0) == 0.0))
    checks.append(("more reflection gives a colder planet",
                   L.equilibrium_temperature(1361.0, 0.5) < L.equilibrium_temperature(1361.0, 0.3)))
    checks.append(("T_e scales as S^(1/4): 16 times the sunlight doubles T_e",
                   abs(L.equilibrium_temperature(16 * 1361.0, 0.3) / te - 2.0) < 1e-12))
    checks.append(("Mars: bare model is close to the measured 210 K (thin atmosphere, within 5 K)",
                   abs(L.equilibrium_temperature(586.0, 0.25) - 210.0) < 5.0))
    checks.append(("Venus: measured surface is over 400 K above the bare model",
                   737.0 - L.equilibrium_temperature(2601.0, 0.77) > 400.0))
    checks.append(("kelvin to Celsius: 288 K = 14.85 C", abs(L.to_celsius(288.0) - 14.85) < 1e-12))
    bad = 0
    for call in (lambda: L.absorbed_solar(1361.0, 1.2), lambda: L.absorbed_solar(-5.0, 0.3), lambda: L.emitted(-1.0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
