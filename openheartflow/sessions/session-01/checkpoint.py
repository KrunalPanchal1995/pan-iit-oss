"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: 93 mmHg through 18.6 mmHg per L/min gives 5.0 L/min",
                   abs(L.flow(93.0, 18.6) - 5.0) < 1e-9))
    checks.append(("total resistance is 18.6 when nothing is narrowed", abs(L.total_resistance(1.0) - 18.6) < 1e-9))
    checks.append(("worked example: narrowing x1.5 gives total resistance 26.04", abs(L.total_resistance(1.5) - 26.04) < 1e-9))
    q15 = L.flow(93.0, L.total_resistance(1.5))
    checks.append(("worked example: same pump, narrowing x1.5 gives 3.57 L/min", abs(q15 - 3.571) < 1e-3))
    checks.append(("restoring 5 L/min at narrowing x1.5 needs 130.2 mmHg", abs(L.push_needed(5.0, 1.5) - 130.2) < 1e-6))
    prof = L.pressure_profile(93.0)
    checks.append(("the pressure ends at 0 back at the heart", abs(prof[-1]) < 1e-9))
    checks.append(("the pressure never rises along the loop", bool(np.all(np.diff(prof) <= 1e-12))))
    checks.append(("the small vessels lose 74.4 mmHg of the 93", abs((prof[1] - prof[2]) - 74.4) < 1e-9))
    p15 = L.pressure_profile(93.0, 1.5)
    share = (p15[1] - p15[2]) / 93.0
    checks.append(("narrowing x1.5 makes the small vessels take 85.7% of the pressure loss", abs(share - 1.2 / 1.4) < 1e-9))
    checks.append(("doubling the push doubles the flow", abs(L.flow(186.0, 18.6) - 2 * L.flow(93.0, 18.6)) < 1e-9))
    checks.append(("flow is 0 with no push", L.flow(0.0, 18.6) == 0.0))
    try:
        L.flow(93.0, 0.0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("zero resistance is rejected instead of dividing by zero", bad))

    # --- numbers used in the text
    checks.append(("worked example: the segments are 1.86, 14.88 and 1.86 and the small vessels lose 5.0 x 14.88 = 74.4",
                   np.allclose(L.segment_resistances(), [1.86, 14.88, 1.86]) and abs(5.0 * 14.88 - 74.4) < 1e-9))
    checks.append(("worked example: narrowed small vessels have 22.32", abs(L.segment_resistances(1.5)[1] - 22.32) < 1e-9))
    checks.append(("profile at 93 mmHg is 93, 83.7, 9.3, 0", np.allclose(prof, [93.0, 83.7, 9.3, 0.0], atol=1e-9)))
    checks.append(("doubling the small-vessel resistance cuts the flow to 2.78 L/min", abs(L.flow(93.0, L.total_resistance(2.0)) - 2.778) < 1e-3))
    checks.append(("60 mmHg through 18.6 gives 3.23 L/min", abs(L.flow(60.0, 18.6) - 3.2258) < 1e-3))
    checks.append(("narrowing x1.5: the small vessels lose 79.7 mmHg", abs((p15[1] - p15[2]) - 79.714) < 1e-3))
    ok_d = (abs(120.0 / 4.5 - 26.667) < 1e-3 and abs((26.667 / 18.6 - 0.2) / 0.8 - 1.5421) < 1e-3
            and L.flow(120.0, L.total_resistance(1.54)) >= 4.5 > L.flow(120.0, L.total_resistance(1.55))
            and abs(L.flow(120.0, L.total_resistance(1.54)) - 4.505) < 1e-3 and abs(L.flow(120.0, L.total_resistance(1.55)) - 4.480) < 1e-3)
    checks.append(("design: with 120 mmHg and a flow of at least 4.5 L/min the narrowing can reach 1.54 but not 1.55", bool(ok_d)))
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
