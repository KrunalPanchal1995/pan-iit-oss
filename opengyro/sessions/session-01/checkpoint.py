"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("I = m R^2 / 2 = 6.25e-4 kg m^2 for the 0.5 kg, 5 cm disc", abs(L.I3 - 6.25e-4) < 1e-9))
    checks.append(("L = I w: 0.0625 kg m^2/s at 100 rad/s", abs(L.angular_momentum(100) - 0.0625) < 1e-9))
    checks.append(("weight torque m g r = 0.1962 N m", abs(L.gravity_torque() - 0.5 * 9.81 * 0.04) < 1e-9))
    t, Ls = L.precess(100)
    rate = L.circling_rate(t, Ls)
    # worked example: spin 100 rad/s -> torque / L = 0.1962 / 0.0625 = 3.139 rad/s, one circle in 2.00 s
    checks.append((f"worked example: spin 100 rad/s circles at 3.139 rad/s, once per 2.00 s (got {rate:.3f})",
                   abs(rate - 3.139) < 0.01 and abs(2 * np.pi / rate - 2.0) < 0.01))
    checks.append(("simulated circling matches torque / L within 0.5 percent", abs(rate / L.predicted_rate(100) - 1) < 0.005))
    checks.append(("the size of L does not change (torque is sideways)", abs(np.linalg.norm(Ls[-1]) - np.linalg.norm(Ls[0])) < 1e-6))
    checks.append(("the axle stays horizontal", float(np.abs(Ls[:, 2]).max()) < 1e-9))
    t2, L2 = L.precess(200)
    checks.append(("double the spin: half the circling rate", abs(L.circling_rate(t2, L2) / rate - 0.5) < 0.005))
    checks.append(("faster spin circles slower (50 > 100 > 200 rad/s)", L.predicted_rate(50) > L.predicted_rate(100) > L.predicted_rate(200)))
    checks.append(("without spin the wheel falls within 0.5 s", L.fall_time_no_spin() < 0.5))
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
