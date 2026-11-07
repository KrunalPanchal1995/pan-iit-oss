"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("tolerance of 9.93 to 9.98 is 0.05", abs(L.tolerance(9.93, 9.98) - 0.05) < 1e-9))
    checks.append(("a part exactly on a limit is in tolerance", L.in_limits(9.98, 9.93, 9.98) and L.in_limits(9.93, 9.93, 9.98)))
    checks.append(("9.99 mm is out of tolerance for the pin (9.93 to 9.98)", not L.in_limits(9.99, 9.93, 9.98)))
    try:
        L.tolerance(10.0, 9.9)
        bad = False
    except ValueError:
        bad = True
    checks.append(("edge: upper below lower is rejected", bad))

    lo, hi = L.pin_limits(0.05)
    checks.append(("pin limits for tol 0.05 are 9.93 and 9.98", abs(lo - 9.93) < 1e-9 and abs(hi - 9.98) < 1e-9))
    lo, hi = L.hole_limits(0.05)
    checks.append(("hole limits for tol 0.05 are 10.00 and 10.05", abs(lo - 10.0) < 1e-9 and abs(hi - 10.05) < 1e-9))

    cmin, cmax = L.clearance_range(0.05)
    checks.append((f"worked example: clearance range is 0.02 to 0.12 mm (got {cmin:.2f} to {cmax:.2f})",
                   abs(cmin - 0.02) < 1e-9 and abs(cmax - 0.12) < 1e-9))
    checks.append(("hand calculation: tol 0.10 gives a maximum clearance of 0.22", abs(L.clearance_range(0.10)[1] - 0.22) < 1e-9))
    checks.append(("edge: tol 0 gives one clearance, 0.02 mm", L.clearance_range(0.0) == (0.02, 0.02)))
    checks.append(("clearance 0.03 is a clearance fit", L.kind_of_fit(0.03) == "clearance"))
    checks.append(("clearance -0.01 is interference", L.kind_of_fit(L.clearance(10.0, 10.01)) == "interference"))
    checks.append(("clearance 0 is line to line", L.kind_of_fit(0.0) == "line to line"))
    checks.append(("every pair assembles for these limits", L.always_assembles(0.05) and L.always_assembles(0.2)))
    # the spread of clearance is 2 * tol: loosening the tolerance widens it
    tols = (0.02, 0.05, 0.10)
    w = [L.clearance_range(t)[1] - L.clearance_range(t)[0] for t in tols]
    checks.append(("spread of clearance equals 2 x tolerance", all(abs(a - 2 * t) < 1e-9 for a, t in zip(w, tols))))
    # a pin of 9.99 mm is out of spec, yet it would still fit a 10.00 mm hole: tolerance is about the spec
    checks.append(("a 9.99 pin still fits a 10.00 hole (0.01 mm clearance) but is rejected by the drawing",
                   abs(L.clearance(10.0, 9.99) - 0.01) < 1e-9 and not L.in_limits(9.99, *L.pin_limits(0.05))))
    # numbers used in the assessment questions
    checks.append(("tol 0.04 gives clearance 0.02 to 0.10; tol 0.02 gives 0.02 to 0.06",
                   L.clearance_range(0.04) == (0.02, 0.10) and L.clearance_range(0.02) == (0.02, 0.06)))
    checks.append(("a 9.95 pin in a 10.04 hole has 0.09 mm clearance, and both are in tolerance for tol 0.05",
                   abs(L.clearance(10.04, 9.95) - 0.09) < 1e-9 and L.in_limits(9.95, *L.pin_limits(0.05)) and L.in_limits(10.04, *L.hole_limits(0.05))))
    checks.append(("tol 0.10 gives a minimum clearance of 0.02 mm and tol 0.01 a maximum of 0.04", L.clearance_range(0.10)[0] == 0.02 and L.clearance_range(0.01)[1] == 0.04))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
