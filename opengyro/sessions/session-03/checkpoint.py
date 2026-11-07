"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("I3 = 6.25e-4 and I1 = 1.1125e-3 kg m^2", abs(L.I3 - 6.25e-4) < 1e-9 and abs(L.I1 - 1.1125e-3) < 1e-9))
    th0, w3 = np.radians(60), 300.0
    t, y = L.simulate(w3, th0, 3.0)
    p_psi, p_phi, en = L.invariants(y)
    checks.append(("p_psi constant to 1e-9", L.relative_drift(p_psi) < 1e-9))
    checks.append(("p_phi constant to 1e-9", L.relative_drift(p_phi) < 1e-9))
    checks.append(("energy constant to 1e-9", L.relative_drift(en) < 1e-9))
    rate, nut = L.measured_rates(t, y)
    # worked example: w3 = 300 rad/s -> formula 1.046 rad/s, simulation 1.050 rad/s
    checks.append((f"worked example: spin 300 rad/s, formula 1.046 rad/s, simulation within 1 percent (got {rate:.4f})",
                   abs(L.omega_p(300.0) - 1.0464) < 1e-3 and abs(rate / L.omega_p(300.0) - 1) < 0.01))
    checks.append((f"nutation frequency near I3 w3 / I1 = 168.5 rad/s (got {nut:.1f})", abs(nut / (L.I3 * w3 / L.I1) - 1) < 0.02))
    r_fast = L.measured_rates(*L.simulate(600.0, th0, 3.0))[0]
    r_slow = L.measured_rates(*L.simulate(200.0, th0, 3.0))[0]
    checks.append(("faster spin gives slower precession", r_fast < r_slow))
    checks.append(("formula error shrinks with spin (200 rad/s worse than 600)", abs(r_slow / L.omega_p(200.0) - 1) > abs(r_fast / L.omega_p(600.0) - 1)))
    wc = L.sleeping_limit()
    checks.append((f"classical sleeping limit sqrt(4 m g r I1) / I3 = 47.3 rad/s (got {wc:.1f})", abs(wc - 47.3) < 0.1))
    checks.append(("sleeping: 1.3 x limit stays below 8 degrees", np.degrees(L.sleeping_run(1.3 * wc, t_end=2.0)) < 8))
    checks.append(("below the limit: 0.8 x limit tips over beyond 45 degrees", np.degrees(L.sleeping_run(0.8 * wc, t_end=2.0)) > 45))
    checks.append(("failure case: spin 10 rad/s from 45 degrees falls over", L.falls(10.0)))
    checks.append(("spin 300 rad/s from 45 degrees does not fall over", not L.falls(300.0)))
    return checks

# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
