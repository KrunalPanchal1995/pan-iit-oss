"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("1 microsecond is 299.79 m of range", abs(L.time_error_to_range_error(1e-6) - 299.792458) < 1e-6))
    checks.append(("range_from_time and clock_accuracy_for are inverses", abs(L.clock_accuracy_for(L.range_from_time(2.5e-3)) - 2.5e-3) < 1e-15))
    dt10 = L.clock_accuracy_for(10.0)
    checks.append((f"design: 10 m needs a clock better than 33.4 ns (got {dt10 * 1e9:.2f} ns)", abs(dt10 * 1e9 - 33.36) < 0.01))
    stab = dt10 / 86400.0
    checks.append((f"design: holding 33.4 ns for a day is 3.9e-13 steadiness (got {stab:.2e})", abs(stab - 3.86e-13) < 0.02e-13))

    # worked example: three ground beacons (km -> m), travel times in microseconds, linear solve
    beacons = np.array([[0.0, 40.0], [120.0, 40.0], [60.0, 95.0]]) * 1e3
    me = np.array([45.0, 25.0]) * 1e3
    t = np.linalg.norm(beacons - me, axis=1) / L.C
    checks.append(("worked example: travel times are 158.2, 255.1 and 238.8 microseconds",
                   np.allclose(t * 1e6, [158.22, 255.12, 238.80], atol=0.01)))
    ranges = L.range_from_time(t)
    A, b = L.linear_system(beacons, ranges)
    checks.append(("worked example: first subtracted equation is 240 x = 10800 (km units)",
                   abs(A[0, 0] / 1e3 - 240.0) < 1e-6 and abs(A[0, 1]) < 1e-9 and abs(b[0] / 1e6 - 10800.0) < 1e-3))
    fix = L.linear_fix(beacons, ranges)
    checks.append(("worked example: the linear solve gives (45, 25) km", np.allclose(fix, me, atol=1e-3)))

    # 3D with toy satellites
    rec = L.receiver_on_earth(19.0, 73.0)
    sats = L.toy_sats(rec, [(20, 60), (110, 35), (200, 50), (290, 25)])
    checks.append(("toy satellites are at the orbit radius", np.allclose(np.linalg.norm(sats, axis=1), L.R_ORBIT)))
    r = np.linalg.norm(sats - rec, axis=1)
    checks.append(("four exact ranges recover the 3D position to 1 mm", np.linalg.norm(L.linear_fix(sats, r) - rec) < 1e-3))
    pts = L.three_sphere_points(sats[:3], r[:3])
    radii = sorted(np.linalg.norm(pts, axis=1) / 1e3)
    checks.append(("three spheres give two points: one on the Earth, one far out in space",
                   len(pts) == 2 and abs(radii[0] - 6371.0) < 0.01 and radii[1] > 30000.0))
    # a 1 microsecond error on one range moves the fix by hundreds of metres
    rb = r.copy()
    rb[0] += L.time_error_to_range_error(1e-6)
    e = np.linalg.norm(L.linear_fix(sats, rb) - rec)
    checks.append((f"1 microsecond on one range moves the fix by more than 300 m (got {e:.0f} m)", e > 299.0))
    # a receiver clock error on all ranges is large and not zero
    e2 = np.linalg.norm(L.linear_fix(sats, r + L.range_from_time(1e-3)) - rec)
    checks.append(("a 1 ms receiver clock error ruins the fix (tens of km)", e2 > 10e3))
    # edge case: collinear beacons cannot fix a 2D position
    line = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]])
    A2, _ = L.linear_system(line, np.array([1.0, 1.0, 1.0]))
    checks.append(("collinear beacons give a rank-deficient system", np.linalg.matrix_rank(A2) < 2))
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
