"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: q at 50 m/s at sea level is 1531.25 Pa", abs(L.dynamic_pressure(50.0) - 1531.25) < 1e-9))
    checks.append(("worked example: 1000 kg, 16 m2, 50 m/s needs CL = 0.4004",
                   abs(L.cl_needed(1000.0, 50.0, 16.0) - 9810.0 / (1531.25 * 16.0)) < 1e-12 and abs(L.cl_needed(1000, 50, 16) - 0.4004) < 1e-4))
    checks.append(("lift at the needed CL equals the weight m g",
                   abs(L.lift(L.cl_needed(1000, 50, 16), 50, 16) - 1000 * 9.81) < 1e-9))
    checks.append(("worked example: stall speed with CL_max 1.4 is 26.74 m/s", abs(L.stall_speed(1000, 16, 1.4) - 26.74) < 0.01))
    checks.append(("at the stall speed the needed CL is exactly CL_max",
                   abs(L.cl_needed(1000, L.stall_speed(1000, 16, 1.4), 16) - 1.4) < 1e-12))
    checks.append(("doubling the speed gives four times the lift", abs(L.lift(0.5, 60, 16) / L.lift(0.5, 30, 16) - 4.0) < 1e-12))
    checks.append(("worked example: drag with CD 0.03 is 735 N", abs(L.drag(0.03, 50, 16) - 735.0) < 1e-9))
    checks.append(("worked example: fuel energy 2.94 MJ per km at engine efficiency 0.25",
                   abs(L.fuel_energy_per_km(735.0) - 2.94e6) < 1e-3))
    checks.append(("drag = weight / (L/D): L/D 12 gives 817.5 N", abs(L.cruise_drag(1000, 12) - 817.5) < 1e-9))
    checks.append(("Bernoulli: Cp = 1 at a stagnation point, 0 at free-stream speed",
                   L.pressure_coefficient(0.0, 30.0) == 1.0 and abs(L.pressure_coefficient(30.0, 30.0)) < 1e-15))
    checks.append(("worked example: toy wing 1.2 and 0.95 V_inf gives CL = 0.5375", abs(L.toy_wing_cl(1.2, 0.95) - 0.5375) < 1e-12))
    checks.append(("equal speeds on both sides give no lift", abs(L.toy_wing_cl(1.1, 1.1)) < 1e-15))
    bad = 0
    for call in (lambda: L.dynamic_pressure(10, rho=0), lambda: L.stall_speed(1000, 16, 0),
                 lambda: L.cruise_drag(1000, 0), lambda: L.fuel_energy_per_km(500, 1.5)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 4))
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
