"""Checkpoint for Session 3. Prints PASS or FAIL."""
import datetime as dt

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    ang = [L.phase_angle_deg(x) for x in (0, 90, 180)]
    k = [L.illuminated_fraction(a) for a in (180, 90, 0)]
    checks.append(("phase angle is 180 degrees at new Moon and 0 at full Moon; k = 0, 0.5, 1 at new, quarter, full",
                   abs(ang[0] - 180) < 1e-6 and abs(ang[2]) < 0.01 and k[0] < 1e-12 and abs(k[1] - 0.5) < 1e-12 and abs(k[2] - 1) < 1e-12))
    checks.append(("at elongation 90 degrees the phase angle is 89.85 degrees: the Moon is half lit slightly before the quarter",
                   abs(ang[1] - 89.85) < 0.01))
    gap = max(abs(L.illuminated_fraction(L.phase_angle_deg(x)) - (1 - np.cos(np.radians(x))) / 2) for x in np.linspace(0, 360, 73))
    checks.append(("the real-distance geometry agrees with k = (1 - cos D) / 2 to better than 0.002", gap < 0.002))
    syn = L.synodic_from()
    hand = 1.0 / (1.0 / 27.321662 - 1.0 / 365.25636)
    checks.append(("worked example: 1/27.321662 - 1/365.25636 = 0.033864 per day, so the synodic month is 29.5306 days",
                   abs(1 / 27.321662 - 1 / 365.25636 - 0.033864) < 1e-6 and abs(syn - 29.5306) < 0.0005 and abs(hand - syn) < 1e-12))
    checks.append(("the derived month matches the accepted mean synodic month 29.530589 within 0.001 day",
                   abs(syn - 29.530589) < 0.001))
    cal = L.phase_calendar(2026)
    fulls = [w for w, n in cal if n == "full Moon"]
    news = [w for w, n in cal if n == "new Moon"]
    checks.append(("the simulation finds 13 full Moons and 12 new Moons in 2026, in order",
                   len(fulls) == 13 and len(news) == 12 and fulls == sorted(fulls)))
    gaps = np.diff([w.timestamp() for w in news]) / 86400.0
    checks.append(("successive new Moons are 29.53 days apart", np.allclose(gaps, 29.5306, atol=0.01)))
    refs = [dt.datetime(2026, 1, 3, 10, 3), dt.datetime(2026, 3, 3, 11, 38), dt.datetime(2026, 5, 31, 8, 45),
            dt.datetime(2026, 8, 28, 4, 18)]
    errs = []
    for ref in refs:
        errs.append(min(abs((w - ref).total_seconds()) for w in fulls) / 86400.0)
    checks.append(("mean-motion full Moons fall within 0.3 day of the almanac on 3 Jan, 3 Mar, 31 May and 28 Aug (error from mean motion)",
                   max(errs) < 0.3))
    checks.append(("the mean-motion error is far below the 14 hours worst case (0.58 day)", max(errs) < 0.58))
    rises = L.moonrise_times(0.0, 10)
    delays = (np.diff(rises) - 24.0) * 60.0
    exact = (24.0 * syn / (syn - 1.0) - 24.0) * 60.0
    checks.append(("moonrise comes 50.5 minutes later each day in the simulation",
                   len(delays) >= 8 and np.allclose(delays, 50.5, atol=0.15)))
    checks.append(("hand derivation: delay = 24 h x 29.5306 / 28.5306 - 24 h = 50.47 minutes, equal to the simulation",
                   abs(exact - 50.47) < 0.01 and abs(delays.mean() - exact) < 0.1))
    checks.append(("a new Moon (elongation 0) rises at 6.21 h, a little after sunrise at 6 h; 12.19/(15-0.508) = 0.841 h",
                   abs(rises[0] - 90.0 / (15.0 - 0.5079)) < 0.02 and abs(12.1908 / (15.0 - 0.5079) - 0.8412) < 0.001))
    a, mc = L.fraction_near_node(), L.fraction_near_node_mc()
    checks.append(("the share of new Moons close enough to a node for an eclipse is 0.185 (about 1 in 5.4), analytic and Monte Carlo",
                   abs(a - 0.1853) < 0.001 and abs(mc - a) < 0.005 and abs(1 / a - 5.4) < 0.05))
    checks.append(("edge: with no tilt every new Moon would be near the node (share 1); a bigger tilt gives a smaller share",
                   L.fraction_near_node(inclination=1.0) == 1.0 and L.fraction_near_node(10.0) < L.fraction_near_node(5.145)))
    flagged = [(w.month, w.day, n) for w, n, b in L.syzygy_latitudes(2026) if abs(b) < L.latitude_limit_deg()]
    expect = [(2, 17, "new Moon"), (3, 3, "full Moon"), (8, 12, "new Moon"), (8, 28, "full Moon")]
    ok = len(flagged) == 4 and all(f[2] == e[2] and abs((dt.date(2026, f[0], f[1]) - dt.date(2026, e[0], e[1])).days) <= 1
                                   for f, e in zip(flagged, expect))
    checks.append(("only 4 of the 25 new and full Moons of 2026 are near a node: 17 Feb, 3 Mar, 12 Aug and 28 Aug (the eclipse dates)", ok))
    ur = L.umbra_radius_km()
    checks.append(("the Earth's dark shadow at the Moon's distance has radius 4600 km, about 2.65 Moon radii",
                   abs(ur - 4600) < 5 and abs(ur / L.R_MOON - 2.65) < 0.01))
    checks.append(("at first quarter the Moon is 384400 km from the shadow axis, 84 times the shadow radius: the shadow cannot make quarter",
                   abs(L.moon_offset_from_shadow_axis_km(90) - 384400) < 1 and not L.shadow_could_touch(90) and abs(384400 / ur - 83.6) < 0.2))
    half_width = np.degrees(np.arcsin((ur + L.R_MOON) / L.MOON_DIST_KM))
    checks.append(("the shadow can reach the Moon only within 0.94 degrees of full: 1.9 of 360 degrees, about 3.7 hours a month",
                   L.shadow_could_touch(180) and L.shadow_could_touch(179.5) and not L.shadow_could_touch(178)
                   and abs(half_width - 0.94) < 0.01 and abs(2 * half_width / (360 / 29.5306 / 24) - 3.7) < 0.1))
    rows = L.year_table(40.0, 2026, [(6, 21), (12, 21), (3, 20), (9, 23), (1, 3)])
    byd = {r[0]: r for r in rows}
    checks.append(("table for 40 N: 14.84 h and noon 73.4 degrees on 21 June; 9.16 h and 26.6 degrees on 21 December",
                   abs(byd[dt.date(2026, 6, 21)][1] - 14.84) < 0.02 and abs(byd[dt.date(2026, 6, 21)][2] - 73.4) < 0.1
                   and abs(byd[dt.date(2026, 12, 21)][1] - 9.16) < 0.02 and abs(byd[dt.date(2026, 12, 21)][2] - 26.6) < 0.1))
    checks.append(("table: day and night are equal (12 h within 0.1) at the equinoxes of 2026",
                   abs(byd[dt.date(2026, 3, 20)][1] - 12) < 0.1 and abs(byd[dt.date(2026, 9, 23)][1] - 12) < 0.1))
    checks.append(("table: the Moon is more than 98 percent lit on 3 January 2026 (full Moon day)", byd[dt.date(2026, 1, 3)][3] > 0.98))
    full = L.year_table(40.0, 2026, [(m, 1) for m in range(1, 13)])
    checks.append(("table: 12 rows, every bright fraction between 0 and 1, every day length between 9 and 15 hours at 40 N",
                   len(full) == 12 and all(0 <= r[3] <= 1 and 9 < r[1] < 15 for r in full)))
    t60 = L.year_table(60.0, 2026, [(m, 21) for m in range(1, 13)])
    first15 = [r[0].month for r in t60 if r[1] > 15][0]
    checks.append(("mini-project at 60 N: 18.49 h and noon 53.4 degrees on 21 June, 5.51 h and 6.6 degrees on 21 December, first 21st over 15 h is in May",
                   abs(t60[5][1] - 18.49) < 0.02 and abs(t60[5][2] - 53.4) < 0.1 and abs(t60[11][1] - 5.51) < 0.02
                   and abs(t60[11][2] - 6.6) < 0.1 and first15 == 5))
    checks.append(("the eclipse latitude limit is 1.48 degrees, the Sun is 389 times farther than the Moon, the Moon gains 12.19 degrees a day on the Sun",
                   abs(L.latitude_limit_deg() - 1.476) < 0.001 and abs(L.SUN_DIST_KM / L.MOON_DIST_KM - 389.2) < 0.1
                   and abs(360 / L.SYNODIC - 12.19) < 0.01))
    checks.append(("edge: phase names wrap at 360 degrees", L.phase_label(0.0) == "new" and L.phase_label(359.0) == "new"
                   and L.phase_label(180.0) == "full"))
    checks.append(("25 percent bright at age 4.92 days", abs(L.illuminated_fraction(180 - 360 * 4.92 / 29.5306) - 0.25) < 0.003))
    checks.append(("the second moonrise is at 7.05 h, 0.84 h after the first", abs(rises[1] - 24.0 - 7.05 + 24.0) < 0.02 or abs(rises[1] % 24 - 7.05) < 0.02))
    checks.append(("a tilt of 2.95 degrees would put one new Moon in three near a node", abs(L.fraction_near_node(2.9526) - 1 / 3) < 0.002))
    checks.append(("the mean-motion calendar is more than 5 hours off the almanac on 3 Jan, 3 Mar and 28 Aug",
                   all(e * 24 > 5 for e in (errs[0], errs[1], errs[3]))))
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
