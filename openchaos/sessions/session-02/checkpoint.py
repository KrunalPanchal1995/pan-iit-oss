"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    w, vecs = L.normal_modes()
    hand = np.array([np.sqrt(L.G * (2 - np.sqrt(2))), np.sqrt(L.G * (2 + np.sqrt(2)))])
    checks.append((f"worked example: equal masses and rods give w = sqrt(g(2 -/+ sqrt 2)) = 2.397 and 5.787 rad/s (got {w[0]:.3f}, {w[1]:.3f})",
                   bool(np.allclose(w, hand, atol=1e-9)) and abs(hand[0] - 2.397) < 1e-3 and abs(hand[1] - 5.787) < 1e-3))
    checks.append(("mode shapes: th2 / th1 = +sqrt 2 for the slow mode and -sqrt 2 for the fast mode",
                   bool(np.allclose(vecs[1], [np.sqrt(2), -np.sqrt(2)]))))

    # the closed-form equations agree with the mass-matrix form for unequal masses and rods
    rng = np.random.default_rng(3)
    p = dict(m1=2.0, m2=0.5, l1=0.8, l2=1.3)
    worst = 0.0
    for _ in range(40):
        st = rng.uniform(-3, 3, size=4)
        worst = max(worst, float(np.max(np.abs(np.array(L.accel(st, **p)) - np.array(L.accel_matrix(st, **p))))))
    checks.append((f"closed form equals mass-matrix form for m1=2, m2=0.5, l1=0.8, l2=1.3 (worst difference {worst:.1e})", worst < 1e-9))

    # frequencies satisfy det(K - w^2 M) = 0 for unequal masses
    wq, _ = L.normal_modes(**p)
    m1, m2, l1, l2 = p["m1"], p["m2"], p["l1"], p["l2"]
    M = np.array([[(m1 + m2) * l1 ** 2, m2 * l1 * l2], [m2 * l1 * l2, m2 * l2 ** 2]])
    K = np.diag([(m1 + m2) * L.G * l1, m2 * L.G * l2])
    checks.append(("unequal masses: det(K - w^2 M) = 0 for both frequencies",
                   all(abs(np.linalg.det(K - x ** 2 * M)) < 1e-8 for x in wq)))

    checks.append(("small-angle limit: full simulation matches the linear normal modes to 1e-6 rad (amplitude 1e-3 rad)",
                   L.small_angle_error(0) < 1e-6 and L.small_angle_error(1) < 1e-6))

    # energy
    e_hand = -(2 * 1.0) * L.G * np.cos(np.radians(120)) - L.G * np.cos(np.radians(120))
    checks.append(("hand calculation: rest at 120 degrees has E = 3 g / 2 = 14.715 J",
                   abs(float(L.energy(L.release(120.0))) - e_hand) < 1e-9 and abs(e_hand - 14.715) < 1e-3))
    checks.append(("energy scale for equal masses and rods is 3 g = 29.43 J", abs(L.energy_scale() - 3 * L.G) < 1e-12))
    s0 = L.release(120.0)
    d1 = L.energy_drift(s0, 20.0, 0.01)
    d2 = L.energy_drift(s0, 20.0, 0.005)
    checks.append((f"RK4 is fourth order: halving the step cuts the drift by 10 to 40 times (ratio {d1 / d2:.1f})", 10 < d1 / d2 < 40))
    best, table = L.largest_step(1e-5, s0, 20.0, [0.04, 0.02, 0.01, 0.005, 0.0025])
    best6, _ = L.largest_step(1e-6, s0, 20.0, [0.04, 0.02, 0.01, 0.005, 0.0025])
    checks.append((f"design: largest step with energy drift below 1e-5 over 20 s is 0.005 s; below 1e-6 it is 0.0025 s (got {best}, {best6})",
                   best == 0.005 and best6 == 0.0025))

    # edge cases
    checks.append(("edge: hanging at rest has zero acceleration and zero energy drift",
                   bool(np.allclose(L.accel(np.zeros(4)), 0.0)) and L.energy_drift(np.zeros(4), 5.0, 0.01) == 0.0))
    checks.append(("edge: no step small enough in the list gives None", L.largest_step(1e-30, s0, 2.0, [0.02, 0.01])[0] is None))
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
