"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    m = 1.4
    checks.append(("worked example: Kp = 4 N/m, m = 1.4 kg gives wn = 1.690 rad/s", abs(L.natural_frequency(4.0, m) - 1.6903) < 1e-3))
    z = L.damping_ratio(4.0, 3.0, m)
    checks.append(("worked example: Kd = 3 N s/m gives zeta = 0.634", abs(z - 0.6339) < 1e-3))
    checks.append(("worked example: overshoot formula exp(-zeta pi / sqrt(1 - zeta^2)) = 7.6 percent",
                   abs(L.overshoot_formula(z) - 0.0760) < 1e-3))
    checks.append(("worked example: steady-state error (1.4 - 1.2) 9.81 / 4 = 0.4905 m", abs(L.steady_state_error(4.0, m) - 0.4905) < 1e-9))
    checks.append(("known limits: zeta = 1 gives no overshoot, zeta -> 0 gives 100 percent",
                   L.overshoot_formula(1.0) == 0.0 and L.overshoot_formula(1e-9) > 0.999))

    pd = L.simulate_altitude(4.0, 0.0, 3.0, mass=m, t_end=20.0)
    met = L.step_metrics(pd["t"], pd["z"], 0.0)
    checks.append((f"PD simulation settles at {met['final']:.3f} m = 2 - 0.4905 (the predicted steady-state error)",
                   abs(met["final"] - (2.0 - 0.4905)) < 5e-3))
    checks.append((f"PD simulation overshoot {met['overshoot']:.3f} matches the formula 0.076 within 0.01",
                   abs(met["overshoot"] - 0.0760) < 0.01))
    exact = L.simulate_altitude(4.0, 0.0, 3.0, mass=1.2, t_end=20.0)
    checks.append(("with the true mass known, PD reaches 2 m exactly", abs(exact["z"][-1] - 2.0) < 2e-3))
    pid = L.simulate_altitude(4.0, 1.5, 3.0, mass=m, t_end=25.0)
    checks.append(("integral action removes the steady-state error (within 1 cm)", abs(pid["z"][-1] - 2.0) < 0.01))
    checks.append(("at rest the PID thrust equals the true weight 1.4 x 9.81 = 13.73 N",
                   abs(pid["thrust"][-1] - 1.4 * 9.81) < 0.05))
    p_only = L.simulate_altitude(4.0, 0.0, 0.0, mass=1.2, t_end=20.0)
    checks.append(("P only (no damping) keeps oscillating: still swinging more than 1 m after 15 s",
                   np.ptp(p_only["z"][p_only["t"] > 15.0]) > 1.0))
    a = L.simulate_altitude(4.0, 0.0, 3.0, mass=m, t_end=20.0, dt=0.01)["z"][-1]
    b = L.simulate_altitude(4.0, 0.0, 3.0, mass=m, t_end=20.0, dt=0.002)["z"][-1]
    checks.append(("a smaller time step gives the same answer (convergence)", abs(a - b) < 2e-3))
    checks.append(("Routh test: Kp = 4, Ki = 1.5, Kd = 3 is stable; Ki = 10 (> Kd Kp / m = 8.6) is not",
                   L.pid_is_stable(4.0, 1.5, 3.0, m) and not L.pid_is_stable(4.0, 10.0, 3.0, m)))
    bad_run = L.simulate_altitude(4.0, 10.0, 3.0, mass=m, t_end=40.0, t_max=1e9)
    checks.append(("the unstable gains really grow in the simulation", np.max(np.abs(bad_run["z"][-500:] - 2.0)) > 2.0))
    thr = L.simulate_altitude(50.0, 0.0, 10.0, mass=m, t_end=3.0)["thrust"]
    checks.append(("thrust is limited to 0..40 N even with large gains", thr.min() >= 0.0 and thr.max() <= 40.0))
    bad = 0
    for call in (lambda: L.PID(-1.0), lambda: L.steady_state_error(0.0, 1.4), lambda: L.simulate_altitude(1, 0, 1, dt=0.0)):
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
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
