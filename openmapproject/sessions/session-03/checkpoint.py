"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    rad = np.radians

    # finite-difference Jacobian against formulas, away from the central meridian too
    ok = True
    for name in ("equirectangular", "Mercator", "Lambert cylindrical"):
        for lat in (0.0, 20.0, 45.0, 70.0):
            d = L.distortion(L.PROJECTIONS[name], rad(lat), 0.7)
            h, k, a = L.analytic_scales(name, rad(lat))
            ok &= abs(d["s_max"] - max(h, k)) < 1e-5 * max(h, k) and abs(d["s_min"] - min(h, k)) < 1e-5 and abs(d["area"] - a) < 1e-5 * a
    checks.append(("numerical scale factors match the formulas (equirectangular, Mercator, Lambert)", bool(ok)))
    ok = all(abs(L.distortion(L.sinusoidal, rad(lat), rad(lon))["area"] - 1.0) < 1e-6
             for lat in (-70, -20, 0, 35, 75) for lon in (-150, -40, 0, 90, 170))
    checks.append(("sinusoidal map has area scale 1 everywhere", ok))
    ok = all(abs(L.distortion(L.mercator, rad(lat), 0.3)["omega"]) < 1e-3 for lat in (10, 40, 70))
    checks.append(("Mercator keeps angles (omega = 0)", ok))

    # worked example: Lambert cylindrical equal-area at 60 degrees north
    d = L.distortion(L.lambert_cyl, rad(60.0), 0.0)
    checks.append((f"worked example: Lambert cylindrical at 60 N has stretch {d['s_max']:.3f} and {d['s_min']:.3f}, area {d['area']:.3f}, omega {d['omega']:.2f} deg",
                   abs(d["s_max"] - 2.0) < 1e-5 and abs(d["s_min"] - 0.5) < 1e-5 and abs(d["area"] - 1.0) < 1e-5
                   and abs(d["omega"] - 2 * np.degrees(np.arcsin(0.6))) < 1e-3 and abs(d["omega"] - 73.74) < 0.01))

    # hand calculation: equirectangular at 60 N is (2, 1), omega = 2 asin(1/3) = 38.94 deg
    d = L.distortion(L.equirectangular, rad(60.0), 0.0)
    checks.append(("equirectangular at 60 N: stretches 2 and 1, omega 38.94 degrees",
                   abs(d["s_max"] - 2) < 1e-5 and abs(d["s_min"] - 1) < 1e-5 and abs(d["omega"] - 38.94) < 0.01))

    # area of the sphere
    checks.append(("Lambert cylindrical map area is 4 pi", abs(L.map_area(L.lambert_cyl) - 4 * np.pi) / (4 * np.pi) < 3e-3))
    checks.append(("sinusoidal map area is 4 pi", abs(L.map_area(L.sinusoidal) - 4 * np.pi) / (4 * np.pi) < 3e-3))
    checks.append(("Mercator inflates the area of the sphere (above 4.5 times)", L.map_area(L.mercator) > 4.5 * 4 * np.pi))
    checks.append(("equirectangular map area exceeds 4 pi", L.map_area(L.equirectangular) > 4 * np.pi * 1.4))

    # shortest path versus straight line on Mercator
    route = (51.5, -0.1, 40.7, -74.0)
    gc, rh = L.great_circle_distance(*route) * 6371, L.rhumb_distance(*route) * 6371
    checks.append((f"great circle ({gc:.0f} km) is shorter than the Mercator straight line ({rh:.0f} km)", gc < rh and abs(gc - 5573) < 2 and abs(rh - 5797) < 2))
    checks.append(("along the equator both routes have the same length", abs(L.great_circle_distance(0, 0, 0, 60) - L.rhumb_distance(0, 0, 0, 60)) < 1e-9))
    glat, glon = L.great_circle_points(*route)
    checks.append(("the great circle starts and ends on the cities and bulges poleward",
                   abs(glat[0] - 51.5) < 1e-6 and abs(glat[-1] - 40.7) < 1e-6 and glat.max() > 51.5))
    checks.append(("a quarter of the equator is pi/2 long", abs(L.great_circle_distance(0, 0, 0, 90) - np.pi / 2) < 1e-12))

    # failure case: the poles
    a80 = L.distortion(L.mercator, rad(80.0), 0.0)["area"]
    a89 = L.distortion(L.mercator, rad(89.9), 0.0)["area"]
    checks.append((f"failure case: Mercator area scale grows from {a80:.1f} at 80 N to {a89:.0f} at 89.9 N", abs(a80 - 33.2) < 0.1 and a89 > 3e5))
    try:
        L.jacobian_fd(L.mercator, rad(90.0), 0.0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("the Jacobian refuses to run at the pole", bad))

    # mini-project helpers
    rep = L.region_report(8, 37, 68, 97)
    checks.append(("region 8-37 N, 68-97 E: spreads are 1.24, 1.54, 1.00, 1.00",
                   abs(rep["equirectangular"][1] - 1.24) < 0.01 and abs(rep["Mercator"][1] - 1.54) < 0.01
                   and abs(rep["sinusoidal"][1] - 1.0) < 1e-6 and abs(rep["Lambert cylindrical"][1] - 1.0) < 1e-6))
    checks.append(("equal-area need picks the sinusoidal map (8.7 degrees) for that region",
                   L.choose_projection(rep, max_spread=1.05)[0] == "sinusoidal" and abs(rep["sinusoidal"][0] - 8.71) < 0.02))
    checks.append(("an angle need (omega below 1 degree) picks Mercator", L.choose_projection(rep, max_omega=1.0) == ["Mercator"]))
    checks.append(("impossible limits give an empty answer", L.choose_projection(rep, max_spread=1.05, max_omega=1.0) == []))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
