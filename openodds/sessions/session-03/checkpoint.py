"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def _raises(f):
    try:
        f()
    except ValueError:
        return True
    return False


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    p = L.exact_sum_at_least(9)
    checks.append(("exact P(sum >= 9) = 10/36", abs(p - 10 / 36) < 1e-12))
    est = L.estimate_sum_probability(9, 1000000, seed=1)
    checks.append(("1000000 simulated rolls are within 4 standard errors of 10/36", abs(est - p) < 4 * L.standard_error(p, 1000000)))
    checks.append(("same seed gives the same estimate", L.estimate_sum_probability(9, 5000, 4) == L.estimate_sum_probability(9, 5000, 4)))
    checks.append(("hand calculation: SE for p = 0.5, N = 100 is 0.05", abs(L.standard_error(0.5, 100) - 0.05) < 1e-12))
    checks.append(("worked example: p = 0.5 and half-width 0.01 need N = 9604 trials", L.trials_needed(0.5, 0.01) == 9604))
    checks.append(("ten times the accuracy needs about 100 times the trials",
                   abs(L.trials_needed(0.3, 0.001) / L.trials_needed(0.3, 0.01) - 100) < 0.1))
    errs = [abs(L.estimate_sum_probability(9, 400, seed=s) - p) for s in range(1, 201)]
    checks.append(("about 95 percent of N = 400 estimates fall within 1.96 SE", 0.90 <= np.mean(np.array(errs) <= 1.96 * L.standard_error(p, 400)) <= 0.99))
    checks.append(("birthday simulation for 23 people is close to 0.507", abs(L.estimate_birthday(23, 60000, seed=2) - 0.5073) < 0.01))
    frac, cnt = L.next_flip_after_streak(400000, 5, seed=3)
    checks.append(("gambler's fallacy: after 5 heads the next flip is still about 50 percent heads", cnt > 5000 and abs(frac - 0.5) < 0.02))
    checks.append(("lottery: C(49, 6) = 13983816 exactly", L.LOTTERY_TOTAL == 13983816 == math.comb(49, 6)))
    checks.append(("worked example: Rs 100 ticket, Rs 10 crore jackpot, expected loss Rs 92.85",
                   abs(L.lottery_expected_loss(100, 1e8) - 92.85) < 0.01))
    checks.append(("fair game: payout 36 for price 10 when p = 10/36", abs(L.fair_payout(10, p) - 36) < 1e-9))
    m, se = L.simulate_game(10, 36, 200000, seed=5)
    checks.append(("the fair game averages within 3 SE of 0", abs(m) < 3 * se))
    m2, se2 = L.simulate_game(10, 30, 200000, seed=5)
    checks.append(("an unfair payout of 30 shows a clear loss (expected -1.667)", m2 < -10 * se2 and abs(m2 + 1.667) < 0.2))
    checks.append(("failure case: 200000 simulated draws find no jackpot", L.simulate_lottery(100000, seed=1) == 0))
    checks.append(("failure case: 30 percent accuracy needs over 100 million draws", L.draws_for_relative_error(1 / L.LOTTERY_TOTAL, 0.3) > 1e8))
    checks.append(("edge case: zero half-width is rejected", _raises(lambda: L.trials_needed(0.5, 0))))
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
