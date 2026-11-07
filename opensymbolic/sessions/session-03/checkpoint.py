"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # enumeration
    x = L.LAWS["quadratic"][1]
    t5, s5, v5 = L.enumerate_pool(x, 5)
    t7, s7, v7 = L.enumerate_pool(x, 7)
    checks.append(("enumeration: 518 distinct formulas up to 5 nodes and 11777 up to 7 nodes (quadratic x grid)",
                   len(t5) == 518 and len(t7) == 11777))
    checks.append(("every tree in the pool has the size it is filed under",
                   all(L.count_nodes(t) == s for t, s in zip(t7[::50], s7[::50]))))
    checks.append(("no two formulas in the pool give the same numbers",
                   len(np.unique(np.round(v7, 9), axis=0)) == len(t7)))
    # constant fitting by hand
    a, b, m = L.fit_all(np.array([[0.0, 1.0, 2.0]]), np.array([1.0, 3.0, 5.0]))
    checks.append(("hand calculation: data (1, 3, 5) on f = (0, 1, 2) gives a = 2, b = 1, error 0",
                   abs(a[0] - 2) < 1e-12 and abs(b[0] - 1) < 1e-12 and m[0] < 1e-20))
    a, b, m = L.fit_all(np.ones((1, 4)), np.array([1.0, 2.0, 3.0, 4.0]))
    checks.append(("edge: a formula that does not change with x gets infinite error", np.isinf(m[0])))
    # noise-free recovery
    for name in L.LAWS:
        law, xx = L.LAWS[name]
        tr, sz, vv = L.pool_for(name)
        res = L.search(tr, sz, vv, law(xx))
        xw = np.linspace(xx.min() * 0.5, xx.max() * 1.5, 200)
        checks.append((f"worked example: noise-free {name} law is recovered exactly ({L.to_str(res['tree'])})",
                       L.recovered(res["tree"], law, xw)))
    law, xx = L.LAWS["quadratic"]
    tr, sz, vv = L.pool_for("quadratic")
    r0 = L.search(tr, sz, vv, law(xx))
    checks.append(("worked example: noise-free y = 3 x^2 gives sq(x) with a = 3.000 and b = 0.000",
                   L.to_str(r0["tree"]) == "sq(x)" and abs(r0["a"] - 3.0) < 1e-9 and abs(r0["b"]) < 1e-9))
    checks.append(("noise-free quadratic: the Pareto front is x then sq(x)",
                   [L.to_str(tr[i]) for i in r0["front"]] == ["x", "sq(x)"]))
    checks.append(("the saturating law's formula x / (x + 1) has 5 nodes",
                   L.count_nodes(("div", ("x",), ("add", ("x",), ("1",)))) == 5))
    # roadmap numbers: what the shipped search cannot do
    xm = np.linspace(0.2, 5.0, 30)
    mm = lambda v: 5 * v / (1 + 0.37 * v)
    trm, szm, vm = L.cached_pool(xm, 7)
    xwm = np.linspace(0.1, 7, 200)
    mm_rate = np.mean([L.recovered(L.search(trm, szm, vm, L.noisy(mm(xm), 0.05, np.random.default_rng(1000 + s)))["tree"], mm, xwm) for s in range(40)])
    checks.append(("roadmap: the shipped search recovers y = 5x/(1 + 0.37x) in 0 percent of 40 trials at 5% noise", mm_rate == 0.0))
    law_q, xq = L.LAWS["quadratic"]
    trq, szq, vq = L.pool_for("quadratic")
    xwq = np.linspace(0.25, 7.5, 200)
    het = np.mean([L.recovered(L.search(trq, szq, vq, law_q(xq) + np.where(np.arange(30) % 2 == 0, 0.02, 0.5) * np.std(law_q(xq)) * np.random.default_rng(1000 + s).standard_normal(30))["tree"], law_q, xwq) for s in range(40)])
    checks.append(("roadmap: with half the points at 2% noise and half at 50%, the unweighted search recovers the law in 80 percent of 40 trials", het == 0.8))
    law10 = ("add", ("div", ("sqrt", ("x",)), ("add", ("1",), ("sq", ("x",)))), ("log", ("x",)))
    t9, s9, v9 = L.enumerate_pool(xq, 9)
    checks.append(("roadmap: the target law has 10 nodes; the enumeration holds 296966 formulas at 9 nodes, about 5 times the 58808 at 8",
                   L.count_nodes(law10) == 10 and len(t9) == 296966 and 4.9 < len(t9) / int(np.sum(s9 <= 8)) < 5.2))
    # one concrete noisy search
    law, xx = L.LAWS["quadratic"]
    tr, sz, vv = L.pool_for("quadratic")
    res = L.search(tr, sz, vv, L.noisy(law(xx), 0.02, np.random.default_rng(1)))
    checks.append(("quadratic at 2% noise: chosen sq(x) with a = 2.99 (true 3) and a 2-point front",
                   L.to_str(res["tree"]) == "sq(x)" and round(res["a"], 2) == 2.99 and len(res["front"]) == 2))
    law, xx = L.LAWS["pendulum"]
    tr, sz, vv = L.pool_for("pendulum")
    res = L.search(tr, sz, vv, L.noisy(law(xx), 0.02, np.random.default_rng(1)))
    checks.append(("pendulum at 2% noise: chosen sqrt(x) with a = 2.00 (true 2 pi / sqrt(9.81) = 2.006)",
                   L.to_str(res["tree"]) == "sqrt(x)" and round(res["a"], 2) == 2.00 and abs(2 * np.pi / np.sqrt(9.81) - 2.006) < 5e-4))
    law, xx = L.LAWS["arrhenius"]
    tr, sz, vv = L.pool_for("arrhenius")
    Es = []
    for s in range(40):
        r = L.search(tr, sz, vv, L.noisy(law(xx), 0.02, np.random.default_rng(s)))
        Es.append(-1000.0 * r["a"] if r["tree"] == ("x",) else np.nan)
    Es = np.array(Es)
    checks.append(("Arrhenius at 2% noise: E recovered in all 40 trials, mean 19977 K, worst error 0.75% (true 20000 K)",
                   not np.isnan(Es).any() and round(float(Es.mean())) == 19977 and round(float(np.max(np.abs(Es - 20000)) / 200.0), 2) == 0.75))
    # success rates
    rates = {n: (L.recovery_rate(n, 0.0, range(40)), L.recovery_rate(n, 0.05, range(40)), L.recovery_rate(n, 0.2, range(40)))
             for n in L.LAWS}
    checks.append(("success with no noise is 100% for all four laws (40 trials each)",
                   all(r[0] == 1.0 for r in rates.values())))
    checks.append(("success at 5% noise (40 trials): quadratic 97.5%, pendulum 97.5%, Arrhenius 97.5%, saturating 87.5%",
                   [rates[n][1] for n in ("quadratic", "pendulum", "arrhenius", "saturating")] == [0.975, 0.975, 0.975, 0.875]))
    checks.append(("success at 20% noise: quadratic 87.5%, pendulum 92.5%, Arrhenius 97.5%, saturating 0%",
                   [rates[n][2] for n in ("quadratic", "pendulum", "arrhenius", "saturating")] == [0.875, 0.925, 0.975, 0.0]))
    # failures
    trials = [L.overfit_trial(s) for s in range(30)]
    wins = sum(o["penalised"][0] < o["min_train"][0] for o in trials)
    med_min = float(np.median([o["min_train"][0] for o in trials]))
    med_pen = float(np.median([o["penalised"][0] for o in trials]))
    checks.append(("overfitting: the penalised choice has lower held-out error in 23 of 30 trials",
                   wins == 23))
    checks.append(("overfitting: median held-out MSE is 5.73 for lowest-training-error versus 0.78 for the penalised choice",
                   round(med_min, 2) == 5.73 and round(med_pen, 2) == 0.78))
    checks.append(("the lowest-training-error formulas are big (6 or 7 nodes in the first trials)",
                   all(o["min_train"][1] >= 6 for o in trials[:6])))
    sf = L.sine_failure()
    checks.append(("missing law: sin(3x) gives a relative error of 0.92 against 0.02 noise, so the search warns us",
                   round(sf["rel_rmse"], 2) == 0.92 and sf["noise"] == 0.02 and sf["rel_rmse"] > 10 * sf["noise"]))
    # units
    Lh, g, m, T = L.confounded_pendulum_data()
    fits = L.power_law_fits(Lh, g, m, T)
    best = min(f[1] for f in fits)
    ties = [f for f in fits if f[1] <= 1.5 * best]
    ok_units = [f for f in fits if L.units_ok(*f[0])]
    checks.append(("units filter: 729 exponent triples, 9 tie for the best fit, only 1 has the units of a time",
                   len(fits) == 729 and len(ties) == 9 and len(ok_units) == 1))
    checks.append(("the survivor is L^0.5 g^-0.5 m^0 with C = 6.17, within 2% of 2 pi = 6.283",
                   ok_units[0][0] == (0.5, -0.5, 0.0) and round(ok_units[0][2], 2) == 6.17 and abs(ok_units[0][2] / (2 * np.pi) - 1) < 0.02))
    checks.append(("units_ok: sqrt(L/g) is a time, but L*g is not",
                   L.units_ok(0.5, -0.5, 0.0) and not L.units_ok(1.0, 1.0, 0.0)))
    # mini-project
    kin = {n: float(np.mean([L.kinetics_trial(n, s)[0] for s in range(20)])) for n in range(4, 13)}
    first = min(n for n, r in kin.items() if r >= 0.9)
    checks.append(("mini-project: rate-order recovery is 55% with 4 points, 80% with 7, 100% with 11; smallest n with at least 90% is 11",
                   kin[4] == 0.55 and kin[7] == 0.8 and kin[11] == 1.0 and first == 11))
    # app mirror
    ids = [L.MINI[L.mini_front(nz / 100, lam)[2]][0] for nz in range(10, 21) for lam in np.arange(0.2, 0.61, 0.05)]
    checks.append(("app: for noise 10 to 20 percent and penalty 0.2 to 0.6 the mini search picks sq(x)",
                   all(i == "sq(x)" for i in ids)))
    checks.append(("app: at noise 10 percent and penalty 0.05 it wrongly picks exp(x / 4)",
                   L.MINI[L.mini_front(0.10, 0.05)[2]][0] == "exp(x / 4)"))
    checks.append(("app: node counts of the 8 mini formulas match the table",
                   [s for _, s in L.MINI] == [1, 2, 2, 2, 4, 4, 3, 4]))
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
