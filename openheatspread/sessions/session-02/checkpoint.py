"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hand calculation: paste 0.2 mm, k = 3, 4 cm^2 has R = 0.1667 K/W",
                   abs(L.r_cond(0.2, 3.0, 4.0e-4) - 0.16667) < 1e-4))
    checks.append(("hand calculation: air film h = 50 on 100 cm^2 has R = 2 K/W",
                   abs(L.r_conv(50.0, 1.0e-2) - 2.0) < 1e-12))
    t = L.chip_temperature(20.0, 3.0, 200.0, 50.0)
    checks.append(("worked example: 20 W, 3 mm aluminium, h = 50 gives 69.08 C", abs(t - 69.08) < 0.01))
    temps = L.interface_temperatures(20.0, 3.0, 200.0, 50.0)
    checks.append(("interface temperatures fall step by step: 69.08, 65.75, 65.00, 25.00",
                   np.allclose(temps, [69.08, 65.75, 65.0, 25.0], atol=0.01)))
    checks.append(("the temperature drops add up to P * R_total",
                   abs((temps[0] - temps[-1]) - 20.0 * sum(L.stack(3.0, 200.0, 50.0))) < 1e-9))
    checks.append(("zero power leaves the chip at ambient", L.chip_temperature(0.0, 3.0, 200.0, 50.0) == L.T_AMBIENT))
    h = L.required_h(30.0, 85.0, 3.0, 200.0)
    checks.append(("design: a 30 W chip at 85 C needs h of about 55.7", abs(h - 55.68) < 0.05))
    checks.append(("with that h the chip sits exactly at the limit",
                   abs(L.chip_temperature(30.0, 3.0, 200.0, h) - 85.0) < 1e-9))
    checks.append(("an impossible limit returns None (200 W, 30 C)", L.required_h(200.0, 30.0, 3.0, 200.0) is None))
    checks.append(("max power of the example cooler at 85 C is 27.2 W", abs(L.max_power(85.0, 3.0, 200.0, 50.0) - 27.22) < 0.01))
    checks.append(("airflow matters more than metal: doubling h beats switching steel to copper",
                   L.chip_temperature(20.0, 3.0, 200.0, 25.0) - L.chip_temperature(20.0, 3.0, 200.0, 50.0)
                   > L.chip_temperature(20.0, 3.0, 50.0, 50.0) - L.chip_temperature(20.0, 3.0, 400.0, 50.0)))
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
