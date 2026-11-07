"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: a 1.2 kg drone weighs 11.77 N, 2.943 N per rotor",
                   abs(L.weight(1.2) - 11.772) < 1e-9 and abs(L.weight(1.2) / 4 - 2.943) < 1e-9))
    w_h = L.hover_omega(1.2)
    checks.append(("worked example: hover speed 542.5 rad/s (about 5180 rpm)",
                   abs(w_h - 542.49) < 0.05 and abs(float(L.rpm_from_omega(w_h)) - 5180) < 1.0))
    checks.append(("at the hover speed the four rotors carry exactly the weight",
                   abs(4 * float(L.rotor_thrust(w_h)) - L.weight(1.2)) < 1e-9))
    checks.append(("thrust grows with the square of speed: doubling omega gives 4 times the thrust",
                   abs(float(L.rotor_thrust(800.0)) / float(L.rotor_thrust(400.0)) - 4.0) < 1e-12))
    checks.append(("hover speed scales with the square root of mass: 4x the mass needs 2x the speed",
                   abs(L.hover_omega(4.8) / L.hover_omega(1.2) - 2.0) < 1e-12))
    checks.append(("hand calculation: thrust-to-weight at 1000 rad/s is 40 / 11.772 = 3.40",
                   abs(L.thrust_to_weight(1.2, 1000.0) - 40.0 / 11.772) < 1e-9))
    checks.append(("exact hover thrust gives zero acceleration", abs(L.vertical_acceleration(L.weight(1.2), 1.2)) < 1e-12))
    checks.append(("zero thrust gives free fall, a = -g", abs(L.vertical_acceleration(0.0, 1.4) + 9.81) < 1e-12))
    a = L.vertical_acceleration(L.weight(1.2), 1.4)
    checks.append(("worked example: with a 0.2 kg parcel a = -1.40 m/s^2", abs(a + 1.4014) < 1e-3))
    checks.append(("worked example: it sinks 1 m in 1.19 s", abs(L.time_to_drop(1.0, L.weight(1.2), 1.4) - 1.195) < 2e-3))
    checks.append(("height from z = a t^2 / 2 agrees with time_to_drop",
                   abs(L.open_loop_height(L.time_to_drop(1.0, L.weight(1.2), 1.4), L.weight(1.2), 1.4) + 1.0) < 1e-9))
    checks.append(("a drone that does not sink never drops", L.time_to_drop(1.0, L.weight(1.2), 1.0) == float("inf")))
    p12 = L.ideal_hover_power(L.weight(1.2) / 4, 0.127)
    p14 = L.ideal_hover_power(L.weight(1.4) / 4, 0.127)
    checks.append(("hover power grows as mass^1.5: the parcel costs 26 percent more", abs(p14 / p12 - (1.4 / 1.2) ** 1.5) < 1e-12
                   and 1.25 < p14 / p12 < 1.27))
    checks.append(("hand calculation: ideal hover power of the 1.2 kg drone is about 57 W",
                   abs(4 * p12 - 57.3) < 0.2))
    bad = 0
    for call in (lambda: L.weight(0.0), lambda: L.hover_omega(1.2, n_rotors=0), lambda: L.weight(-1.0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
    _ = np  # numpy is available for your own extra checks
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
