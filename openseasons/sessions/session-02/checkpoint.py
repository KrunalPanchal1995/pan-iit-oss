"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d0 = L.days_since_j2000(2026, 1, 1)
    days = d0 + np.arange(365)
    lam = L.sun_longitude(days)
    dec = np.array([L.declination_from_vectors(x) for x in lam])
    checks.append(("on 1 January 2000 the Sun's ecliptic longitude is about 280.4 degrees",
                   abs(float(L.sun_longitude(0.0)) - 280.4) < 0.1))
    checks.append(("declination peaks at 23.44 degrees on day 172 (21 June), the June solstice",
                   abs(dec.max() - 23.44) < 0.01 and int(np.argmax(dec)) + 1 == 172))
    checks.append(("declination reaches -23.44 degrees near day 355 (21 December)",
                   abs(dec.min() + 23.44) < 0.01 and 354 <= int(np.argmin(dec)) + 1 <= 356))
    ok = all(abs(L.declination_from_vectors(x) - np.degrees(np.arcsin(np.sin(np.radians(23.44)) * np.sin(np.radians(x))))) < 1e-9
             for x in (0, 17, 90, 133, 200, 270, 345))
    checks.append(("the dot product s . a equals sin(tilt) sin(longitude): the subsolar latitude is the declination", ok))
    old = np.array([L.declination_formula(n) for n in range(1, 366)])
    checks.append(("the vector declination and the simple formula of opendaylight agree within 1.2 degrees all year",
                   np.abs(dec - old).max() < 1.2))
    checks.append(("on 20 March 2026 the Sun is within 0.5 degrees of the equator (equinox)", abs(dec[78]) < 0.5))
    checks.append(("at the equinox every latitude has 12 hours of day (equal day and night)",
                   all(abs(L.day_length_hours(lat, 0.0) - 12.0) < 1e-9 and abs(L.day_length_by_vectors(lat, 0.0) - 12.0) < 0.01
                       for lat in (-60, -20, 0, 35, 70))))
    checks.append(("worked example: at 40 N on the June solstice the day is 14.84 h and the noon Sun is 73.44 degrees high",
                   abs(L.day_length_hours(40, 23.44) - 14.84) < 0.01 and abs(L.noon_height(40, 23.44) - 73.44) < 0.01))
    checks.append(("the sunrise equation and the brute-force vector count agree on day length (within 0.01 h)",
                   all(abs(L.day_length_hours(lat, dd) - L.day_length_by_vectors(lat, dd)) < 0.01
                       for lat in (-50, 0, 40, 66) for dd in (-23.44, -10, 0, 12, 23.44))))
    checks.append(("the noon height 90 - |lat - d| equals the maximum from the dot product",
                   all(abs(L.noon_height(lat, dd) - L.noon_height_by_vectors(lat, dd)) < 0.01
                       for lat in (0, 40, 60) for dd in (-23.44, 0, 15))))
    checks.append(("polar day: 67 N has 24 h at the June solstice, 66 N has 22.25 h; 67 S has 0 h",
                   L.day_length_hours(67, 23.44) == 24.0 and abs(L.day_length_hours(66, 23.44) - 22.25) < 0.01
                   and L.day_length_hours(-67, 23.44) == 0.0))
    checks.append(("the polar limit is 90 - 23.44 = 66.56 degrees",
                   L.day_length_hours(66.5, 23.44) < 24.0 and L.day_length_hours(66.6, 23.44) == 24.0))
    checks.append(("edge: the poles do not crash and give 12 h at the equinox, 24 h and 0 h at the solstice",
                   L.day_length_hours(90, 0.0) == 12.0 and L.day_length_hours(90, 23.44) == 24.0
                   and L.day_length_hours(-90, 23.44) == 0.0))
    r = L.sun_distance_au(days)
    checks.append(("distance runs from 147.1 to 152.1 million km, closest on day 4 (4 January)",
                   abs(r.min() * L.AU_MKM - 147.1) < 0.05 and abs(r.max() * L.AU_MKM - 152.1) < 0.05
                   and int(np.argmin(r)) + 1 == 4))
    checks.append(("inverse square: sunlight is 6.9 percent stronger at perihelion than at aphelion",
                   abs(L.irradiance_ratio(147.1, 152.1) - 1.069) < 0.001
                   and abs(L.irradiance_ratio(r.min(), r.max()) - 1.069) < 0.001))
    dj = L.days_since_j2000(2026, 1, 4, 12)
    ju = L.days_since_j2000(2026, 7, 4, 12)
    q = {}
    for tag, dd in (("jan", dj), ("jul", ju)):
        de = L.declination_from_vectors(L.sun_longitude(dd))
        for lat in (45, -45):
            q[(tag, lat)] = L.daily_insolation(lat, de, L.sun_distance_au(dd))
    checks.append(("same distance, opposite seasons: 45 N gets 126 W/m^2 on 4 Jan and 478 on 4 Jul; 45 S gets 510 and 117",
                   abs(q[("jan", 45)] - 126) < 3 and abs(q[("jul", 45)] - 478) < 3
                   and abs(q[("jan", -45)] - 510) < 3 and abs(q[("jul", -45)] - 117) < 3))
    checks.append(("distance cannot be the cause: in January (closest) the north gets less sunlight than in July (farthest)",
                   q[("jan", 45)] < q[("jul", 45)] and q[("jan", -45)] > q[("jul", -45)]))
    checks.append(("the equator-to-pole check: at the equinox the daily sunlight at the equator is S0/pi = 433 W/m^2",
                   abs(L.daily_insolation(0.0, 0.0, 1.0) - 1361.0 / np.pi) < 0.5))
    checks.append(("the spin turns 360/365.2422 = 0.9856 degrees extra per day, which takes 235.9 s (3 min 56 s, about 4 minutes)",
                   abs(360.0 / 365.2422 - 0.9856) < 1e-4 and abs(L.extra_rotation_seconds() - 235.9) < 0.1))
    sid = L.sidereal_day_seconds()
    checks.append(("the sidereal day is 86164.1 s = 23 h 56 m 4.1 s",
                   abs(sid - 86164.1) < 0.1 and int(sid // 3600) == 23 and int(sid % 3600 // 60) == 56))
    checks.append(("1/T_solar = 1/T_sidereal - 1/T_year holds (days)",
                   abs(1.0 - (1.0 / (sid / 86400.0) - 1.0 / L.TROPICAL_YEAR)) < 1e-12))
    checks.append(("the solar day is sidereal day + 235.9 s", abs((86400.0 - sid) - L.extra_rotation_seconds()) < 0.2))
    checks.append(("50 N on the June solstice: 16.15 h of day and a noon Sun of 63.44 degrees",
                   abs(L.day_length_hours(50, 23.44) - 16.15) < 0.01 and abs(L.noon_height(50, 23.44) - 63.44) < 0.01))
    checks.append(("30 solar days make the stars rise 118 minutes earlier", abs(30 * L.extra_rotation_seconds() / 60.0 - 118.0) < 0.2))
    checks.append(("45 S gets 4 times the sunlight of 45 N on 4 January, and the north's winter-to-summer change is a factor 3.8",
                   abs(q[("jan", -45)] / q[("jan", 45)] - 4.05) < 0.1 and abs(q[("jul", 45)] / q[("jan", 45)] - 3.8) < 0.1))
    checks.append(("the distance in AU runs 0.98329 to 1.01671 and the speed ratio perihelion/aphelion is 1.034",
                   abs(r.min() - 0.98329) < 0.0002 and abs(r.max() - 1.01671) < 0.0002 and abs(r.max() / r.min() - 1.034) < 0.001))
    checks.append(("sin 23.44 = 0.3978, tan 40 = 0.8391, tan 23.44 = 0.4336",
                   abs(np.sin(np.radians(23.44)) - 0.3978) < 5e-5 and abs(np.tan(np.radians(40)) - 0.8391) < 5e-5
                   and abs(np.tan(np.radians(23.44)) - 0.4336) < 5e-5))
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
