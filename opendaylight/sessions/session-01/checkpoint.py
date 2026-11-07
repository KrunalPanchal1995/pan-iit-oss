"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d_dec = float(L.declination(355))
    alt = float(L.noon_altitude(28.6, d_dec))
    checks.append(("worked example: Delhi (28.6 N) noon altitude on 21 December is 37.95 degrees", abs(alt - 37.95) < 0.01))
    checks.append(("worked example: shadow of a 2 m pole is 2.56 m (hand: 2 / tan 37.95)",
                   abs(L.shadow_length(2.0, alt) - 2.0 / np.tan(np.radians(37.95))) < 0.01 and abs(L.shadow_length(2.0, alt) - 2.564) < 0.005))
    checks.append(("worked example: Delhi day length on 21 December is 10.18 h", abs(float(L.day_length(28.6, d_dec)) - 10.18) < 0.01))
    a9, z9 = L.sun_position(13.0, 0.0, 9.0)
    checks.append(("worked example: Chennai, equinox, 9:00 gives altitude 43.55 and azimuth 102.7 degrees",
                   abs(float(a9) - 43.55) < 0.01 and abs(float(z9) - 102.68) < 0.02))
    checks.append(("declination is 0 at the March equinox (n = 81) and +23.45 on 21 June (n = 172)",
                   abs(float(L.declination(81))) < 0.01 and abs(float(L.declination(172)) - 23.45) < 0.01))
    a12, z12 = L.sun_position(28.6, d_dec, 12.0)
    checks.append(("general formula at noon agrees with the noon rule and points due south",
                   abs(float(a12) - alt) < 1e-9 and abs(float(z12) - 180.0) < 1e-6))
    a_eq, z_eq = L.sun_position(0.0, 0.0, 6.0)
    checks.append(("equator at the equinox: sun rises due east at 6:00", abs(float(a_eq)) < 1e-9 and abs(float(z_eq) - 90.0) < 1e-9))
    checks.append(("equinox: day length is 12 h at every latitude",
                   all(abs(float(L.day_length(lat, 0.0)) - 12.0) < 1e-9 for lat in (0.0, 13.0, 28.6, 50.0))))
    checks.append(("summer and winter day lengths add up to 24 h (symmetry)",
                   abs(float(L.day_length(28.6, 23.45)) + float(L.day_length(28.6, -23.45)) - 24.0) < 1e-9))
    checks.append(("sun altitude is 0 at the computed sunrise", abs(float(L.sun_position(28.6, d_dec, float(L.sunrise_hour(28.6, d_dec)))[0])) < 1e-6))
    checks.append(("morning and afternoon are mirror images about noon (same altitude, azimuths add to 360)",
                   abs(float(L.sun_position(13, 10, 9.5)[0]) - float(L.sun_position(13, 10, 14.5)[0])) < 1e-9
                   and abs(float(L.sun_position(13, 10, 9.5)[1]) + float(L.sun_position(13, 10, 14.5)[1]) - 360.0) < 1e-9))
    checks.append(("polar limits: 24 h of day in the Arctic summer, 0 h in the Arctic winter",
                   abs(float(L.day_length(80, 23.45)) - 24) < 1e-9 and abs(float(L.day_length(80, -23.45))) < 1e-9))
    checks.append(("Chennai (13 N) has its noon sun overhead (Zero Shadow Day) twice a year, in April and August",
                   sum(1 for k in range(1, 366) if float(L.noon_altitude(13.0, L.declination(k))) > 89.75) >= 2
                   and 100 <= min(k for k in range(1, 366) if float(L.noon_altitude(13.0, L.declination(k))) > 89.75) <= 125))
    try:
        L.shadow_length(1.0, -5.0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("a sun below the horizon raises ValueError", bad))
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
