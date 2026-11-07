"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("declination: +23.45 at the June solstice (day 172), -23.45 in December (day 355), 0 at day 81",
                   abs(L.declination(172) - 23.45) < 0.01 and abs(L.declination(355) + 23.45) < 0.01 and abs(L.declination(81)) < 0.01))
    alt, az = L.sun_position(13.08, 81, 12.0)
    checks.append(("equinox noon in Chennai: altitude = 90 - latitude = 76.92, sun due south", abs(alt - 76.92) < 0.01 and abs(az - 180) < 0.01))
    alt, az = L.sun_position(13.08, 172, 12.0)
    checks.append(("June noon in Chennai: altitude 90 - (23.45 - 13.08), sun due NORTH", abs(alt - (90 - 23.45 + 13.08)) < 0.02 and abs(az) < 0.01))
    alt9, az9 = L.sun_position(13.08, 105, 9.0)
    alt15, az15 = L.sun_position(13.08, 105, 15.0)
    checks.append(("symmetry: 9:00 and 15:00 have the same altitude, mirror azimuths",
                   abs(alt9 - alt15) < 1e-9 and abs((az9 + az15) - 360.0) < 1e-9))
    d = np.radians(L.declination(105))
    sin_a = np.sin(np.radians(13.08)) * np.sin(d) + np.cos(np.radians(13.08)) * np.cos(d) * np.cos(np.radians(45))
    checks.append(("worked example: 15 April 15:00 altitude 45.8 degrees (hand formula)", abs(alt15 - np.degrees(np.arcsin(sin_a))) < 1e-9 and abs(alt15 - 45.77) < 0.01))
    om = L.profile_angle(alt15, az15, L.WALL_AZ["west"])
    checks.append(("sun facing the west wall: profile angle = altitude", abs(om - alt15) < 0.01))
    dep = L.depth_for_full_shade(0.3, 1.5, alt15, az15, L.WALL_AZ["west"])
    checks.append(("worked example: full shade needs D = (0.3 + 1.5) / tan(45.8) = 1.75 m", abs(dep - 1.8 / np.tan(np.radians(om))) < 1e-9 and abs(dep - 1.75) < 0.01))
    checks.append(("an overhang of exactly that depth shades the whole window",
                   abs(L.overhang_shaded_fraction(dep, 0.3, 1.5, alt15, az15, L.WALL_AZ["west"]) - 1.0) < 1e-9))
    f06 = L.overhang_shaded_fraction(0.6, 0.3, 1.5, alt15, az15, L.WALL_AZ["west"])
    checks.append(("worked example: a 0.6 m overhang shades (0.6 x 1.028 - 0.3) / 1.5 = 0.21", abs(f06 - 0.211) < 0.002))
    checks.append(("no overhang, no shade; sun behind the wall counts as fully shaded",
                   L.overhang_shaded_fraction(0.0, 0.3, 1.5, alt15, az15, 270.0) == 0.0
                   and L.overhang_shaded_fraction(0.0, 0.3, 1.5, alt15, az15, 90.0) == 1.0))
    checks.append(("deeper overhang never lets in more sun",
                   all(L.window_irradiance(alt15, az15, 270.0, a) >= L.window_irradiance(alt15, az15, 270.0, b) - 1e-9
                       for a, b in ((0, 0.3), (0.3, 0.6), (0.6, 1.2)))))
    checks.append(("effective area: two 0.5 m2 openings in series act like 0.354 m2", abs(L.effective_area(0.5, 0.5) - 0.5 / np.sqrt(2)) < 1e-12))
    checks.append(("effective area is never more than the smaller opening", L.effective_area(0.2, 5.0) < 0.2))
    q = L.cross_vent_flow(0.5, 0.5, 1.5)
    checks.append(("worked example: Q = 0.6 x 0.354 x 1.5 x sqrt(0.8) = 0.285 m3/s = 21.3 ACH in 48 m3",
                   abs(q - 0.6 * 0.5 / np.sqrt(2) * 1.5 * np.sqrt(0.8)) < 1e-12 and abs(L.ach_from_flow(q, 48) - 21.34) < 0.01))
    checks.append(("doubling the wind doubles the flow", abs(L.cross_vent_flow(0.5, 0.5, 3.0) - 2 * q) < 1e-12))
    qs = L.stack_flow(0.5, 0.5, 2.0, 32.0, 28.0)
    checks.append(("stack flow: 0.6 x 0.354 x sqrt(2 x 9.81 x 2 x 4 / 303.15) = 0.153 m3/s", abs(qs - 0.6 * 0.5 / np.sqrt(2) * np.sqrt(2 * 9.81 * 2 * 4 / 303.15)) < 1e-12))
    checks.append(("stack flow is zero with no temperature difference, and grows as sqrt(h)",
                   L.stack_flow(0.5, 0.5, 2.0, 30, 30) == 0.0 and abs(L.stack_flow(0.5, 0.5, 8.0, 32, 28) - 2 * qs) < 1e-12))
    checks.append(("wind and stack combine in quadrature: 3 and 4 give 5", abs(L.combined_flow(3.0, 4.0) - 5.0) < 1e-12))
    bad = 0
    for call in (lambda: L.declination(0), lambda: L.effective_area(0, 1), lambda: L.overhang_shaded_fraction(0.5, 0.3, 0, 40, 270, 270),
                 lambda: L.depth_for_full_shade(0.3, 1.5, alt15, az15, 90.0), lambda: L.ach_from_flow(1, 0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 5))
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
