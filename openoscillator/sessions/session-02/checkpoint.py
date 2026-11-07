"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def _residual(L, m, k, b, A=0.05):
    """Largest |m x'' + b x' + k x| / (k A) for the damped solution, by finite differences."""
    t = np.linspace(0.2, 4.0, 4001)
    h = 1e-4
    x0, xp, xm = L.damped_x(t, A, m, k, b), L.damped_x(t + h, A, m, k, b), L.damped_x(t - h, A, m, k, b)
    v = (xp - xm) / (2 * h)
    a = (xp - 2 * x0 + xm) / h ** 2
    return float(np.max(np.abs(m * a + b * v + k * x0)) / (k * A))


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    m, k, A = 0.5, 20.0, 0.05
    w = L.omega_spring(m, k)
    checks.append(("worked example: spring 0.5 kg, 20 N/m has w = 6.325 rad/s and T = 0.9935 s",
                   abs(w - 6.3246) < 1e-3 and abs(L.period_from_omega(w) - 0.9935) < 1e-3))
    checks.append(("worked example: a 1.0 s period with 0.5 kg needs k = 19.74 N/m", abs(L.stiffness_for_period(1.0, 0.5) - 19.739) < 1e-2))
    checks.append(("worked example: the seconds pendulum (T = 2 s) needs L = 0.994 m", abs(L.length_for_period(2.0) - 0.9940) < 5e-4))
    checks.append(("a 1 s full period needs L = 0.2485 m", abs(L.length_for_period(1.0) - 0.2485) < 5e-4))
    checks.append(("round trip: the period of that length is 2 s", abs(2 * np.pi / L.omega_pendulum(L.length_for_period(2.0)) - 2.0) < 1e-9))
    t = np.linspace(0, 6, 6001)
    ke, pe, tot = L.energies(t, L.x_shm(t, A, w), m, k)
    checks.append(("undamped energy stays at 1/2 k A^2 = 25 mJ (within 0.1 percent)", np.allclose(tot[2:-2], 0.5 * k * A ** 2, rtol=1e-3)))
    checks.append(("kinetic energy is zero at the ends and total at the middle", abs(ke[0]) < 1e-5 and abs(ke[np.argmin(np.abs(t - np.pi / (2 * w)))] - 0.5 * k * A ** 2) < 1e-4))
    bc = L.critical_damping(m, k)
    checks.append(("critical damping 2 sqrt(k m) = 6.325 kg/s, zeta = 1", abs(bc - 6.3246) < 1e-3 and abs(L.damping_ratio(m, k, bc) - 1.0) < 1e-12))
    for name, b in (("underdamped", 0.5), ("critical", bc), ("overdamped", 3 * bc)):
        checks.append((f"the {name} solution satisfies m x'' + b x' + k x = 0", _residual(L, m, k, b) < 1e-3))
    x = L.damped_x(t, A, m, k, 3 * bc)
    checks.append(("overdamped motion never crosses zero", bool(np.all(x > 0))))
    checks.append(("hand calculation: b = 0.5 gives damped T = 0.9966 s", abs(L.damped_period(m, k, 0.5) - 0.9966) < 1e-3))
    ratio = L.envelope(5.0, A, m, k, 0.5) / L.envelope(0.0, A, m, k, 0.5)
    checks.append(("hand calculation: the envelope falls to exp(-2.5) = 0.082 after 5 s", abs(ratio - np.exp(-2.5)) < 1e-9))
    checks.append(("time to fall to half: 2 m ln 2 / b = 1.386 s", abs(L.time_to_fraction(m, 0.5, 0.5) - 1.3863) < 1e-3))
    checks.append(("edge: b = 0 gives the undamped cosine", np.allclose(L.damped_x(t, A, m, k, 0.0), L.x_shm(t, A, w), atol=1e-12)))
    checks.append(("edge: critical damping has no nan", bool(np.all(np.isfinite(L.damped_x(t, A, m, k, bc))))))
    checks.append(("edge: a critical or overdamped system has no period", np.isnan(L.damped_period(m, k, bc))))
    k1 = L.stiffness_for_period(1.0, 0.5)
    checks.append(("worked example: with k = 19.74 and b = 0.5 the damped period is 1.0032 s and zeta = 0.0796",
                   abs(L.damped_period(0.5, k1, 0.5) - 1.0032) < 1e-3 and abs(L.damping_ratio(0.5, k1, 0.5) - 0.0796) < 1e-4))
    checks.append(("worked example: critical damping for that spring is 6.283 kg/s", abs(L.critical_damping(0.5, k1) - 6.2832) < 1e-3))
    checks.append(("worked example: after 5 s the envelope is 8.2 percent of its start",
                   abs(L.envelope(5.0, 1.0, 0.5, k1, 0.5) / L.envelope(0.0, 1.0, 0.5, k1, 0.5) - 0.0821) < 1e-3))
    checks.append(("question B: 0.20 kg at 2 Hz needs k = 31.58 N/m", abs(L.stiffness_for_period(0.5, 0.2) - 31.58) < 1e-2))
    checks.append(("question B2: a 1.5 s pendulum needs L = 0.559 m", abs(L.length_for_period(1.5) - 0.559) < 1e-3))
    checks.append(("question D: b = 1.0 kg/s leaves 4.98 percent after 3 s, critical damping leaves almost nothing",
                   abs(L.envelope(3.0, 1.0, 0.5, 20.0, 1.0) / L.envelope(0.0, 1.0, 0.5, 20.0, 1.0) - 0.0498) < 1e-3
                   and abs(L.damped_x(3.0, 1.0, 0.5, 20.0, L.critical_damping(0.5, 20.0))) < 1e-6))
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
