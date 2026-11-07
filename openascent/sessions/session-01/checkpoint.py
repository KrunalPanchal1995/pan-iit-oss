"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: Isp 300 s gives ve = 2942 m/s", abs(L.exhaust_velocity(300) - 2941.995) < 0.01))
    checks.append(("worked example: 100 t -> 25 t at Isp 300 s gives 4078 m/s",
                   abs(L.delta_v(300, 100e3, 25e3) - 4078.5) < 0.5))
    checks.append(("hand calculation: mass ratio 4 = 2 x 2, so delta-v is 2 ve ln 2",
                   abs(L.delta_v(300, 100e3, 25e3) - 2 * 300 * 9.80665 * np.log(2)) < 1e-6))
    checks.append(("no propellant burnt means no delta-v", L.delta_v(300, 5e3, 5e3) == 0.0))
    checks.append(("mass ratio needed inverts the rocket equation",
                   abs(L.mass_ratio_needed(L.delta_v(320, 80e3, 20e3), 320) - 4.0) < 1e-9))
    checks.append(("worked example: circular speed at 200 km is 7788 m/s", abs(L.circular_speed(200e3) - 7788.0) < 1.0))
    checks.append(("circular speed falls with altitude (v**2 r is constant)",
                   abs(L.circular_speed(1000e3) ** 2 * (L.R_EARTH + 1000e3) - L.circular_speed(0) ** 2 * L.R_EARTH) < 1e6))
    total, parts = L.stack_delta_v(L.LAUNCHER, L.PAYLOAD)
    checks.append(("worked example: stage 1 gives 4385 m/s and stage 2 6488 m/s",
                   abs(parts[0] - 4385) < 1 and abs(parts[1] - 6488) < 1))
    checks.append(("hand calculation: stage 2 = 340 g0 ln(17500 / 2500)",
                   abs(parts[1] - 340 * 9.80665 * np.log(17500 / 2500)) < 1e-6))
    single, _ = L.stack_delta_v(L.single_stage_equivalent(L.LAUNCHER), L.PAYLOAD)
    checks.append((f"staging wins: two stages {total:.0f} m/s against one stage {single:.0f} m/s", total > single + 3000))
    checks.append(("two stages exceed the 9.4 km/s budget, one stage does not", total > L.DV_TO_LEO > single))
    checks.append(("a stack of one stage equals the single-stage formula",
                   abs(L.stack_delta_v([dict(prop=75e3, dry=25e3, isp=300)], 0)[0] - L.delta_v(300, 100e3, 25e3)) < 1e-9))
    bad = 0
    for call in (lambda: L.exhaust_velocity(0), lambda: L.delta_v(300, 10, 20), lambda: L.circular_speed(-1)):
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
