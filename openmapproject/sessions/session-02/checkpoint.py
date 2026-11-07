"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R = L.R_EARTH
    p = L.sphere_xyz(0.0, 0.0)
    checks.append(("the point (lat 0, lon 0) is (R, 0, 0) on the sphere", np.allclose(p, [R, 0, 0])))
    p = L.sphere_xyz(90.0, 0.0)
    checks.append(("the north pole is (0, 0, R)", np.allclose(p, [0, 0, R], atol=1e-9)))
    pts = L.sphere_xyz(np.array([10.0, -40.0, 75.0]), np.array([20.0, 130.0, -60.0]))
    checks.append(("every point is at distance R from the centre", np.allclose(np.linalg.norm(pts, axis=-1), R)))

    # worked example: Mercator at latitude 60, longitude 30
    x, y = L.mercator(60.0, 30.0)
    checks.append((f"worked example: Mercator (60, 30) gives x = {float(x):.1f} km, y = {float(y):.1f} km, area scale 4",
                   abs(float(x) - 3335.8) < 0.1 and abs(float(y) - 8390.3) < 0.1
                   and abs(L.mercator_area_scale(60.0) - 4.0) < 1e-9))
    lat, lon = L.mercator_inverse(x, y)
    checks.append(("the inverse returns latitude 60 and longitude 30", abs(float(lat) - 60) < 1e-9 and abs(float(lon) - 30) < 1e-9))
    xe, ye = L.mercator(0.0, 0.0)
    checks.append(("the equator maps to y = 0 with scale 1", abs(float(ye)) < 1e-9 and abs(L.mercator_scale(0.0) - 1) < 1e-12))

    # numerical check of the scale factor sec(lat) against a small step north
    h = 1e-4
    _, y1 = L.mercator(45.0, 0.0)
    _, y2 = L.mercator(45.0 + h, 0.0)
    num = float(y2 - y1) / (R * np.radians(h))
    checks.append(("a small northward step is enlarged by sec(45 deg) = 1.4142", abs(num - np.sqrt(2)) < 1e-4))

    # areas: whole sphere in lat/lon boxes and the Greenland/Africa boxes
    total = L.box_area_sphere(-90, 90, -180, 180)
    checks.append(("the box covering the whole sphere has area 4 pi R^2", abs(total - 4 * np.pi * R ** 2) < 1.0))
    rep, tr, ar = L.box_ratio_report()
    checks.append((f"true Africa/Greenland box ratio is 10.36, the Mercator map shows {ar:.2f} (about equal)",
                   abs(tr - 10.36) < 0.01 and abs(ar - 1.02) < 0.01))

    # design: latitude limits
    checks.append(("area exaggeration 2 holds up to 45 degrees", abs(L.max_lat_for_exaggeration(2.0) - 45.0) < 1e-9))
    checks.append(("area exaggeration 4 holds up to 60 degrees", abs(L.max_lat_for_exaggeration(4.0) - 60.0) < 1e-9))
    checks.append(("k = 1 gives latitude 0", L.max_lat_for_exaggeration(1.0) == 0.0))

    # edge cases: poles and bad input
    _, ypole = L.mercator(90.0, 0.0)
    checks.append(("the pole maps to infinity", bool(np.isinf(ypole)) and float(ypole) > 0))
    try:
        L.max_lat_for_exaggeration(0.5)
        bad = False
    except ValueError:
        bad = True
    checks.append(("k below 1 is rejected", bad))
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
