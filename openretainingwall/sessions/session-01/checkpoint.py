"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: H = 4 m gives a push of 0.5 * (1/3) * 18 * 16 = 48 kN/m",
                   abs(L.soil_push(4.0) - 48.0) < 1e-9))
    checks.append(("the push acts at H/3 = 1.333 m above the base", abs(L.push_height(4.0) - 4.0 / 3.0) < 1e-12))
    checks.append(("wall weight for B = 2 m, H = 4 m is 24 * 2 * 4 = 192 kN/m", abs(L.wall_weight(2.0, 4.0) - 192.0) < 1e-9))
    checks.append(("worked example: sliding ratio 2.00 and tipping ratio 3.00 for B = 2, H = 4",
                   abs(L.slide_ratio(2.0, 4.0) - 2.0) < 1e-9 and abs(L.tip_ratio(2.0, 4.0) - 3.0) < 1e-9))
    checks.append(("doubling the height quadruples the push (192 kN/m at 8 m)",
                   abs(L.soil_push(8.0) / L.soil_push(4.0) - 4.0) < 1e-12 and abs(L.soil_push(8.0) - 192.0) < 1e-9))
    checks.append(("hand calculation: H = 3 m, B = 1.2 m gives sliding 1.6 and tipping 1.92",
                   abs(L.slide_ratio(1.2, 3.0) - 1.6) < 1e-9 and abs(L.tip_ratio(1.2, 3.0) - 1.92) < 1e-9))
    # closed forms for B = 2: slide = 4B/H, tip = 12 B^2 / H^2
    h_slide = 4.0 * 2.0
    h_tip = np.sqrt(12.0 * 4.0)
    checks.append(("for B = 2 m the sliding ratio is 1 at H = 8 m and the tipping ratio is 1 at H = 6.93 m",
                   abs(L.slide_ratio(2.0, h_slide) - 1.0) < 1e-9 and abs(L.tip_ratio(2.0, h_tip) - 1.0) < 1e-9
                   and abs(h_tip - 6.928) < 1e-3))
    checks.append(("design: H = 3 m needs B = 1.25 m for sliding 1.5 and tipping 2 (1.20 m is not enough)",
                   L.slide_ratio(1.25, 3.0) >= 1.5 and L.tip_ratio(1.25, 3.0) >= 2.0 and L.tip_ratio(1.2, 3.0) < 2.0))
    checks.append(("challenge: H = 5 m with B = 2.25 m meets 1.5 and 2, but B = 2.0 m tips (1.92)",
                   L.slide_ratio(2.25, 5.0) >= 1.5 and L.tip_ratio(2.25, 5.0) >= 2.0
                   and abs(L.tip_ratio(2.0, 5.0) - 1.92) < 1e-9))
    checks.append(("1.25 m instead of 1.20 m is about 4 percent more width", abs(1.25 / 1.20 - 1.0 - 0.0417) < 1e-3))
    checks.append(("edge: zero height gives zero push", L.soil_push(0.0) == 0.0))
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
