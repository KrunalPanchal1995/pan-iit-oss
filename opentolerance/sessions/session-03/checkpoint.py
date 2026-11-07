"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    lsl, usl = L.spec_limits()
    checks.append(("gap nominal is 2.00 mm and the limits are 1.70 to 2.30 mm",
                   abs(L.GAP_NOMINAL - 2.0) < 1e-9 and abs(lsl - 1.7) < 1e-9 and abs(usl - 2.3) < 1e-9))

    # worked example: five parts, +-0.10 mm each
    t = np.full(5, 0.10)
    wc, rs = L.worst_case_tol(t), L.rss_tol(t)
    sg = L.sigma_gap(t)
    checks.append((f"worked example: worst case 0.500, RSS 0.224 mm (got {wc:.3f}, {rs:.3f})",
                   abs(wc - 0.5) < 1e-9 and abs(rs - 0.2236) < 1e-4))
    checks.append(("worked example: sigma of the gap is 0.0745 mm", abs(sg - 0.0745) < 1e-4))
    checks.append(("worked example: Cp is 1.34 (above the 1.33 guideline)", abs(L.cp(lsl, usl, sg) - 1.3416) < 1e-3))
    checks.append(("worked example: fraction out is 5.7e-5 (0.0057 percent)", abs(L.fraction_out(lsl, usl, 2.0, sg) - 5.70e-5) < 1e-7))

    # validation against exact corner enumeration
    lo, hi = L.corner_range(t)
    checks.append(("corner enumeration (32 corners) gives exactly 2 +- the sum of tolerances", abs(lo - 1.5) < 1e-9 and abs(hi - 2.5) < 1e-9))
    rng = np.random.default_rng(3)
    ok = True
    for _ in range(10):
        tt = rng.uniform(0.02, 0.2, 5)
        a, b = L.corner_range(tt)
        ok &= abs((b - a) / 2 - L.worst_case_tol(tt)) < 1e-9 and L.rss_tol(tt) <= L.worst_case_tol(tt) + 1e-12
    checks.append(("RSS never exceeds the worst-case sum (10 random sets)", bool(ok)))

    # validation against Monte Carlo
    g = L.simulate_gaps(t, n=400_000, seed=5)
    checks.append((f"Monte Carlo sigma matches the RSS formula within 1 percent (got {g.std():.4f})", abs(g.std() / sg - 1) < 0.01))
    checks.append(("Monte Carlo mean is the nominal gap", abs(g.mean() - 2.0) < 5e-4))
    checks.append(("no simulated assembly leaves the worst-case corners", bool(g.min() > lo and g.max() < hi)))
    checks.append(("simulation is repeatable for the same seed", np.array_equal(L.simulate_gaps(t, 1000, 9), L.simulate_gaps(t, 1000, 9))))

    # Cp, Cpk and the erf fraction
    checks.append(("hand calculation: +-3 sigma limits give 0.27 percent out (erf)", abs(L.fraction_out(-3, 3, 0, 1) - 0.0026998) < 1e-6))
    sim = float(np.mean(np.abs(g - 2.0) > 3 * sg))
    checks.append((f"simulation agrees with erf at +-3 sigma within 0.05 percentage points (got {100 * sim:.3f}%)", abs(sim - 0.0027) < 5e-4))
    checks.append(("Cp = 1.333 means limits four sigma away: 6.3e-5 out", abs(L.fraction_out(1.7, 2.3, 2.0, 0.075) - 6.334e-5) < 1e-7
                   and abs(L.cp(1.7, 2.3, 0.075) - 4 / 3) < 1e-9))
    checks.append(("Cpk = Cp for a centred process", abs(L.cpk(1.7, 2.3, 2.0, 0.075) - L.cp(1.7, 2.3, 0.075)) < 1e-9))
    checks.append(("Cpk = 0.889 when the mean is 2.10 mm and sigma 0.075", abs(L.cpk(1.7, 2.3, 2.1, 0.075) - 0.8889) < 1e-3))
    try:
        L.cp(1.7, 2.3, 0.0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("edge: sigma = 0 is rejected", bad))

    # allocation and cost
    target = L.rss_target()
    checks.append(("RSS target for Cp 1.333 is 0.225 mm", abs(target - 0.225) < 1e-9))
    tr = L.allocate_rss(target)
    checks.append(("allocated tolerances meet the RSS target exactly", abs(L.rss_tol(tr) - 0.225) < 1e-9))
    checks.append(("allocation: the cheapest-to-tighten part gets the tightest tolerance",
                   int(np.argmin(tr)) == int(np.argmin(L.K_COST)) and int(np.argmax(tr)) == int(np.argmax(L.K_COST))))
    t_eq = np.full(5, target / math.sqrt(5))
    checks.append((f"mini-project: cost {L.cost(tr):.2f} beats equal allocation {L.cost(t_eq):.2f} by 13 percent",
                   abs(1 - L.cost(tr) / L.cost(t_eq) - 0.1303) < 5e-4))
    # the closed form really is the minimum: random allocations with the same RSS never do better
    best = True
    for _ in range(2000):
        r = rng.uniform(0.2, 1.0, 5)
        r = r * target / np.sqrt(np.sum(r ** 2))
        best &= L.cost(r) >= L.cost(tr) - 1e-9
    checks.append(("no random allocation with the same RSS is cheaper (2000 trials)", bool(best)))
    checks.append(("all five allocated tolerances can be made (>= 0.05 mm)", L.makeable(tr) and abs(tr.min() - 0.0608) < 1e-4))
    checks.append(("equal allocation of identical k gives equal tolerances", np.allclose(L.allocate_rss(0.2, np.ones(5)), 0.2 / math.sqrt(5))))
    tw = L.allocate_worst_case(L.GAP_TOL)
    checks.append(("worst-case allocation sums to 0.30 but needs +-0.029 mm on one part: not makeable", abs(tw.sum() - 0.3) < 1e-9 and not L.makeable(tw)))
    checks.append(("worst-case equal allocation costs 86.67 against 44.94 for RSS",
                   abs(L.cost(np.full(5, 0.06)) - 86.667) < 1e-2 and abs(L.cost(tr) - 44.94) < 1e-2))

    # failure case 1: worst-case design too tight to be made
    t_wc20 = np.full(5, 0.20 / 5)
    t_rss20 = np.full(5, L.rss_target(gap_tol=0.20) / math.sqrt(5))
    checks.append(("failure case: for a +-0.20 gap, worst-case +-0.040 per part cannot be made but RSS +-0.067 can",
                   (not L.makeable(t_wc20)) and L.makeable(t_rss20) and abs(t_rss20[0] - 0.0671) < 1e-4))

    # failure case 2 and sensitivity: process centres drifted by one sigma
    s_r = L.sigma_gap(tr)
    shift = float(np.sum(tr / 3.0))
    ana = L.fraction_out(lsl, usl, 2.0 + shift, s_r)
    gd = L.simulate_gaps(tr, n=400_000, seed=11, drift=1.0)
    simd = float(np.mean((gd < lsl) | (gd > usl)))
    checks.append((f"failure case: a 1 sigma drift of every part makes 3.1 percent fail (erf {100 * ana:.2f}%, simulation {100 * simd:.2f}%)",
                   abs(ana - 0.0308) < 5e-4 and abs(simd - ana) < 2e-3))
    checks.append(("the centred design has Cp 1.333, but after the drift Cpk drops to 0.62",
                   abs(L.cp(lsl, usl, s_r) - 4 / 3) < 1e-9 and abs(L.cpk(lsl, usl, 2.0 + shift, s_r) - 0.623) < 1e-3))
    f = [L.fraction_out(lsl, usl, 2.0 + d * shift, s_r) for d in (0, 0.5, 1.0, 1.5)]
    checks.append(("sensitivity: out-of-tolerance fraction rises with drift (0.006, 0.17, 3.1, 21 percent)",
                   all(a < b for a, b in zip(f, f[1:])) and abs(f[1] - 0.00167) < 1e-5 and abs(f[3] - 0.2106) < 1e-3))
    # numbers used in the text and the mini-project
    checks.append(("allocation rounds to 0.150, 0.077, 0.104, 0.061, 0.088 mm", list(np.round(tr, 3)) == [0.150, 0.077, 0.104, 0.061, 0.088]))
    checks.append(("equal allocation is +-0.101 mm per part at cost 51.68", abs(t_eq[0] - 0.1006) < 1e-4 and abs(L.cost(t_eq) - 51.68) < 5e-3))
    checks.append(("sigma of the allocated gap is 0.075 mm", abs(s_r - 0.075) < 1e-9))
    checks.append(("app challenge: t = 0.09, drift 0.5 sigma gives Cpk about 1.12",
                   abs(L.cpk(lsl, usl, 2.0 + 0.5 * 5 * 0.09 / 3, math.sqrt(5) * 0.09 / 3) - 1.118) < 2e-3))
    checks.append(("a part toleranced +-0.10 costs half as much as +-0.05 with the same k (cost model)",
                   abs(L.cost(np.full(5, 0.05)) / L.cost(np.full(5, 0.10)) - 2.0) < 1e-9))
    checks.append(("worked example: limits are 4.02 sigma away and about 1 assembly in 17500 is out",
                   abs(0.3 / sg - 4.025) < 5e-3 and abs(1 / L.fraction_out(lsl, usl, 2.0, sg) - 17500) < 100))
    checks.append(("simulated drift fraction rounds to 0.0306 and the worst-case equal design costs 68 percent more",
                   abs(simd - 0.0306) < 5e-5 and abs(L.cost(np.full(5, 0.06)) / L.cost(t_eq) - 1.677) < 2e-3))
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
