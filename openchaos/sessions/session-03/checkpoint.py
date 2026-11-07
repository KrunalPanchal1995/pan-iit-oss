"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    s0 = L.release(120.0)

    # worked example: horizon formula, hand calculation
    h1 = L.predicted_horizon(1e-6, 0.1, 1.0)
    h2 = L.predicted_horizon(1e-6, 0.1, 1.4)
    gain = L.predicted_horizon(1e-9, 0.1, 1.4) - h2
    checks.append((f"worked example: ln(0.1 / 1e-6) / 1.4 = 8.2 s, and a 1000 times better measurement adds only ln(1000) / 1.4 = 4.9 s (got {h2:.2f}, {gain:.2f})",
                   abs(h1 - math.log(1e5)) < 1e-12 and abs(h2 - 8.22) < 0.01 and abs(gain - 4.93) < 0.01))

    # equations: scalar and array versions agree; rest at the bottom stays at rest
    st = (0.7, -1.1, 0.4, 2.0)
    r_scalar = np.array(L.rate(st))
    r_array = np.array([float(x[0]) for x in L.rate(tuple(np.array([v]) for v in st))])
    checks.append(("the rate function gives the same numbers for single values and for arrays", bool(np.allclose(r_scalar, r_array))))
    checks.append(("hanging at rest: zero rates and energy -3 g", bool(np.allclose(L.rate((0.0, 0.0, 0.0, 0.0)), 0.0)) and abs(L.energy((0.0, 0.0, 0.0, 0.0)) + 3 * L.G) < 1e-12))

    # solvers
    t_r, d_r = L.drift_curve(L.rk4_step, s0, 200.0, 0.01)
    t_m, d_m = L.drift_curve(L.midpoint_step, s0, 200.0, 0.01)
    rk_growth = np.abs(d_r).max() / np.abs(d_r[t_r <= 20]).max()
    mid_ratio = np.abs(d_m[t_m > 100]).max() / np.abs(d_m[t_m <= 100]).max()
    checks.append((f"RK4 energy error keeps growing (x{rk_growth:.0f} from 20 s to 200 s); midpoint stays bounded (second half / first half = {mid_ratio:.2f})",
                   rk_growth > 3 and mid_ratio < 1.3))
    x0 = (0.5, -0.3, 0.2, 0.1)
    err = []
    for h in (0.02, 0.01):
        ref = x0
        for _ in range(int(round(0.2 / 0.0005))):
            ref = L.rk4_step(ref, 0.0005)
        s_m = x0
        for _ in range(int(round(0.2 / h))):
            s_m = L.midpoint_step(s_m, h)
        err.append(float(np.max(np.abs(np.array(s_m) - np.array(ref)))))
    checks.append((f"midpoint is second order: halving the step cuts its error over 0.2 s by about 4 (ratio {err[0] / err[1]:.1f})", 3.0 < err[0] / err[1] < 5.0))

    # Lyapunov: hand check on a synthetic exponential, then the real thing
    tt = np.arange(0.0, 30.0, 0.1)
    lam_syn, _, _, _ = L.fit_exponent(tt, 1e-8 * np.exp(0.9 * tt))
    checks.append(("hand calculation: the fit recovers lambda = 0.9 /s from d = 1e-8 exp(0.9 t)", abs(lam_syn - 0.9) < 1e-6))
    t, d = L.separation_curve(s0)
    lam_fit = L.fit_exponent(t, d)[0]
    lam_ben = float(L.benettin(np.array([s0]))[0])
    checks.append((f"chaotic start (120 degrees): fitted lambda {lam_fit:.2f} /s and Benettin lambda {lam_ben:.2f} /s agree within 30 percent, both above 1 /s",
                   lam_fit > 1.0 and lam_ben > 1.0 and abs(lam_fit - lam_ben) / lam_ben < 0.3))
    checks.append(("Section F hand calculations: horizon 14.8 s (lambda 1.2, 1e-8 to 0.5 rad) and start precision 4.8e-11 rad for a 15 s forecast at lambda 1.43",
                   abs(L.predicted_horizon(1e-8, 0.5, 1.2) - 14.8) < 0.05 and abs(0.1 * math.exp(-1.43 * 15) / 4.8e-11 - 1) < 0.02))
    i0, i1 = int(np.argmax(d > 1e-6)), int(np.argmax(d > 1e-2))
    two_point = float(np.log(d[i1] / d[i0]) / (t[i1] - t[i0]))
    checks.append((f"Section F: two-point slope of ln d across the fit window is 1.40 /s (got {two_point:.2f})", abs(two_point - 1.40) < 0.1))
    lam_reg = float(L.benettin(np.array([L.release(20.0)]), duration=30.0)[0])
    checks.append((f"regular start (20 degrees): lambda is about zero (got {lam_reg:.2f} /s, below 0.15)", lam_reg < 0.15))
    e145 = L.energy(L.release(145.0))
    starts = [L.rest_start_with_energy(a_, e145) for a_ in (140, 150, 160, 170)]
    lams = L.benettin(np.array(starts), duration=60.0)
    checks.append((f"at one energy, different starts give different lambda (spread {lams.max() - lams.min():.2f} /s over 60 s, above 0.1 /s; it grows to about 0.4 /s over 120 s)", float(lams.max() - lams.min()) > 0.1))
    checks.append(("edge: no rest start exists with impossible energy", L.rest_start_with_energy(10.0, 0.0) is None))

    # flip-time map validated against energy
    ang, ft = L.flip_time_map(n=40)
    g1, g2 = np.meshgrid(ang, ang)
    inside = L.cannot_flip(g1, g2)
    checks.append((f"flip-time map: no flips anywhere in the energy-forbidden region ({int(inside.sum())} starts checked)",
                   int(inside.sum()) > 100 and bool(np.all(ft[inside] >= 10.0))))
    frac = float(np.mean(ft >= 10.0))
    checks.append((f"flip-time map: between 25 and 65 percent of starts never flip, and the rest do (got {frac:.0%})", 0.25 < frac < 0.65))
    checks.append(("energy test: cannot_flip is true at (0, 0) and false at (pi, pi)",
                   bool(L.cannot_flip(0.0, 0.0)) and not bool(L.cannot_flip(math.pi, math.pi))))

    # linear small-angle limit
    checks.append(("small-angle limit: nonlinear run matches both normal modes to 1e-6 rad", L.small_angle_error(0) < 1e-6 and L.small_angle_error(1) < 1e-6))

    # failure case: big step
    t_big = L.departure_time(s0, 0.1, duration=20.0)
    t_small = L.departure_time(s0, 0.01, duration=20.0)
    _, dbig = L.drift_curve(L.rk4_step, s0, 20.0, 0.1, stride=1)
    checks.append((f"failure case: step 0.1 s departs from the reference at {t_big} s, step 0.01 s at {t_small} s; step 0.1 s loses over 10 percent of the energy scale",
                   t_big is not None and t_small is not None and t_big < 5.0 and t_small > 8.0 and np.abs(dbig).max() > 0.1))

    # predictability horizon
    measured = L.forecast_horizon(s0, (1e-6, 0.0, 0.0, 0.0))
    predicted = L.predicted_horizon(1e-6, 0.1, lam_ben)
    checks.append((f"horizon: measured {measured} s is within 40 percent of predicted {predicted:.1f} s",
                   measured is not None and abs(measured - predicted) / predicted < 0.4))
    checks.append(("edge: zero measurement error gives a forecast that never fails", L.forecast_horizon(s0, (0.0, 0.0, 0.0, 0.0), duration=10.0) is None))
    med6 = L.median_horizon(s0, 1e-6, n_dirs=8, duration=30.0)
    med9 = L.median_horizon(s0, 1e-9, n_dirs=8, duration=40.0)
    checks.append((f"mini-project: median horizon is {med6:.1f} s for error 1e-6 and {med9:.1f} s for 1e-9 (gain {med9 - med6:.1f} s, between 3 and 9 s)",
                   med6 is not None and med9 is not None and 3.0 < med9 - med6 < 9.0 and 7.0 < med6 < 13.0))
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
