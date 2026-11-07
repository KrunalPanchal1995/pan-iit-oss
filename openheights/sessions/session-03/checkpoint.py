"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    H = 28.4
    checks.append(("true_angle(28.4, 28.4) is 45 degrees", abs(L.true_angle(28.4, 28.4) - 45.0) < 1e-9))
    checks.append(("noise-free readings recover the height exactly",
                   abs(float(L.h_one(40, L.true_angle(40, H))) - 30.0) < 1e-9))
    a1, a2 = L.true_angle(40, H), L.true_angle(30, H)
    checks.append(("noise-free two-angle estimate recovers 30 m", abs(float(L.h_two(10, a1, a2)) - 30.0) < 1e-9))

    rng = np.random.default_rng(0)
    r = L.noisy_readings(45.0, 0.5, 20000, rng)
    checks.append(("simulated readings have mean 45 and std 0.5 degrees", abs(r.mean() - 45) < 0.02 and abs(r.std() - 0.5) < 0.02))

    one, two = L.monte_carlo(40.0, H, 0.5, b=10.0)
    f1 = L.sigma_one(40.0, L.true_angle(40.0, H), 0.5)
    checks.append((f"Monte Carlo std of the one-angle method matches d sec^2 sigma (MC {one.std():.3f}, formula {f1:.3f})",
                   abs(one.std() - f1) / f1 < 0.05))
    f2 = L.sigma_two(10.0, a1, a2, 0.5)
    checks.append((f"Monte Carlo std of the two-angle method matches the propagated formula (MC {two.std():.2f}, formula {f2:.2f})",
                   abs(two.std() - f2) / f2 < 0.08))
    checks.append(("with a short 10 m walk the two-angle method is much noisier than one angle", two.std() > 3 * one.std()))
    two30 = L.monte_carlo(40.0, H, 0.5, b=30.0)[1]
    checks.append(("a longer walk (30 m) makes the two-angle method much better than 10 m", two30.std() < 0.4 * two.std()))

    # averaging: standard error of the mean falls as 1/sqrt(n)
    rng = np.random.default_rng(1)
    sem1 = np.std([L.h_one(28.4, L.noisy_readings(45.0, 0.5, 1, rng)).mean() for _ in range(4000)])
    sem25 = np.std([L.h_one(28.4, L.noisy_readings(45.0, 0.5, 25, rng)).mean() for _ in range(4000)])
    checks.append((f"25 readings cut the uncertainty by about 5 (ratio {sem1 / sem25:.2f})", 4.5 < sem1 / sem25 < 5.5))
    m, s = L.mean_and_sem([1.0, 2.0, 3.0, 4.0])
    checks.append(("hand calculation: mean 2.5, sample std 1.291, SEM 0.645",
                   abs(m - 2.5) < 1e-12 and abs(s - 1.2909944 / 2) < 1e-6))

    # slope: worked example
    phi = 10.0
    top = math.degrees(math.atan((30 + 30 * math.tan(math.radians(phi)) - 1.6) / 30))
    sd = 30 / math.cos(math.radians(phi))
    corrected = L.h_on_slope(sd, phi, top)
    naive = L.h_ignoring_slope(sd, top)
    checks.append((f"worked example: on a 10 degree slope the corrected height is 30.0 m (got {corrected:.2f}), the naive one is 35.81 m (got {naive:.2f})",
                   abs(corrected - 30.0) < 1e-9 and abs(naive - 35.81) < 0.01))
    checks.append(("edge: zero slope gives the flat-ground formula", abs(L.h_on_slope(40, 0.0, 35.0) - L.h_ignoring_slope(40, 35.0)) < 1e-9))

    # failure case near 90 degrees
    far = L.sigma_one(28.4, 45.0, 0.5)
    near = L.sigma_one(2.0, L.true_angle(2.0, H), 0.5)
    checks.append((f"failure case: 2 m from the tower the error is about {near:.1f} m, over 7 times the 45 degree value", near > 7 * far))
    for bad in ([90.0], [95.0], [0.0]):
        try:
            L.h_one(10, bad)
            ok = False
        except ValueError:
            ok = True
        checks.append((f"edge: reading {bad[0]} degrees is rejected", ok))
    try:
        L.mean_and_sem([3.0])
        ok = False
    except ValueError:
        ok = True
    checks.append(("edge: a standard error needs at least two values", ok))

    mean, sem, comb = L.flagpole_report()
    checks.append((f"worked example: flagpole mean 9.38 m, SEM 0.035 m, combined 0.056 m (got {mean:.2f}, {sem:.3f}, {comb:.3f})",
                   abs(mean - 9.38) < 0.005 and abs(sem - 0.035) < 0.002 and abs(comb - 0.056) < 0.002))
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
