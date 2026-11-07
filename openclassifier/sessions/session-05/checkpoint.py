"""Checkpoint for Session 5. Prints PASS or FAIL."""
import math

import numpy as np


def _raises(f, *a, **k):
    try:
        f(*a, **k)
    except ValueError:
        return True
    return False


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    A, B = L.GROUP_A, L.GROUP_B

    # the model agrees with Session 3
    s3 = L.group_rates_analytic(1.0, 0.5)
    r = L.single_threshold_report([A, B], 1.0)
    checks.append((f"the group model agrees with Session 3 at one threshold t = 1: FPR {r['A']['fpr']:.4f} and {r['B']['fpr']:.4f}, TPR {r['A']['tpr']:.4f} and {r['B']['tpr']:.4f}; the gap is {L.fpr_gap(r):.3f} (about 0.15)",
                   abs(r["A"]["fpr"] - s3["fpr_A"]) < 1e-12 and abs(r["B"]["fpr"] - s3["fpr_B"]) < 1e-12
                   and abs(r["A"]["tpr"] - s3["tpr_A"]) < 1e-12 and abs(r["B"]["tpr"] - s3["tpr_B"]) < 1e-12 and abs(L.fpr_gap(r) - 0.15) < 0.001))
    xa, ya = L.simulate_group(500, 0.5, seed=2)
    xb, yb = L.simulate_group_g(500, B, seed=2)
    checks.append(("the new simulator draws exactly the Session 3 cases when the prevalence is 0.3", np.array_equal(xa, xb) and np.array_equal(ya, yb)))
    ok_inv = all(abs(L.phi(L.inv_phi(p)) - p) < 1e-12 for p in (0.001, 0.1, 0.5, 0.9, 0.999))
    checks.append(("inv_phi inverts phi, and refuses 0 and 1", ok_inv and _raises(L.inv_phi, 0.0) and _raises(L.inv_phi, 1.0)))

    # the roadmap test
    target = r["A"]["fpr"]
    th = L.equal_fpr_thresholds([A, B], target)
    fixed = L.per_group_report([A, B], th)
    checks.append((f"roadmap test: one threshold per group ({th['A']:.2f} and {th['B']:.2f}) leaves a false-positive-rate gap of {L.fpr_gap(fixed):.1e} (needed: at most 0.01) while both true-positive rates stay at {fixed['A']['tpr']:.3f} and {fixed['B']['tpr']:.3f} (needed: at least 0.6)",
                   L.fpr_gap(fixed) <= 0.01 and abs(L.fpr_gap(fixed)) < 1e-9 and min(v["tpr"] for v in fixed.values()) >= 0.6 and abs(th["B"] - 1.5) < 1e-9))
    e1, e2 = L.errors_per_1000(r), L.errors_per_1000(fixed)
    same = all(abs(fixed["A"][k] - fixed["B"][k]) < 1e-12 for k in ("fpr", "tpr", "ppv", "flagged", "errors"))
    checks.append((f"in the Session 3 setting the repair is free: every rate of the two groups becomes equal, and the errors of group B fall from {e1['B']:.1f} to {e2['B']:.1f} per 1000 people (group A: {e2['A']:.1f})",
                   same and e2["B"] < e1["B"] and abs(e2["A"] - e1["A"]) < 1e-9))

    # what it costs elsewhere
    sit, common = L.three_situations()
    pr = sit["different prevalence"]
    odds = lambda g, v: v["ppv"] / (1 - v["ppv"]) - g["prev"] / (1 - g["prev"]) * v["tpr"] / v["fpr"]
    checks.append((f"different prevalence: FPR and TPR agree but PPV does not ({pr['A']['ppv']:.3f} against {pr['B']['ppv']:.3f}); the odds identity PPV/(1-PPV) = prev/(1-prev) x TPR/FPR holds for both",
                   abs(pr["A"]["tpr"] - pr["B"]["tpr"]) < 1e-12 and pr["B"]["ppv"] - pr["A"]["ppv"] > 0.15
                   and abs(odds(A, pr["A"])) < 1e-12 and abs(odds(L.GROUP_B_BASE, pr["B"])) < 1e-12))
    need = L.tpr_for_equal_ppv(pr["A"]["ppv"], 0.5, target)
    checks.append((f"forcing equal PPV and equal FPR for B with prevalence 0.5 needs a TPR of {need:.3f}, below the floor of 0.6; with prevalence 0.1 it is impossible (needed TPR above 1)",
                   abs(need - 0.2963) < 0.0005 and need < 0.6 and _raises(L.tpr_for_equal_ppv, pr["A"]["ppv"], 0.1, target)
                   and abs(L.ppv_from(0.5, need, target) - pr["A"]["ppv"]) < 1e-12))
    wk = sit["weaker instrument"]
    checks.append((f"weaker instrument for B (d = 1.0): equal FPR leaves B's TPR at {wk['B']['tpr']:.3f}, below the floor 0.6, while A has {wk['A']['tpr']:.3f}",
                   abs(wk["B"]["tpr"] - 0.5) < 1e-3 and wk["B"]["tpr"] < 0.6 < wk["A"]["tpr"]))
    wf = sit["weaker, with floor"]
    extra = 1000 * (common - target)
    checks.append((f"the floor costs a higher common FPR: {common:.4f} instead of {target:.4f}, so group A gets {extra:.0f} more false alarms per 1000 negatives; both TPR are then at least 0.6 (B exactly {wf['B']['tpr']:.3f}) and the gap is {L.fpr_gap(wf):.1e}",
                   abs(common - 0.2276) < 0.0005 and abs(extra - 69.0) < 0.5 and abs(wf["B"]["tpr"] - 0.6) < 1e-9 and wf["A"]["tpr"] >= 0.6 and L.fpr_gap(wf) < 1e-9))

    # from data
    h = L.headline()
    gap1, gap2 = L.fpr_gap(h["single"]), L.fpr_gap(h["per_group"])
    tprs = [v["tpr"] for v in h["per_group"].values()]
    checks.append((f"fitted from 20000 calibration cases per group, the thresholds are {h['thresholds']['A']:.3f} and {h['thresholds']['B']:.3f} (ideal 1.0 and 1.5)",
                   abs(h["thresholds"]["A"] - 1.0) < 0.05 and abs(h["thresholds"]["B"] - 1.5) < 0.05))
    checks.append((f"on the Session 3 test data the empirical gap falls from {gap1:.3f} (one threshold) to {gap2:.3f} (one per group): at most 0.01, with both TPR at least 0.6 ({tprs[0]:.3f}, {tprs[1]:.3f})",
                   gap1 > 0.14 and gap2 <= 0.01 and min(tprs) >= 0.6))
    checks.append((f"the true gap of the fitted thresholds (from the normal curve, no test noise) is {L.fpr_gap(h['true_report']):.4f}; the error of a fitted FPR is about 0.003 at this size, so a gap of 0.01 is not guaranteed for every sample",
                   L.fpr_gap(h["true_report"]) < 0.01))

    # how many cases
    table = L.size_table()
    ok = {n: int(np.sum(g <= 0.01)) for n, (g, _) in table.items()}
    means = [g.mean() for g, _ in table.values()]
    checks.append((f"how many cases: the gap of fitted thresholds is at most 0.01 in {ok[200]} of 100 repeats with 200 cases per group, {ok[2000]} with 2000, {ok[10000]} with 10000 and {ok[20000]} with 20000; the mean gap falls steadily ({means[0]:.3f} to {means[-1]:.3f})",
                   ok[200] <= 40 and ok[2000] <= 60 and ok[10000] >= 85 and ok[20000] >= 90 and all(a > b for a, b in zip(means, means[1:]))))
    checks.append((f"with 200 cases per group even the TPR floor can fail: the smallest TPR over 100 repeats is {table[200][1].min():.3f}, below 0.6",
                   table[200][1].min() < 0.6 <= table[20000][1].min()))

    # failure cases
    cal = {"A": L.simulate_group_g(500, A, 1), "B": L.simulate_group_g(500, B, 2)}
    only_pos = {"A": (cal["A"][0][cal["A"][1] == 1], np.ones(int(cal["A"][1].sum()), dtype=int))}
    checks.append(("failure cases are refused: a target FPR of 0 or 1, a group with no negative cases, a prevalence of 0 or 1, d <= 0, and a TPR floor of 0 or 1",
                   _raises(L.fit_thresholds, cal, 0.0) and _raises(L.fit_thresholds, cal, 1.0) and _raises(L.fit_thresholds, only_pos, 0.1)
                   and _raises(L.make_group, "X", prev=0.0) and _raises(L.make_group, "X", prev=1.0) and _raises(L.make_group, "X", d=0.0)
                   and _raises(L.fpr_needed_for_tpr, A, 0.0) and _raises(L.fpr_needed_for_tpr, A, 1.0)))
    tool = L.threshold_tool(cal, cal, 0.16, single_t=1.0)
    checks.append(("the tool returns the thresholds, the per-group report and, when asked, the single-threshold report; on its own calibration data the FPR of each group is the target 0.16 to within 0.005",
                   set(tool) == {"thresholds", "per_group", "single"} and all(abs(v["fpr"] - 0.16) < 0.005 for v in tool["per_group"].values())))
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
