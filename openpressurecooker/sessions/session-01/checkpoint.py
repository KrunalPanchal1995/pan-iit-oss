"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("open pot (101.325 kPa absolute) boils at 100 C", abs(L.boiling_point(101.325) - 100.0) < 1e-9))
    checks.append(("table value: 200 kPa boils at 120.2 C", abs(L.boiling_point(200.0) - 120.2) < 1e-9))
    t0, t1, t2 = (L.boiling_point(p) for p in (80.0, 150.0, 250.0))
    checks.append(("higher pressure always gives a higher boiling point", t0 < t1 < t2))
    checks.append(("gauge 0 is one atmosphere absolute", abs(L.gauge_to_abs(0.0) - 101.325) < 1e-12))
    checks.append(("speed factor is 1 at 100 C and 2 at 110 C", abs(L.speed_factor(100.0) - 1.0) < 1e-12 and abs(L.speed_factor(110.0) - 2.0) < 1e-12))
    t = L.boiling_point(L.gauge_to_abs(100.0))
    time = L.cooking_time(40.0, 100.0)
    checks.append((f"worked example: 100 kPa gauge boils at {t:.1f} C (about 120.4) and 40 min becomes {time:.1f} min (about 9.7)",
                   abs(t - 120.42) < 0.05 and abs(time - 9.7) < 0.1))
    checks.append(("open pot keeps the 40 minute time", abs(L.cooking_time(40.0, 0.0) - 40.0) < 1e-9))
    # hand calculation: 20 C hotter means two doublings, so a quarter of the time
    checks.append(("hand calculation: 20 C hotter means four times faster", abs(L.speed_factor(120.0) - 4.0) < 1e-12))
    try:
        L.boiling_point(10.0)
        edge = False
    except ValueError:
        edge = True
    checks.append(("a pressure outside the table raises ValueError", edge))
    checks.append(("table end points are accepted (50 and 400 kPa)", abs(L.boiling_point(400.0) - 143.6) < 1e-9 and abs(L.boiling_point(50.0) - 81.3) < 1e-9))
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
