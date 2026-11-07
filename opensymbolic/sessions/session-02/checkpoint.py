"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    t = ("add", ("mul", ("x",), ("x",)), ("c", 1.0))
    checks.append(("worked example: x*x + 1 has 5 nodes and equals 10 at x = 3",
                   L.complexity(t) == 5 and abs(float(L.evaluate(t, [3.0])[0]) - 10.0) < 1e-12))
    checks.append(("show() prints the tree as text", L.show(t) == "((x * x) + 1)"))
    checks.append(("edge: sqrt of a negative number is nan, not a crash",
                   bool(np.isnan(L.evaluate(("sqrt", ("x",)), [-4.0])[0]))))
    checks.append(("sq, exp, log and div evaluate correctly",
                   np.allclose(L.evaluate(("div", ("sq", ("x",)), ("log", ("c", float(np.e)))), [3.0]), [9.0])))
    t4 = ("sub", ("sq", ("x",)), ("c", 2.0))
    checks.append(("hand calculation: x^2 - 2 has 4 nodes and equals 7 at x = 3",
                   L.complexity(t4) == 4 and abs(float(L.evaluate(t4, [3.0])[0]) - 7.0) < 1e-12))
    tr = L.fit_candidates(L.A_AU[L.TRAIN], L.T_YR[L.TRAIN])
    rows = L.report(L.A_AU[L.TRAIN], L.T_YR[L.TRAIN], L.A_AU[L.TEST], L.T_YR[L.TEST])
    checks.append(("candidates A, B, C have 3, 8 and 13 nodes", [r[1] for r in rows] == [3, 8, 13]))
    checks.append(("train MSE: A = 0.0296, B below 1e-7, C below 1e-20 (C passes through all 4 points)",
                   round(rows[0][2], 4) == 0.0296 and rows[1][2] < 1e-7 and rows[2][2] < 1e-20))
    checks.append(("held-out MSE: A = 198.2, B below 1e-4, C = 645.0 years squared",
                   round(rows[0][3], 1) == 198.2 and rows[1][3] < 1e-4 and round(rows[2][3], 1) == 645.0))
    checks.append(("the fitted B constant is 1.000 to 3 digits (Kepler: T = a^1.5)",
                   abs(tr["B"][1][1] - 1.0) < 1e-3))
    pred = L.evaluate(tr["B"], L.A_AU)
    checks.append(("worked example: B predicts Mars at 1.881 years and Saturn at 29.45 years",
                   round(float(pred[3]), 3) == 1.881 and round(float(pred[5]), 2) == 29.45))
    t1 = L.cand_b(1.0)
    checks.append(("worked example: with c = 1, B gives a^3 = 3.540 and T = 1.8814 years for Mars (a = 1.524 AU)",
                   round(1.524 ** 3, 3) == 3.540 and round(float(L.evaluate(t1, [1.524])[0]), 4) == 1.8814))
    checks.append(("B with the fitted constant predicts Jupiter at 11.867 years (observed 11.862)",
                   round(float(pred[4]), 3) == 11.867 and L.T_YR[4] == 11.862))
    rows5 = L.report(L.A_AU[:5], L.T_YR[:5], L.A_AU[5:], L.T_YR[5:])
    checks.append(("training on 5 planets still leaves C failing on Saturn (held-out MSE 43.4) while B stays below 1e-3",
                   round(rows5[2][3], 1) == 43.4 and rows5[1][3] < 1e-3))
    rows_all = L.report(L.A_AU, L.T_YR, L.A_AU, L.T_YR)
    pts = [(r[1], r[2]) for r in rows_all]
    checks.append(("on all six planets the Pareto front is A and B; C is larger and worse than B",
                   L.pareto_indices(pts) == [0, 1] and round(rows_all[0][2], 2) == 4.38 and rows_all[1][2] < rows_all[2][2]))
    ok_design = [r[0] for r in rows if r[3] < 0.01]
    checks.append(("design rule: held-out MSE below 0.01 selects only B", ok_design == ["B"]))
    checks.append(("exact law T = a^1.5 has MSE about 1.0e-5 on the rounded textbook data",
                   round(float(np.mean((L.A_AU ** 1.5 - L.T_YR) ** 2)) * 1e5, 1) == 1.0))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
