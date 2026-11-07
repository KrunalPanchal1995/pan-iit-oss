"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    rs, rm = L.sky_radii()
    checks.append(("Sun looks 0.533 degrees wide and the Moon 0.518 degrees wide (both about 0.5)",
                   abs(2 * rs - 0.533) < 0.001 and abs(2 * rm - 0.518) < 0.001))
    checks.append(("diameter ratio Sun/Moon is about 400.7 and distance ratio about 389.2",
                   abs(L.R_SUN / L.R_MOON - 400.7) < 0.1 and abs(L.D_SUN / L.D_MOON - 389.2) < 0.1))
    checks.append(("hand calculation: Sun angular radius is about r/d = 0.00465 rad = 0.2666 degrees",
                   abs(696000 / 1.496e8 - 0.00465) < 1e-5 and abs(rs - 0.2666) < 5e-4))
    checks.append(("the Moon's angular radius runs from 0.245 (apogee 406700 km) to 0.279 degrees (perigee 356500 km)",
                   abs(L.sky_radii(406700.0)[1] - 0.245) < 0.001 and abs(L.sky_radii(356500.0)[1] - 0.279) < 0.001))

    checks.append(("mean Moon: rm = 0.259, rs + rm = 0.525 and rs - rm = 0.008 degrees; at 400000 km rm = 0.2488",
                   abs(rm - 0.259) < 0.0005 and abs(rs + rm - 0.525) < 0.0006 and abs(rs - rm - 0.008) < 0.0006
                   and abs(L.sky_radii(400000.0)[1] - 0.2488) < 0.0005))
    checks.append(("worked example: mean Moon, centres 0.30 degrees apart: partial, about 31 percent covered",
                   L.classify_sky(0.30, rs, rm) == "partial" and abs(L.covered_fraction(0.30, rs, rm) - 0.306) < 0.002))
    a, b = L.sky_radii(360000.0)
    checks.append(("Moon at 360000 km, centres aligned: total, 100 percent covered, Moon bigger by 0.0099 degrees",
                   L.classify_sky(0.0, a, b) == "total" and abs(L.covered_fraction(0.0, a, b) - 1.0) < 1e-9
                   and abs((b - a) - 0.0099) < 5e-4))
    a, b = L.sky_radii(400000.0)
    checks.append(("Moon at 400000 km, aligned: annular, 87.1 percent of the Sun's area covered (b^2/a^2)",
                   L.classify_sky(0.0, a, b) == "annular" and abs(L.covered_fraction(0.0, a, b) - 0.871) < 0.002
                   and abs(L.covered_fraction(0.0, a, b) - (b / a) ** 2) < 1e-12))
    checks.append(("discs are the same size when the Moon is at 373355 km",
                   abs(L.critical_moon_distance() - 373355.0) < 50.0))
    checks.append(("the mean Moon distance 384400 km is farther than that, so a mean-distance aligned eclipse is annular",
                   L.classify_sky(0.0, *L.sky_radii(384400.0)) == "annular"))

    # edge cases
    rs0, rm0 = 0.25, 0.30
    checks.append(("edge: touching discs (sep = rs + rm) are no eclipse; sep = rm - rs is still total",
                   L.classify_sky(rs0 + rm0, rs0, rm0) == "none" and L.classify_sky(rm0 - rs0, rs0, rm0) == "total"
                   and L.covered_fraction(rs0 + rm0, rs0, rm0) == 0.0))
    fr = [L.covered_fraction(s, rs, rm) for s in np.linspace(0, 0.6, 25)]
    checks.append(("covered fraction never increases as the Moon moves away", bool(np.all(np.diff(fr) <= 1e-12))))

    checks.append(("the Moon moves at 1.023 km/s; its shadow crosses the equator ground at 0.558 km/s",
                   abs(L.moon_speed_kms() - 1.023) < 0.001 and abs(L.ground_speed_kms() - 0.558) < 0.001))
    checks.append(("a 200 km wide shadow passes a place at the equator in about 6 minutes (200 / 0.558 / 60)",
                   abs(200.0 / L.ground_speed_kms() / 60.0 - 6.0) < 0.1))
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
