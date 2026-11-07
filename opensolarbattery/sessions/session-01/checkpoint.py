"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("no solar at night (3 h and 22 h)", float(L.solar_power(3.0, 4.0)) == 0.0 and float(L.solar_power(22.0, 4.0)) == 0.0))
    checks.append(("solar peaks at noon at the array rating", abs(float(L.solar_power(12.0, 4.0)) - 4.0) < 1e-9))
    per_kw = float(L.solar_power(L.T, 1.0).sum() * L.DT)
    checks.append((f"a clear day gives 24/pi = 7.639 kWh per kW (got {per_kw:.3f})", abs(per_kw - 24 / np.pi) < 0.01))
    load = float(L.demand_power(L.T, 10.0).sum() * L.DT)
    checks.append(("demand curve area equals the chosen daily energy", abs(load - 10.0) < 1e-9))
    b = L.day_balance(4.0, 10.0)
    checks.append((f"worked example: 4 kW array, 10 kWh/day: solar energy 4 x 7.639 = 30.56 kWh (got {b['pv_kwh']:.2f})", abs(b["pv_kwh"] - 4 * 24 / np.pi) < 0.1))
    checks.append(("energy balance: direct + surplus = solar and direct + deficit = demand",
                   abs(b["direct_kwh"] + b["surplus_kwh"] - b["pv_kwh"]) < 1e-9 and abs(b["direct_kwh"] + b["deficit_kwh"] - b["load_kwh"]) < 1e-9))
    z = L.day_balance(0.0, 10.0)
    checks.append(("edge case: no array means no direct use and deficit = demand", z["direct_kwh"] == 0 and abs(z["deficit_kwh"] - 10.0) < 1e-9))
    checks.append(("a cloudier day (sun 0.5) halves the solar energy",
                   abs(L.day_balance(4.0, 10.0, 0.5)["pv_kwh"] * 2 - b["pv_kwh"]) < 1e-9))
    big = L.day_balance(20.0, 10.0)
    checks.append(("a huge array cannot meet more than 100 percent of demand", big["solar_share"] <= 1.0 + 1e-12 and big["self_consumption"] < b["self_consumption"]))
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
