"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    p, q, r = L.find_exponents(["length", "acceleration", "mass"], "time")
    checks.append(("worked example: pendulum period goes as L^0.5 g^-0.5 m^0",
                   np.allclose([p, q, r], [0.5, -0.5, 0.0], atol=1e-9)))
    checks.append(("worked example: a 1.000 m pendulum swings in 2.006 s",
                   abs(L.pendulum_period(1.0) - 2.006) < 5e-4))
    ok_terms = L.check_sum("length", [[("speed", 1), ("time", 1)], [("acceleration", 1), ("time", 2)]])
    checks.append(("s = u t + a t^2 is dimensionally consistent", all(ok_terms)))
    bad_terms = L.check_sum("length", [[("speed", 1), ("time", 1)], [("acceleration", 1), ("time", 1)]])
    checks.append(("s = u t + a t is caught (second term is a speed)", bad_terms == [True, False]))
    checks.append(("impulse and momentum have the same dimension", L.same_dim("impulse", "momentum")))
    checks.append(("force times time is an impulse",
                   L.same_dim(L.expr_dim([("force", 1), ("time", 1)]), "impulse")))
    checks.append(("hand calculation: feet read as metres makes a volume 35.31 times too big",
                   abs(1 / L.scale_factor("volume", length=0.3048) - 35.3147) < 1e-3))
    re_dim = L.expr_dim([("density", 1), ("speed", 1), ("length", 1), ("viscosity", -1)])
    checks.append(("Reynolds number rho v D / mu has no dimension", bool(np.allclose(re_dim, 0.0))))
    checks.append(("worst-case error of x*y^2 with 2% and 1% errors is 4%",
                   abs(L.rel_error_worst([1, 2], [0.02, 0.01]) - 0.04) < 1e-12))
    checks.append(("independent errors (root sum of squares) are smaller: 2.83%",
                   abs(L.rel_error_rss([1, 2], [0.02, 0.01]) - 0.028284) < 1e-5))
    try:
        L.find_exponents(["length", "length", "mass"], "time")
        edge_ok = False
    except np.linalg.LinAlgError:
        edge_ok = True
    checks.append(("edge: dependent quantities cannot fix exponents (error raised)", edge_ok))
    checks.append(("no change of units, no change of value", L.scale_factor("force") == 1.0))
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
