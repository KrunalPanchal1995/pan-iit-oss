"""Checkpoint for Session 1. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append((f"worked example: at 40 degrees a 100 px sideways distance looks {100 * L.width_ratio(40):.1f} px (cos 40 = 0.766)",
                   abs(100 * L.width_ratio(40) - 76.6) < 0.05))
    checks.append(("a camera looking straight on does not squeeze anything", abs(L.width_ratio(0) - 1.0) < 1e-12))
    checks.append(("edge: a camera at 90 degrees sees the sheet edge-on (squeeze 0)", abs(L.width_ratio(90)) < 1e-12))
    pa, pb = L.view_of_sheet(L.LANDMARKS, L.CAM_A), L.view_of_sheet(L.LANDMARKS, L.CAM_B)
    checks.append(("camera A shows the 10 x 6 sheet as 400 x 240 pixels",
                   abs(pa[1, 0] - pa[0, 0] - 400) < 1e-9 and abs(pa[3, 1] - pa[0, 1] - 240) < 1e-9))
    checks.append(("camera B shows it 459.6 pixels wide and 360 tall",
                   abs(pb[1, 0] - pb[0, 0] - 459.6) < 0.05 and abs(pb[3, 1] - pb[0, 1] - 360) < 1e-9))
    sx, sy = L.stretch_between(pa, pb)
    checks.append((f"the stretch from B onto A is {sx:.3f} sideways and {sy:.3f} up-down (hand calculation 40/(60 cos 40) and 40/60)",
                   abs(sx - 40 / (60 * math.cos(math.radians(40)))) < 1e-9 and abs(sy - 40 / 60) < 1e-9 and abs(sx - 0.870) < 0.001 and abs(sy - 0.667) < 0.001))
    checks.append(("one resize factor cannot fix it: the two stretches differ", abs(sx - sy) > 0.1))
    checks.append(("the grid has 11 x 7 = 77 crossings", len(L.grid_points()) == 77))
    checks.append(("the aspect ratios are 4:3 and 16:9", abs(L.aspect_ratio(L.CAM_A) - 4 / 3) < 1e-12 and abs(L.aspect_ratio(L.CAM_B) - 16 / 9) < 1e-12))
    checks.append(("30 fps over 0.2 s gives 7 picture times, 24 fps gives 5", len(L.frame_times(30, 0.2)) == 7 and len(L.frame_times(24, 0.2)) == 5))
    checks.append(("worked example: 30 fps and 24 fps agree every 1/6 s", abs(L.coincide_period(30, 24) - 1 / 6) < 1e-12))
    ta, tb = L.frame_times(30, 1.0), L.frame_times(24, 1.0)
    both = [t for t in ta if np.min(np.abs(tb - t)) < 1e-9]
    checks.append(("counting by hand over 1 s: exactly 6 shared instants (0, 1/6 ... 5/6) plus 1.0", len(both) == 7 and abs(both[1] - 1 / 6) < 1e-9))
    gap = L.worst_gap(30, 24)
    checks.append((f"worked example: the worst timing gap is 1/60 s = 16.7 ms (got {gap * 1000:.2f} ms)", abs(gap - 1 / 60) < 1e-9))
    checks.append(("a sample at 120 px/s moves 2.0 px in that gap", abs(L.position_error(120, gap) - 2.0) < 1e-6))
    checks.append(("edge: equal frame rates started together never disagree", L.worst_gap(30, 30) < 1e-12))
    checks.append(("a faster B camera shrinks the gap: 48 fps gives 8.33 ms", abs(L.worst_gap(30, 48) - 1 / 120) < 1e-9))
    checks.append(("a camera at 60 degrees squeezes sideways distances to half: 100 px look 50 px", abs(100 * L.width_ratio(60) - 50.0) < 1e-9))
    checks.append(("a sample at 90 px/s moves 1.5 px in the 1/60 s gap", abs(L.position_error(90, 1 / 60) - 1.5) < 1e-9))
    gaps = [round(L.gap_to_b(k / 30, 24) * 1000, 2) for k in range(5)]
    checks.append((f"the gaps at the five A pictures of one 1/6 s cycle are 0, 8.33, 16.67, 16.67, 8.33 ms (got {gaps})", gaps == [0.0, 8.33, 16.67, 16.67, 8.33]))
    ts = np.linspace(0, 0.2, 4001)
    peak = max(L.gap_to_b(t, 24) for t in ts)
    checks.append((f"the nearest-picture distance never exceeds half a B period: 1/48 s = 20.8 ms (got {peak * 1000:.2f})", abs(peak - 1 / 48) < 1e-4))
    ok_fps = [f for f in (24, 25, 30, 48, 50, 60) if L.worst_gap(30, f) <= 0.010 + 1e-12]
    checks.append((f"design: for a gap of at most 10 ms the B rates 30, 48, 50 and 60 work (got {ok_fps})", ok_fps == [30, 48, 50, 60]))
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
