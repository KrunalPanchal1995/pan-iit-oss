"""Checkpoint for Session 5. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    f = 22.5
    a30, a24, a25 = (L.signed_alias(f, r) for r in (30, 24, 25))

    # ---- the worked example and the roadmap line -----------------------------------------------
    checks.append(("hand calculation: 22.5 rev/s looks like -7.5, -1.5 and -2.5 rev/s at 30, 24 and 25 fps",
                   (a30, a24, a25) == (-7.5, -1.5, -2.5)))
    two = L.common_speeds([a30, a24], [30, 24], 0, 400)
    checks.append(("two clips (30, 24) leave 4 candidates below 400 rev/s: 22.5, 142.5, 262.5 and 382.5", two == [22.5, 142.5, 262.5, 382.5]))
    three = L.common_speeds([a30, a24, a25], [30, 24, 25], 0, 400)
    checks.append(("roadmap line: with 30, 24 and 25 fps the true speed 22.5 rev/s is the only candidate below 400 rev/s", three == [22.5]))
    checks.append(("the range is lcm(30, 24, 25) = 600: 22.5 and 622.5 rev/s look identical on all three clips, and nothing else below 1000 does",
                   L.unambiguous_range([30, 24, 25]) == 600 and L.common_speeds([a30, a24, a25], [30, 24, 25], 0, 1000) == [22.5, 622.5]))

    # ---- independent brute force over the whole range -------------------------------------------
    bad = 0
    for g in np.arange(0.5, 599.6, 0.5):
        aa = [L.signed_alias(float(g), r) for r in (30, 24, 25)]
        bad += L.common_speeds(aa, [30, 24, 25], 0, 599.9) != [float(g)]
    checks.append((f"exact recovery is unique for every speed from 0.5 to 599.5 rev/s in steps of 0.5 ({bad} failures out of 1199)", bad == 0))
    rng = np.random.default_rng(1)
    same = 0
    for _ in range(300):
        g = float(rng.uniform(1, 399))
        aa = [L.signed_alias(g, r) for r in (30, 24, 25)]
        same += len(L.common_speeds(aa, [30, 24, 25], 0, 400, 1e-6)) == 1
    checks.append(("300 random speeds below 400 rev/s: exactly one candidate each time", same == 300))

    # ---- when a third rate helps -----------------------------------------------------------------
    helpless = [r for r in range(20, 61) if not L.third_rate_helps(30, 24, r)]
    brute = [r for r in range(20, 61) if 120 % r == 0]
    checks.append((f"a third rate next to 30 and 24 fps adds nothing exactly when it divides 120: {helpless}", helpless == brute == [20, 24, 30, 40, 60]))
    aa = [L.signed_alias(22.5, r) for r in (30, 24, 20)]
    checks.append(("a third clip at 20 fps changes nothing: still 4 candidates below 400 rev/s (as with two clips)",
                   L.common_speeds(aa, [30, 24, 20], 0, 400) == [22.5, 142.5, 262.5, 382.5]))
    checks.append(("a helpful third rate is not always enough: 36 fps gives only 360 rev/s, so 22.5 and 382.5 both survive below 400",
                   L.unambiguous_range([30, 24, 36]) == 360
                   and L.common_speeds([L.signed_alias(22.5, r) for r in (30, 24, 36)], [30, 24, 36], 0, 400) == [22.5, 382.5]))
    tab = {r: (rg, h) for r, rg, h in L.rate_table(30, 24, [25, 29, 40])}
    checks.append(("range table: third rates 25, 29 and 40 fps give 600, 3480 and 120 rev/s", tab[25] == (600, True) and tab[29] == (3480, True) and tab[40] == (120, False)))

    # ---- noisy clips ------------------------------------------------------------------------------
    t3 = L.run_trials([30, 24, 25], 0.3, 1000, seed=0)
    t2 = L.run_trials([30, 24], 0.3, 1000, seed=0)
    checks.append((f"noisy clips (0.3 rev/s), true speed uniform 5 to 399 rev/s: three clips are within 0.5 rev/s in {t3:.1%} of 1000 trials; two clips in only {t2:.0%} (the range is 120)",
                   t3 >= 0.98 and t2 < 0.40))
    rng = np.random.default_rng(5)
    err, cover = [], 0
    for _ in range(1500):
        g = rng.uniform(5, 59)
        a = [L.signed_alias(g, r) + rng.normal(0, 0.5) for r in (30, 24, 25)]
        r_ = L.recover_noisy_n(a, [30, 24, 25], 0.5, 5, 59)
        err.append(r_["f"] - g)
        cover += abs(r_["f"] - g) <= 2 * r_["sd"]
    err = np.array(err)
    checks.append((f"uncertainty with three clips: sd = sigma / sqrt(3) = {0.5 / math.sqrt(3):.3f}; the errors have sd {err.std():.3f} and the +-2 sd band holds {cover / 1500:.1%} (95.4% expected)",
                   abs(err.std() / (0.5 / math.sqrt(3)) - 1) < 0.07 and abs(cover / 1500 - 0.954) < 0.02))
    ok2 = np.std([L.recover_noisy_n([L.signed_alias(g, r) + rng.normal(0, 0.5) for r in (30, 24)], [30, 24], 0.5, 5, 59)["f"] - g
                  for g in rng.uniform(5, 59, 1500)])
    checks.append((f"a third clip lowers the noise by sqrt(2/3) = 0.82: sd {ok2:.3f} with two clips, {err.std():.3f} with three (sigma = 0.5)", abs(err.std() / ok2 - math.sqrt(2 / 3)) < 0.06))
    pred = all(abs(L.run_trials([30, 24, 25], s, 800, seed=2) - L.predicted_within(s, 3)) < 0.03 for s in (0.4, 0.6))
    checks.append(("the share within 0.5 rev/s follows erf(0.5 sqrt(3) / (sigma sqrt 2)) at sigma = 0.4 and 0.6 (to 3 points): no rule beats it", pred))
    checks.append(("with two clips the same formula gives Session 4's erf(0.5 / sigma)", abs(L.predicted_within(0.3, 2) - math.erf(0.5 / 0.3)) < 1e-12))
    r0 = L.recover_noisy_n([a30, a24, a25], [30, 24, 25], 0.0, 5, 399)
    checks.append(("without noise the answer is exact: 22.5 with sd 0 and an infinite margin", r0["f"] == 22.5 and r0["sd"] == 0.0 and r0["margin"] == math.inf))
    rm = L.recover_noisy_n([a30 + 0.2, a24 - 0.2, a25 + 0.1], [30, 24, 25], 0.3, 5, 399)
    checks.append((f"margin: a slightly noisy trial of 22.5 rev/s gives {rm['f']:.2f} and the best set beats the runner-up by {rm['margin']:.0f} sigma", abs(rm["f"] - 22.5) < 0.2 and rm["margin"] > 5))

    # ---- edges ----------------------------------------------------------------------------------------
    rng = np.random.default_rng(7)
    edge = {}
    for g in (5.0, 399.0):
        ok = 0
        for _ in range(500):
            a = [L.signed_alias(g, r) + rng.normal(0, 0.3) for r in (30, 24, 25)]
            r_ = L.recover_noisy_n(a, [30, 24, 25], 0.3, 5, 399)
            ok += abs(r_["f"] - g) <= 0.5 and 5 <= r_["f"] <= 399
        edge[g] = ok / 500
    checks.append((f"the edges of the range are recovered ({edge[5.0]:.0%} at 5 rev/s, {edge[399.0]:.0%} at 399 rev/s within 0.5) and the answer never leaves it", min(edge.values()) >= 0.97))
    errs = 0
    for fn in (lambda: L.common_speeds([a30], [30]),
               lambda: L.common_speeds([a30, a24], [30, 24, 25]),
               lambda: L.unambiguous_range([30, 24.5]),
               lambda: L.recover_noisy_n([a30, a24], [30, 24], -0.1),
               lambda: L.recover_noisy_n([a30, a24], [30, 24], 0.3, 399, 5),
               lambda: L.recover_noisy_n([a30, a24, a25], [30, 24, 25], 0.3, 0, 100000)):
        try:
            fn()
        except ValueError:
            errs += 1
    checks.append(("a single clip, mismatched lists, a fractional rate, a negative sigma, a reversed range and a search that is far too large are refused with a clear error", errs == 6))
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
