"""Checkpoint for Session 5. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # worked example: sampling error and ensemble size by hand
    se = L.standard_error(0.77, 1000)
    n_need = L.members_needed(0.77, 0.01)
    checks.append((f"worked example: sqrt(0.77 x 0.23 / 1000) = 0.0133, 4 times as many members halve it ({L.standard_error(0.77, 4000):.4f}), and 0.77 +/- 0.01 needs {n_need} members",
                   abs(se - 0.01331) < 1e-4 and abs(L.standard_error(0.77, 4000) - se / 2) < 1e-12 and n_need == 1771))

    # equations: numbers and arrays agree
    st = (0.7, -1.1, 0.4, 2.0)
    r_scalar = np.array(L.rate(st))
    r_array = np.array([float(x[0]) for x in L.rate(tuple(np.array([v]) for v in st))])
    checks.append(("the rate function gives the same numbers for single values and for arrays", bool(np.allclose(r_scalar, r_array))))

    # the cloud itself
    e0 = L.run_ensemble(120.0, duration=0.1)
    cloud = e0["theta2"][0]
    checks.append((f"the cloud is Gaussian around the release: mean {cloud.mean() - math.radians(120):+.1e} rad from 120 degrees, standard deviation {cloud.std():.2e} (1e-6 expected)",
                   abs(cloud.mean() - math.radians(120)) < 4e-6 / math.sqrt(1000) and abs(cloud.std() / 1e-6 - 1) < 0.1 and abs(float(np.mean(((cloud - cloud.mean()) / cloud.std()) ** 3))) < 0.25))
    same = L.run_ensemble(120.0, duration=0.1)
    checks.append(("the same seed gives the same cloud, another seed a different one",
                   bool(np.array_equal(same["theta2"], e0["theta2"])) and not np.array_equal(L.run_ensemble(120.0, duration=0.1, seed=2)["theta2"], e0["theta2"])))

    # edge: no start error means no spread and no probability between 0 and 1
    e_zero = L.run_ensemble(120.0, n=20, sigma=0.0, duration=10.0)
    checks.append(("edge: with zero start error the spread stays 0 and every member flips at the same time (probability 1)",
                   float(L.spread_curve(e_zero).max()) < 1e-12 and L.flip_probability(e_zero["flip"], 10.0) == 1.0))

    # 120 degree release: spread time and flip probability, two seeds
    e1 = L.run_ensemble(120.0, seed=1, duration=25.0)
    e2 = L.run_ensemble(120.0, seed=2, duration=25.0)
    sp1, sp2 = L.spread_curve(e1), L.spread_curve(e2)
    t1, t2 = L.first_time_above(e1["t"], sp1, 0.5), L.first_time_above(e2["t"], sp2, 0.5)
    p1, p2 = L.flip_probability(e1["flip"], 20.0), L.flip_probability(e2["flip"], 20.0)
    checks.append((f"120 degrees: the spread of theta2 first exceeds 0.5 rad at {t1:.2f} s and {t2:.2f} s for two seeds (within 0.5 s, between 9.5 and 11.5 s)",
                   t1 is not None and t2 is not None and abs(t1 - t2) < 0.5 and 9.5 < t1 < 11.5))
    checks.append((f"120 degrees: every member has flipped by 20 s (probability {p1:.3f} and {p2:.3f})", p1 == 1.0 and p2 == 1.0))
    checks.append((f"the spread starts at about 1e-6 rad ({sp1[0]:.1e}) and is still below 1e-3 rad after 5 s ({sp1[100]:.1e})",
                   abs(sp1[0] / 1e-6 - 1) < 0.1 and sp1[100] < 1e-3))
    lam = L.growth_rate_from_spread(e1["t"], sp1)
    checks.append((f"the spread grows like exp(lambda t) with lambda = {lam:.2f} per second (between 0.8 and 1.6; Session 3 measured 1.2 to 1.4 from two close runs)", 0.8 < lam < 1.6))
    ft = L.deterministic_flip_time(120.0)
    checks.append((f"the single exact start (no cloud) first flips at {ft:.2f} s, where the whole cloud flips (median {np.median(e1['flip']):.2f} s)",
                   ft is not None and 6.8 < ft < 7.0 and abs(np.median(e1["flip"]) - ft) < 0.1))

    # 95 degree release: a real probability
    f1 = L.run_ensemble(95.0, seed=1, duration=25.0)
    f2 = L.run_ensemble(95.0, seed=2, duration=25.0)
    q1, q2 = L.flip_probability(f1["flip"], 20.0), L.flip_probability(f2["flip"], 20.0)
    s1 = L.first_time_above(f1["t"], L.spread_curve(f1), 0.5)
    s2 = L.first_time_above(f2["t"], L.spread_curve(f2), 0.5)
    checks.append((f"95 degrees: probability of a flip by 20 s is {q1:.3f} and {q2:.3f} for two seeds, within four standard errors of each other and between 0.70 and 0.85",
                   abs(q1 - q2) < 4 * math.sqrt(2) * L.standard_error(q1, 1000) and 0.70 < q1 < 0.85 and 0.70 < q2 < 0.85))
    checks.append((f"95 degrees: spread time {s1:.2f} s and {s2:.2f} s (within 0.5 s of each other, between 12 and 14 s)",
                   s1 is not None and s2 is not None and abs(s1 - s2) < 0.5 and 12.0 < s1 < 14.0))
    curve = L.flip_probability_curve(f1)
    checks.append((f"the probability curve never decreases, is 0 at 10 s ({curve[200]:.1f}) and {curve[-1]:.2f} at 25 s (between 0.90 and 0.99)",
                   bool(np.all(np.diff(curve) >= 0)) and curve[200] == 0.0 and 0.90 < curve[-1] < 0.99))
    ft95 = L.deterministic_flip_time(95.0)
    checks.append((f"honesty check: the single exact 95 degree start flips at {ft95:.2f} s (before 20 s) although the forecast says only {q1:.2f}; a probability is right on average, not for every case",
                   ft95 is not None and 19.0 < ft95 < 19.4 and q1 < 0.9))

    # numerical convergence: the time step moves the probability more than sampling does
    p_coarse = L.flip_probability(L.run_ensemble(95.0, seed=1, duration=21.0, h=0.01)["flip"], 20.0)
    p_fine = L.flip_probability(L.run_ensemble(95.0, seed=1, duration=21.0, h=0.0025)["flip"], 20.0)
    checks.append((f"step check: h = 0.01 s gives P = {p_coarse:.3f}, h = 0.005 s gives {q1:.3f}, h = 0.0025 s gives {p_fine:.3f}; the coarse step is off by more than 0.04, the middle one by less",
                   abs(p_coarse - p_fine) > 0.04 and abs(q1 - p_fine) < 0.04))

    # mini-project: how good an instrument
    lad = L.precision_ladder(95.0, [1e-8, 1e-6, 1e-4], duration=30.0)
    st_ = [r[1] for r in lad]
    gains = (st_[0] - st_[1], st_[1] - st_[2])
    lam95 = L.growth_rate_from_spread(f1["t"], L.spread_curve(f1))
    pred = math.log(100) / lam95
    checks.append((f"mini-project: each 100 times better instrument delays the spread time by {gains[0]:.1f} s and {gains[1]:.1f} s (spread times {st_[0]:.1f}, {st_[1]:.1f}, {st_[2]:.1f} s), about ln(100) / lambda = {pred:.1f} s each (within a factor 2)",
                   all(s is not None for s in st_) and all(0.5 * pred < g < 2 * pred for g in gains)))
    checks.append((f"mini-project: at sigma = 1e-4 the flip probability is {lad[2][2]:.2f} (above 0.9) and at 1e-6 it is {lad[1][2]:.2f} with standard error {lad[1][3]:.3f}",
                   lad[2][2] > 0.9 and 0.70 < lad[1][2] < 0.85 and 0.005 < lad[1][3] < 0.02))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson5", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
