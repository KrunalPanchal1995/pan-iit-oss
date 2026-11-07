"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # ---- hand numbers and the noise of a measured speed ----------------------------------------
    checks.append(("hand calculation: 22.5 rev/s looks like -7.5 rev/s at 30 fps and -1.5 rev/s at 24 fps",
                   abs(L.signed_alias(22.5, 30) + 7.5) < 1e-9 and abs(L.signed_alias(22.5, 24) + 1.5) < 1e-9))
    rng = np.random.default_rng(0)
    worst = 0.0
    for n, sd, f in ((5, 0.18, 11.3), (10, 0.05, 7.1), (40, 0.05, 3.3)):
        mc = np.std([L.measured_speed(f, 30, n, sd, rng) for _ in range(4000)])
        worst = max(worst, abs(mc / L.speed_noise(sd, n, 30) - 1))
    checks.append((f"noise of a measured speed: simulation matches fs sqrt(2) angle_sd / (2 pi (n - 1)) within 8% for 3 clips (worst {worst:.1%}); a 5 frame clip with a marker 3.6 pixels off gives 0.30 rev/s",
                   worst < 0.08 and abs(L.speed_noise(0.18, 5, 30) - 0.304) < 0.002))

    # ---- why exact matching fails ---------------------------------------------------------------
    a1, a2 = L.signed_alias(22.5, 30), L.signed_alias(22.5, 24)
    checks.append(("without noise the Session 3 rule gives exactly 22.5 in the range 5 to 59",
                   L.recover_exact(a1, 30, a2, 24, 5, 59, 1e-6) == [22.5]))
    ex, ex_ans = L.run_trials("exact", 0.3, 2000, seed=0)
    checks.append((f"with 0.3 rev/s of noise the Session 3 rule is right in only {ex:.0%} of 2000 trials (theory erf(0.5) = 52%); the rest get no answer ({1 - ex_ans:.0%})",
                   0.48 < ex < 0.56 and abs(ex_ans - ex) < 0.03))

    # ---- the best-pair recovery against the roadmap line ------------------------------------------
    pr, pr_ans = L.run_trials("pairs", 0.3, 2000, seed=0)
    checks.append((f"roadmap line: with 0.3 rev/s of noise the best pair is within 0.5 rev/s in {pr:.1%} of 2000 trials (needed: 95%), and always answers ({pr_ans:.0%})",
                   pr >= 0.95 and pr_ans == 1.0))
    wd, wd_ans = L.run_trials("wide", 0.3, 2000, seed=0)
    checks.append((f"a wide tolerance (1.3) also works at 0.3 ({wd:.1%}) but stays silent in {1 - wd_ans:.1%} of the trials; at sigma = 1 it is right {L.run_trials('wide', 1.0, 1000, seed=1)[0]:.0%} against {L.run_trials('pairs', 1.0, 1000, seed=1)[0]:.0%} for the best pair",
                   0.95 <= wd < pr + 0.01 and wd_ans < 1.0 and L.run_trials("wide", 1.0, 1000, seed=1)[0] + 0.1 < L.run_trials("pairs", 1.0, 1000, seed=1)[0]))

    # ---- independent check: brute-force maximum likelihood on a fine grid ---------------------------
    grid = np.arange(5.0, 59.0 + 1e-9, 0.005)

    def wrap(d, fs):
        return d - fs * np.round(d / fs)

    def sa(f, fs):
        return f - fs * np.floor(f / fs + 0.5)

    rng = np.random.default_rng(3)
    agree, n_t = 0, 300
    for _ in range(n_t):
        f = rng.uniform(5, 59)
        b1, b2 = L.noisy_apparent(f, 30, 0.3, rng), L.noisy_apparent(f, 24, 0.3, rng)
        chi = wrap(b1 - sa(grid, 30), 30) ** 2 + wrap(b2 - sa(grid, 24), 24) ** 2
        ml = grid[int(np.argmin(chi))]
        agree += abs(ml - L.recover_noisy(b1, 30, b2, 24, 0.3)["f"]) < 0.02
    checks.append((f"the best pair is the maximum-likelihood answer: it agrees with a brute-force search of 10800 candidate speeds in {agree} of {n_t} trials (to 0.02 rev/s)", agree >= 0.98 * n_t))

    # ---- uncertainty ------------------------------------------------------------------------------
    rng = np.random.default_rng(5)
    err, cover = [], 0
    for _ in range(3000):
        f = rng.uniform(5, 59)
        b1, b2 = L.noisy_apparent(f, 30, 0.3, rng), L.noisy_apparent(f, 24, 0.3, rng)
        r = L.recover_noisy(b1, 30, b2, 24, 0.3)
        err.append(r["f"] - f)
        cover += abs(r["f"] - f) <= 2 * r["sd"]
    err = np.array(err)
    checks.append((f"the reported uncertainty is honest: sd = sigma / sqrt(2) = {0.3 / math.sqrt(2):.3f}; the errors have sd {err.std():.3f} and the +-2 sd band holds {cover / 3000:.1%} of them (95.4% expected)",
                   abs(err.std() / (0.3 / math.sqrt(2)) - 1) < 0.06 and abs(cover / 3000 - 0.954) < 0.02))
    pred_ok = all(abs(L.run_trials("pairs", s, 2000, seed=2)[0] - L.predicted_within(s)) < 0.025 for s in (0.3, 0.5, 0.7))
    checks.append(("the chance of being within 0.5 rev/s follows erf(0.5 / sigma) at sigma = 0.3, 0.5 and 0.7 (to 2.5 points): no rule can do better with two numbers", pred_ok))
    checks.append(("a speed measured twice with no noise is exact: the answer is 22.5 with sd 0 and an infinite margin",
                   L.recover_noisy(a1, 30, a2, 24, 0.0, 5, 59)["f"] == 22.5 and L.recover_noisy(a1, 30, a2, 24, 0.0, 5, 59)["sd"] == 0.0
                   and L.recover_noisy(a1, 30, a2, 24, 0.0, 5, 59)["margin"] == math.inf))
    r0 = L.recover_noisy(a1, 30, a2, 24, 0.3, 5, 59)
    checks.append((f"margin: the true pair of 30 and 24 fps beats the runner-up by {r0['margin']:.0f} sigma (6 rev/s apart), so the choice of pair is safe", r0["margin"] > 10))

    # ---- which pair of frame rates --------------------------------------------------------------------
    r29 = L.run_trials("pairs", 0.3, 1000, seed=4, fs2=29.0)[0]
    r24 = L.run_trials("pairs", 0.3, 1000, seed=4, fs2=24.0)[0]
    checks.append((f"design: rates 30 and 29 reach 870 rev/s but, with gcd 1, a wrong pair wins when the two errors differ by more than 0.5 rev/s: {r29:.0%} within 0.5 against {r24:.0%} for 30 and 24",
                   r29 < 0.92 and r24 >= 0.95))
    rng = np.random.default_rng(6)
    wrong = {}
    for p in (24, 29):
        w = 0
        for _ in range(1500):
            f = rng.uniform(5, 59)
            b1, b2 = L.noisy_apparent(f, 30, 0.6, rng), L.noisy_apparent(f, p, 0.6, rng)
            w += abs(L.recover_noisy(b1, 30, b2, p, 0.6)["f"] - f) > 3
        wrong[p] = w / 1500
    checks.append((f"wrong pairs at sigma = 0.6: bound {L.wrong_pair_probability(0.6, 30, 24):.3f} and measured {wrong[24]:.3f} for 30/24 fps; bound {L.wrong_pair_probability(0.6, 30, 29):.2f} and measured {wrong[29]:.2f} for 30/29 fps (the bound holds)",
                   wrong[24] <= L.wrong_pair_probability(0.6, 30, 24) + 0.01 and wrong[29] <= L.wrong_pair_probability(0.6, 30, 29) + 0.02 and wrong[29] > 5 * wrong[24] + 0.1))

    # ---- edges ----------------------------------------------------------------------------------------
    rng = np.random.default_rng(7)
    edge = {}
    for f in (5.0, 59.0):
        ok = 0
        for _ in range(1000):
            b1, b2 = L.noisy_apparent(f, 30, 0.3, rng), L.noisy_apparent(f, 24, 0.3, rng)
            r = L.recover_noisy(b1, 30, b2, 24, 0.3)
            ok += abs(r["f"] - f) <= 0.5 and 5.0 <= r["f"] <= 59.0
        edge[f] = ok / 1000
    checks.append((f"edges of the range: the true speeds 5 and 59 rev/s are still recovered ({edge[5.0]:.0%}, {edge[59.0]:.0%} within 0.5) because rungs are searched 4 sigma beyond the range, and the answer never leaves it",
                   min(edge.values()) >= 0.95))
    errs = 0
    for fn in (lambda: L.recover_noisy(a1, 30, a2, 24, -0.1),
               lambda: L.recover_noisy(a1, 30, a2, 24, 0.3, 59, 5),
               lambda: L.recover_noisy(a1, 30, a2, 24, 0.0, 30.0, 31.0),
               lambda: L.run_trials("bogus", 0.3),
               lambda: L.speed_noise(0.1, 1, 30)):
        try:
            fn()
        except ValueError:
            errs += 1
    checks.append(("a negative sigma, a reversed range, a range with no pair of rungs, an unknown rule and a one-frame clip are refused with a clear error", errs == 5))
    checks.append(("the same seed gives the same trials (results can be reproduced)",
                   L.run_trials("pairs", 0.3, 200, seed=9) == L.run_trials("pairs", 0.3, 200, seed=9)))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
