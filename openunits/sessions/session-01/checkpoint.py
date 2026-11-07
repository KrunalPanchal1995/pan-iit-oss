"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: 72 km/h is 20 m/s",
                   abs(L.convert(72, "km/h", "m/s", L.SPEED) - 20.0) < 1e-9))
    checks.append(("worked example: 60 mph is 96.56 km/h (96.6 to 3 figures)",
                   abs(L.convert(60, "mph", "km/h", L.SPEED) - 96.56064) < 1e-4
                   and abs(L.round_sig(L.convert(60, "mph", "km/h", L.SPEED), 3) - 96.6) < 1e-9))
    checks.append(("hand calculation: 5 km is 5000 m", abs(L.with_prefix(5, "k") - 5000.0) < 1e-9))
    checks.append(("1 mile is 1.609344 km exactly", abs(L.convert(1, "mi", "km", L.LENGTH) - 1.609344) < 1e-12))
    checks.append(("there and back again restores the number",
                   abs(L.convert(L.convert(37.5, "ft", "m", L.LENGTH), "m", "ft", L.LENGTH) - 37.5) < 1e-9))
    checks.append(("micro is 10^-6: 250 u is 0.00025", abs(L.with_prefix(250, "u") - 0.00025) < 1e-15))
    num, sym = L.best_prefix(0.0042)
    checks.append(("best prefix of 0.0042 is 4.2 m(illi)", abs(num - 4.2) < 1e-9 and sym == "m"))
    checks.append(("edge: zero converts to zero", L.convert(0.0, "mph", "knot", L.SPEED) == 0.0))
    checks.append(("round_sig(0.012345, 3) is 0.0123", abs(L.round_sig(0.012345, 3) - 0.0123) < 1e-12))
    checks.append(("the bare number 60 is five different speeds",
                   len({round(60 * v, 6) for v in L.SPEED.values()}) == 5))
    try:
        L.convert(1.0, "furlong", "m", L.LENGTH)
        unknown_ok = False
    except KeyError:
        unknown_ok = True
    checks.append(("an unknown unit raises an error instead of guessing", unknown_ok))
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
