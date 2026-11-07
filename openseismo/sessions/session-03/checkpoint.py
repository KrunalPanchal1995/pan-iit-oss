"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    Q = L.QUAKE
    t_true = L.p_arrivals(Q, L.GOOD)
    m, hist, J = L.geiger(L.GOOD, t_true)
    checks.append(("noise-free picks: Geiger recovers (55, 40) km and t0 = 3 s", np.allclose(m, Q, atol=1e-6)))
    err0 = np.hypot(hist[0][0] - 55, hist[0][1] - 40)
    err1 = np.hypot(hist[1][0] - 55, hist[1][1] - 40)
    checks.append(("convergence: error falls from 13.9 km to 0.21 km in one step and to ~0 in the next",
                   abs(err0 - 13.93) < 0.02 and abs(err1 - 0.208) < 0.005 and len(hist) - 1 <= 6))
    # hand calculation of one Jacobian row at the truth: station (5, 10), R = sqrt(50^2 + 30^2) = 58.31 km
    row = J[0]
    R = np.hypot(50.0, 30.0)
    checks.append(("hand calculation: Jacobian row of station (5, 10) is (50, 30, 1)/(6 R) with R = 58.31 km",
                   abs(R - 58.31) < 0.01 and np.allclose(row, [50.0 / (6.0 * R), 30.0 / (6.0 * R), 1.0], atol=1e-12)))
    checks.append(("worked example: the same Jacobian entries are 0.143 and 0.086 s/km",
                   abs(row[0] - 0.1429) < 5e-4 and abs(row[1] - 0.0857) < 5e-4))
    from_far = L.geiger(L.GOOD, t_true, start=(90.0, 90.0, 0.0))[0]
    checks.append(("a different starting guess reaches the same answer", np.allclose(from_far, Q, atol=1e-6)))
    try:
        L.geiger(L.GOOD[:3], t_true[:3])
        bad = False
    except ValueError:
        bad = True
    checks.append(("fewer than 4 stations is rejected", bad))

    # Monte Carlo scatter and linear theory
    e1 = L.monte_carlo(L.GOOD, Q, 0.1, n=1000)
    e2 = L.monte_carlo(L.GOOD, Q, 0.2, n=1000)
    dil = L.horizontal_dilution(J)
    pred_mean = 0.1 * dil / np.sqrt(2.0) * np.sqrt(np.pi / 2.0)
    checks.append(("surrounding network, sigma 0.1 s: median error 0.45 km, 95th percentile 0.93 km",
                   abs(np.median(e1) - 0.45) < 0.02 and abs(np.percentile(e1, 95) - 0.93) < 0.05))
    checks.append(("doubling sigma doubles the error (ratio 2.0 within 5 percent)",
                   abs(np.mean(e2) / np.mean(e1) - 2.0) < 0.1))
    checks.append(("Monte Carlo mean error agrees with the covariance prediction within 10 percent",
                   abs(np.mean(e1) / pred_mean - 1.0) < 0.10))
    # geometry
    Jb = L.geiger(L.BAD, L.p_arrivals(Q, L.BAD))[2]
    checks.append(("condition number: 9.2 for the surrounding network, 195 for the one-sided one",
                   abs(L.condition_number(J) - 9.2) < 0.1 and abs(L.condition_number(Jb) - 194.7) < 1.0))
    checks.append(("horizontal dilution: 5.5 km/s (surrounding) against 85 km/s (one-sided)",
                   abs(dil - 5.51) < 0.02 and abs(L.horizontal_dilution(Jb) - 85.4) < 0.5))
    eb = L.monte_carlo(L.BAD, Q, 0.1, n=1000)
    checks.append(("one-sided network at sigma 0.1 s: median error 5.6 km and 95th percentile near 20 km",
                   abs(np.median(eb) - 5.59) < 0.3 and 15.0 < np.percentile(eb, 95) < 25.0))
    checks.append(("one-sided median error is more than 10 times worse than surrounding", np.median(eb) > 10 * np.median(e1)))
    # ellipse coverage
    C = L.covariance(J, 0.1)[:2, :2]
    Ci = np.linalg.inv(C)
    rng = np.random.default_rng(11)
    inside = 0
    for _ in range(1000):
        mm = L.geiger(L.GOOD, t_true + 0.1 * rng.standard_normal(5))[0]
        d = mm[:2] - Q[:2]
        inside += d @ Ci @ d <= 5.991
    checks.append(("95 percent ellipse contains the true epicentre in 93 to 97 percent of 1000 trials", 0.93 <= inside / 1000 <= 0.97))
    # two-layer toy
    checks.append(("two-layer crossover distance is 73.5 km", abs(L.crossover_distance() - 73.48) < 0.02))
    x = np.array([10.0, 50.0, 150.0])
    t2 = L.first_arrival_two_layer(x)
    checks.append(("two-layer first arrivals: 2.00 s direct at 10 km, 10.00 s direct at 50 km, 25.6 s head wave at 150 km",
                   abs(t2[0] - 2.0) < 1e-9 and abs(t2[1] - 10.0) < 1e-9 and abs(t2[2] - 25.63) < 0.05))
    _, e_good, rms_good = L.locate_layered(L.GOOD, Q)
    _, e_bad, rms_bad = L.locate_layered(L.BAD, Q)
    checks.append(("constant-speed assumption: epicentre off by 1.32 km (surrounding) and 19.0 km (one-sided)",
                   abs(e_good - 1.32) < 0.03 and abs(e_bad - 18.99) < 0.2))
    checks.append(("the bias hides: rms residual only 0.077 s (surrounding), similar to pick noise",
                   abs(rms_good - 0.077) < 0.003 and rms_bad > rms_good))
    _, e_ok, rms_ok = L.locate_layered(L.GOOD, Q, v_assumed=5.0)
    checks.append(("limit: using the true layer speed 5.0 km/s (all arrivals direct) gives zero error", e_ok < 1e-6 and rms_ok < 1e-9))
    # magnitude
    checks.append(("worked example: 2 mm amplitude with S-P 11.9 s gives ML 3.3 (hand: 0.30 + 5.94 - 2.92)",
                   abs(L.ml_magnitude(2.0, 11.905) - 3.317) < 0.005 and abs(0.301 + 5.936 - 2.92 - 3.317) < 0.005))
    checks.append(("ten times the amplitude adds exactly 1.0 to ML", abs(L.ml_magnitude(20.0, 11.905) - L.ml_magnitude(2.0, 11.905) - 1.0) < 1e-12))
    checks.append(("amplitude_from_ml undoes ml_magnitude", abs(L.amplitude_from_ml(L.ml_magnitude(2.0, 11.905), 11.905) - 2.0) < 1e-9))
    checks.append(("farther quake (larger S-P) needs a smaller amplitude for the same ML: 8 times for double the gap",
                   abs(L.amplitude_from_ml(3.0, 10.0) / L.amplitude_from_ml(3.0, 20.0) - 8.0) < 1e-9))
    # mini-project
    r = L.mini_project()
    d = r["m"][:2] - Q[:2]
    inside_mp = d @ Ci @ d <= 5.991
    checks.append(("mini-project (seed 3, sigma 0.1 s): error 0.67 km, ellipse 1.01 x 0.90 km, truth inside it",
                   abs(r["error_km"] - 0.67) < 0.01 and abs(r["semi_major"] - 1.006) < 0.01 and abs(r["semi_minor"] - 0.90) < 0.02 and inside_mp))
    outl = []
    for k in range(5):
        tt = t_true.copy()
        tt[k] += 3.0
        mo = L.geiger(L.GOOD, tt)[0]
        outl.append(np.hypot(mo[0] - Q[0], mo[1] - Q[1]))
    checks.append(("a +3 s blunder in one pick moves the epicentre by 5 to 9 km (any of the five stations)", all(5.0 < o < 9.0 for o in outl)))
    more = np.vstack([L.BAD, [[100.0, 90.0]]])
    Jm = L.geiger(more, L.p_arrivals(Q, more))[2]
    checks.append(("adding one far station to the one-sided network cuts the dilution from 85 to below 12 km/s", L.horizontal_dilution(Jm) < 12.0))
    checks.append(("exercise: S-P 20 s and 2 mm amplitude give ML 3.99", abs(L.ml_magnitude(2.0, 20.0) - 3.993) < 0.005))
    g2 = np.median(L.monte_carlo(L.GOOD, Q, 0.2, n=1000))
    b2 = np.median(L.monte_carlo(L.BAD, Q, 0.2, n=1000))
    checks.append(("sigma 0.2 s: medians 0.91 km (surrounding) and 10.9 km (one-sided), about twelve times worse",
                   abs(g2 - 0.91) < 0.03 and abs(b2 - 10.9) < 0.6 and 11.0 < b2 / g2 < 13.0))
    checks.append(("start at the station centroid is 13.9 km from the truth", abs(np.hypot(50.0 - 55.0, 53.0 - 40.0) - 13.93) < 0.01))
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
