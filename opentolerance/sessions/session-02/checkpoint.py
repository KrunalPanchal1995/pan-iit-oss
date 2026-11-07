"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hole H7 zone is 0 to +21 um", L.hole_zone("H", 7) == (0.0, 21.0)))
    ei, es = L.shaft_zone("g", 6)
    checks.append(("shaft g6 zone is -20 to -7 um", (ei, es) == (-20.0, -7.0)))
    checks.append(("shaft zone width equals the IT6 grade, 13 um", abs((es - ei) - 13.0) < 1e-9))
    checks.append(("js6 is symmetric, +-6.5 um", L.shaft_zone("js", 6) == (-6.5, 6.5)))
    checks.append(("p6 zone is +22 to +35 um", L.shaft_zone("p", 6) == (22.0, 35.0)))

    lo, hi, kind = L.fit("g", 6)
    checks.append((f"worked example: 25 H7/g6 clearance is 7 to 41 um, a clearance fit (got {lo:g} to {hi:g}, {kind})",
                   lo == 7.0 and hi == 41.0 and kind == "clearance"))
    hmm = L.to_mm(25, L.hole_zone("H", 7))
    smm = L.to_mm(25, L.shaft_zone("g", 6))
    checks.append(("limits in mm: hole 25.000 to 25.021, shaft 24.980 to 24.993",
                   hmm == (25.0, 25.021) and smm == (24.98, 24.993)))
    # hand calculation: the spread of the fit equals the sum of the two tolerances, 21 + 13 = 34 um
    checks.append(("hand calculation: max - min clearance = IT7 + IT6 = 34 um", abs((hi - lo) - 34.0) < 1e-9))
    # the same numbers recomputed from mm limits
    mn = round((hmm[0] - smm[1]) * 1000, 6)
    mx = round((hmm[1] - smm[0]) * 1000, 6)
    checks.append(("clearance recomputed from the mm limits is 7 and 41 um", mn == 7.0 and mx == 41.0))

    lo, hi, kind = L.fit("h", 6)
    checks.append(("H7/h6 is a clearance fit from 0 to 34 um (zero minimum still counts as clearance)", (lo, hi, kind) == (0.0, 34.0, "clearance")))
    lo, hi, kind = L.fit("js", 6)
    checks.append(("H7/js6 is a transition fit, -6.5 to +27.5 um", (lo, hi, kind) == (-6.5, 27.5, "transition")))
    lo, hi, kind = L.fit("p", 6)
    checks.append(("H7/p6 is an interference fit, max clearance -1 and min clearance -35 um", (lo, hi, kind) == (-35.0, -1.0, "interference")))
    try:
        L.hole_zone("G", 7)
        bad = False
    except ValueError:
        bad = True
    checks.append(("edge: only the hole H is accepted in the hole-basis system", bad))

    checks.append(("design: only H7/g6 suits the sliding bearing (5 to 45 um)", L.choose_fits(5, 45) == ["H7/g6"]))
    checks.append(("design: only H7/p6 suits the light press (interference, at most 40 um)", L.choose_fits(-40, -0.0001) == ["H7/p6"]))
    checks.append(("design edge: an impossible requirement returns no fit", L.choose_fits(100, 120) == []))

    signs = np.array([1, -1, -1, -1])
    nominals = np.array([40.0, 10.0, 12.0, 15.0])
    tols = np.array([0.10, 0.05, 0.05, 0.08])
    nom, lo, hi = L.worst_case_stack(signs, nominals, tols)
    checks.append((f"worked example: stack gap 3.00 mm, worst case 2.72 to 3.28 (got {nom:.2f}, {lo:.2f} to {hi:.2f})",
                   abs(nom - 3.0) < 1e-9 and abs(lo - 2.72) < 1e-9 and abs(hi - 3.28) < 1e-9))
    clo, chi = L.corner_stack(signs, nominals, tols)
    checks.append(("exhaustive corners (16 combinations) agree with the sum of tolerances", abs(clo - lo) < 1e-9 and abs(chi - hi) < 1e-9))
    rng = np.random.default_rng(1)
    ok = True
    for _ in range(20):
        n = int(rng.integers(2, 7))
        s = rng.choice([-1, 1], n)
        x = rng.uniform(5, 50, n)
        t = rng.uniform(0.01, 0.2, n)
        a = L.worst_case_stack(s, x, t)
        b = L.corner_stack(s, x, t)
        ok &= abs(a[1] - b[0]) < 1e-9 and abs(a[2] - b[1]) < 1e-9
    checks.append(("20 random stacks: sum of tolerances equals the corner enumeration", bool(ok)))
    checks.append(("edge: zero tolerances give a single gap", L.worst_case_stack(signs, nominals, np.zeros(4)) == (3.0, 3.0, 3.0)))
    try:
        L.worst_case_stack(signs, nominals, [-0.1, 0, 0, 0])
        bad = False
    except ValueError:
        bad = True
    checks.append(("edge: a negative tolerance is rejected", bad))
    # numbers used in the text and assessment
    checks.append(("stack tolerances add to 0.28 mm, so the gap window is 0.56 mm wide", abs(tols.sum() - 0.28) < 1e-9 and abs((hi - lo) - 0.56) < 1e-9))
    w = L.worst_case_stack(signs, nominals, np.full(4, 0.025))
    checks.append(("four parts of +-0.025 mm keep the worst-case gap at 2.90 mm or more (and 3.10 or less)",
                   abs(w[1] - 2.90) < 1e-9 and abs(w[2] - 3.10) < 1e-9))
    checks.append(("a hole-basis shaft p6 starts 1 um above the top of the H7 hole", L.shaft_zone("p", 6)[0] - L.hole_zone("H", 7)[1] == 1.0))
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
