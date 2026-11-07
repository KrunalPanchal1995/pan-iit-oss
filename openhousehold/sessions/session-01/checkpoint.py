"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    e = L.energy_kwh(1500, 2)
    checks.append((f"worked example: 1500 W for 2 h is 3 kWh (got {e:.3f})", abs(e - 3.0) < 1e-9))
    checks.append(("half the time gives half the energy (1.5 kWh)", abs(L.energy_kwh(1500, 1) - 1.5) < 1e-9))
    checks.append(("double the power doubles the energy", abs(L.energy_kwh(3000, 2) - 2 * e) < 1e-9))
    checks.append(("zero hours gives zero energy", L.energy_kwh(1500, 0) == 0))
    try:
        L.energy_kwh(-5, 1)
        bad = False
    except ValueError:
        bad = True
    checks.append(("negative power is rejected", bad))
    d = L.daily_energies()
    checks.append(("fridge: 0.12 kW x 24 h = 2.88 kWh", abs(d["Fridge (average)"] - 2.88) < 1e-9))
    tot = L.total_energy()
    # hand calculation: 1.68 + 0.30 + 2.88 + 0.40 + 3.00
    checks.append((f"total by hand 1.68+0.30+2.88+0.40+3.00 = 8.26 kWh (got {tot:.2f})", abs(tot - 8.26) < 1e-9))
    checks.append(("cost = 8.26 kWh x Rs 6 = Rs 49.56", abs(L.cost(tot) - 49.56) < 1e-9))
    checks.append(("a zero rate costs nothing", L.cost(tot, 0.0) == 0))
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
