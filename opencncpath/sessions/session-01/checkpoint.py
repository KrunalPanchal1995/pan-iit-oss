"""Checkpoint for Session 1. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("a closed square outline of side 20 mm has length 80 mm",
                   abs(L.polyline_length(L.square_outline(20)) - 80.0) < 1e-9))
    path = L.centre_path(20, 2.0)
    checks.append(("worked example: 20 mm pocket, 4 mm cutter: centre path is the square 2..18 mm",
                   np.allclose(path[:4], [[2, 2], [18, 2], [18, 18], [2, 18]])))
    checks.append(("worked example: centre path length is 64 mm", abs(L.polyline_length(path) - 64.0) < 1e-9))
    checks.append(("worked example: at 120 mm/min one lap takes 32.0 s", abs(L.lap_time_s(20, 2.0, 120) - 32.0) < 1e-9))
    checks.append(("worked example: the island left after one lap is 12 mm wide", abs(L.island_side(20, 2.0) - 12.0) < 1e-9))
    checks.append(("every centre-path corner is exactly one radius from the walls",
                   all(min(x, 20 - x, y, 20 - y) == 2.0 for x, y in path[:4])))
    checks.append(("the island centre (10, 10) is NOT touched by the 4 mm cutter",
                   not L.is_cut((10, 10), path, 2.0)))
    checks.append(("a point 1.5 mm from the wall IS cut", L.is_cut((1.5, 10), path, 2.0)))
    big = L.centre_path(20, 5.0)
    checks.append(("edge: a 10 mm cutter in a 20 mm pocket has island 0 and cuts the centre",
                   L.island_side(20, 5.0) == 0.0 and L.is_cut((10, 10), big, 5.0)))
    checks.append(("edge: the 10 mm cutter lap is 40 mm long and takes 12.0 s at 200 mm/min",
                   abs(L.polyline_length(big) - 40.0) < 1e-9 and abs(L.lap_time_s(20, 5.0, 200) - 12.0) < 1e-9))
    checks.append(("edge: a 24 mm cutter does not fit a 20 mm pocket (no path)", L.centre_path(20, 12.0) is None))
    checks.append(("half the feed doubles the time", abs(L.lap_time_s(20, 2.0, 60) - 2 * L.lap_time_s(20, 2.0, 120)) < 1e-9))
    checks.append(("a bigger cutter makes a shorter lap (30 mm pocket: 4 mm 104 mm, 8 mm 88 mm)",
                   abs(L.polyline_length(L.centre_path(30, 2.0)) - 104.0) < 1e-9
                   and abs(L.polyline_length(L.centre_path(30, 4.0)) - 88.0) < 1e-9))
    checks.append(("exercise/assessment: 30 mm pocket, 6 mm cutter, 150 mm/min: path 96 mm, 38.4 s, island 18 mm",
                   abs(L.polyline_length(L.centre_path(30, 3.0)) - 96.0) < 1e-9 and abs(L.lap_time_s(30, 3.0, 150) - 38.4) < 1e-9
                   and abs(L.island_side(30, 3.0) - 18.0) < 1e-9))
    checks.append(("design question: the 40 mm lap takes exactly 20.0 s at 120 mm/min and 64 s for the 64 mm lap at 60 mm/min",
                   abs(L.lap_time_s(20, 5.0, 120) - 20.0) < 1e-9 and abs(L.lap_time_s(20, 2.0, 60) - 64.0) < 1e-9))
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
