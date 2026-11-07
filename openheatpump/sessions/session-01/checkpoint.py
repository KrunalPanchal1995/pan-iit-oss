"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("a resistance heater needs 1 kWh of electricity per kWh of heat", L.heater_electricity(10.0) == 10.0))
    # hand calculation: 0.45 * 308.15 / 35 = 3.962
    cop = L.heat_pump_cop(0.0, 35.0)
    checks.append((f"worked example: COP at 0 C outdoors, 35 C supply is 0.45 x 308.15 / 35 = 3.96 (got {cop:.3f})",
                   abs(cop - 0.45 * 308.15 / 35.0) < 1e-9 and abs(cop - 3.962) < 1e-3))
    work, outdoor = L.heat_pump_flows(10.0, cop)
    checks.append((f"worked example: 10 kWh of heat needs {work:.2f} kWh of electricity (2.52) and {outdoor:.2f} kWh from outdoors (7.48)",
                   abs(work - 2.524) < 1e-3 and abs(outdoor - 7.476) < 1e-3))
    checks.append(("energy balance: electricity + outdoor heat = heat delivered", abs(work + outdoor - 10.0) < 1e-12))
    checks.append(("the colder it is outside, the lower the COP", L.heat_pump_cop(-10, 35) < L.heat_pump_cop(0, 35) < L.heat_pump_cop(10, 35)))
    checks.append(("a higher supply temperature lowers the COP", L.heat_pump_cop(0, 55) < L.heat_pump_cop(0, 35)))
    checks.append(("the heat pump still beats the heater (COP above 1) at -15 C with 55 C supply", L.heat_pump_cop(-15, 55) > 1.0))
    # edge: supply not above outdoor is rejected
    try:
        L.heat_pump_cop(20.0, 20.0)
        rejected = False
    except ValueError:
        rejected = True
    checks.append(("supply at or below the outdoor temperature is rejected", rejected))
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
