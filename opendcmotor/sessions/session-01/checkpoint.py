"""Checkpoint for Session 1. Prints PASS or FAIL."""
import math


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    w = L.speed_at_load(0.12)
    checks.append(("worked example: load 0.12 N m gives 144 rad/s = 1375 rpm",
                   abs(w - 144.0) < 1e-9 and abs(L.rpm(w) - 1375.1) < 0.1))
    checks.append(("no load gives the no-load speed 240 rad/s", abs(L.speed_at_load(0.0) - 240.0) < 1e-9))
    checks.append(("a load equal to the stall torque stops the motor", L.speed_at_load(0.30) == 0.0))
    checks.append(("a load above the stall torque still gives 0 (not negative)", L.speed_at_load(0.5) == 0.0))
    checks.append(("hand calculation: 1000 rpm is 104.72 rad/s", abs(L.rad_per_s(1000) - 104.72) < 0.01))
    checks.append(("rpm and rad/s convert back and forth", abs(L.rpm(L.rad_per_s(733.0)) - 733.0) < 1e-9))
    checks.append(("half the stall load gives half the no-load speed", abs(L.speed_at_load(0.15) - 120.0) < 1e-9))
    ts, wn = L.motor_at_voltage(6.0)
    checks.append(("6 V halves both stall torque and no-load speed", abs(ts - 0.15) < 1e-9 and abs(wn - 120.0) < 1e-9))
    checks.append(("power is zero at no load and at stall", L.mech_power(0.0) == 0.0 and L.mech_power(0.30) == 0.0))
    checks.append(("mechanical power at 0.12 N m is 17.28 W", abs(L.mech_power(0.12) - 17.28) < 1e-9))
    try:
        L.speed_at_load(-0.1)
        ok = False
    except ValueError:
        ok = True
    checks.append(("a negative load torque is rejected", ok))
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
