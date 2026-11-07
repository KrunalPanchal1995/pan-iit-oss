"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    DELHI = 28.6
    alt, az = L.sun_position(DELHI, L.declination(355), 12.0)
    alt, az = float(alt), float(az)
    vsa = float(L.vertical_shadow_angle(alt, az, 180.0))
    checks.append(("worked example: south wall at noon, VSA equals the sun altitude 37.95 degrees", abs(vsa - 37.95) < 0.01))
    lit = float(L.sunlit_fraction(alt, az, 180.0, 0.5, 1.5, 0.3))
    hand_lit = 1.0 - (0.5 * np.tan(np.radians(37.95)) - 0.3) / 1.5
    checks.append(("worked example: sunlit share 0.94 (hand: 1 - (0.5 tan 37.95 - 0.3) / 1.5)", abs(lit - hand_lit) < 1e-3 and abs(lit - 0.940) < 1e-3))
    checks.append(("worked example: clear-sky DNI 824 W/m2 at 37.95 degrees (Meinel)", abs(float(L.dni(alt)) - 824.0) < 1.0))
    q = float(L.window_gain(DELHI, 355, 12.0, 180.0, 2.0, 1.5, 0.5, 0.3))
    q_hand = 0.6 * 3.0 * (824.0 * np.cos(np.radians(37.95)) * hand_lit + 0.05 * 824.0)
    checks.append(("worked example: solar heat gain about 1174 W through the 3 m2 window", abs(q - 1174.0) < 3.0 and abs(q - q_hand) < 3.0))
    a6, z6 = L.sun_position(DELHI, L.declination(172), 12.0)
    checks.append(("same overhang fully shades the window at June noon (only diffuse, about 85 W)",
                   float(L.sunlit_fraction(a6, z6, 180.0, 0.5, 1.5, 0.3)) == 0.0
                   and abs(float(L.window_gain(DELHI, 172, 12.0, 180.0, 2.0, 1.5, 0.5, 0.3)) - 85.2) < 1.0))
    checks.append(("design: 0.98 m overhang fully shades a 1.5 m window (gap 0.3) at a VSA of 61.4 degrees",
                   abs(float(L.overhang_for_full_shade(61.4, 1.5, 0.3)) - 0.981) < 0.002))
    checks.append(("sun straight in front at altitude 0: cos(incidence) = 1 (edge case)",
                   abs(float(np.cos(np.radians(0.0)) * np.cos(np.radians(L.wall_solar_azimuth(180.0, 180.0)))) - 1.0) < 1e-12))
    checks.append(("sun behind the wall gives no beam", float(L.cos_incidence(30.0, 0.0, 180.0)) == 0.0))
    checks.append(("no overhang: the whole window is sunlit when the sun is in front", float(L.sunlit_fraction(40.0, 200.0, 180.0, 0.0, 1.5)) == 1.0))
    checks.append(("a deeper overhang never lets more sun in",
                   all(float(L.sunlit_fraction(50, 220, 180, d2, 1.5, 0.3)) <= float(L.sunlit_fraction(50, 220, 180, d1, 1.5, 0.3)) + 1e-12
                       for d1, d2 in ((0.0, 0.2), (0.2, 0.5), (0.5, 1.0)))))
    checks.append(("VSA grows as the sun moves round to the side of the wall (oblique sun)",
                   float(L.vertical_shadow_angle(40, 240, 180)) > float(L.vertical_shadow_angle(40, 180, 180))))
    checks.append(("DNI is below the solar constant and falls as the sun gets lower",
                   float(L.dni(90)) < 1353 and float(L.dni(20)) < float(L.dni(60)) and float(L.dni(-5)) == 0.0))
    e = L.daily_gain(DELHI, 172, 90.0, 2.0, 1.5)
    w = L.daily_gain(DELHI, 172, 270.0, 2.0, 1.5)
    checks.append(("symmetry: east and west windows gain the same heat over a day (solar time)", abs(e - w) < 1e-6 * max(e, 1)))
    checks.append(("Delhi, winter: the south window gains the most; summer: the south window gains less than east or west",
                   L.daily_gain(DELHI, 355, 180, 2, 1.5) > L.daily_gain(DELHI, 355, 90, 2, 1.5)
                   and L.daily_gain(DELHI, 172, 180, 2, 1.5) < L.daily_gain(DELHI, 172, 90, 2, 1.5)))
    checks.append(("a smaller time step gives the same daily total (convergence within 0.5%)",
                   abs(L.daily_gain(DELHI, 172, 90, 2, 1.5, step=0.02) - e) < 0.005 * e))
    try:
        L.sunlit_fraction(40, 180, 180, 0.5, 0.0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("a window of zero height raises ValueError", bad))
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
