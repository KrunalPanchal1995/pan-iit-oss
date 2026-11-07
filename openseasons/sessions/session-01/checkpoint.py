"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("at the equator on an equinox it is day at noon and night at midnight",
                   L.is_daylight(0, 0, 0) and not L.is_daylight(0, 180, 0)))
    checks.append(("with no tilt every latitude gets 12 hours of daylight (day and night come from the spin)",
                   all(abs(L.daylight_hours(lat, 0.0) - 12.0) < 0.01 for lat in (0, 30, 60, 85))))
    d_jun, d_dec = L.declination(172), L.declination(355)
    h_jun, h_dec = L.noon_height(40, d_jun), L.noon_height(40, d_dec)
    checks.append(("worked example: noon Sun height at 40 N is 73.4 degrees in June and 26.6 in December",
                   abs(h_jun - 73.4) < 0.1 and abs(h_dec - 26.6) < 0.1))
    checks.append(("hand calculation: 90 - 40 + 23.4 = 73.4 and 90 - 40 - 23.4 = 26.6",
                   abs(h_jun - (90 - 40 + 23.4)) < 0.1 and abs(h_dec - (90 - 40 - 23.4)) < 0.1))
    checks.append(("with no tilt the noon height is the same in June and December (no seasons)",
                   abs(L.noon_height(40, L.declination(172, 0.0)) - L.noon_height(40, L.declination(355, 0.0))) < 1e-9))
    checks.append(("day length at 40 N is 14.84 h in June and 9.16 h in December",
                   abs(L.daylight_hours(40, d_jun) - 14.84) < 0.03 and abs(L.daylight_hours(40, d_dec) - 9.16) < 0.03))
    days = np.arange(1, 366)
    r = L.distance_mkm(days)
    checks.append(("the Earth is closest to the Sun on day 4 (early January): 147.1 million km",
                   int(days[np.argmin(r)]) == 4 and abs(r.min() - 147.1) < 0.05))
    checks.append(("the Earth is farthest in early July: 152.1 million km",
                   183 <= int(days[np.argmax(r)]) <= 188 and abs(r.max() - 152.1) < 0.05))
    checks.append(("on 4 January the Sun is south of the equator (northern winter) although the Earth is closest",
                   L.declination(4) < -22 and L.noon_height(40, L.declination(4)) < 30))
    checks.append(("on 4 January 40 N has a low Sun (27.5) and 40 S a high Sun (72.5): opposite seasons, one distance",
                   abs(L.noon_height(40, L.declination(4)) - 27.5) < 0.1 and abs(L.noon_height(-40, L.declination(4)) - 72.5) < 0.1))
    checks.append(("distance changes the sunlight by only about 7 percent, tilt changes the noon sunlight on flat ground (sine of the height) by a factor of 2.1",
                   abs((r.max() / r.min()) ** 2 - 1.069) < 0.002 and abs(np.sin(np.radians(h_jun)) / np.sin(np.radians(h_dec)) - 2.15) < 0.05))
    checks.append(("Moon: lit fraction is 0 at new Moon, 0.5 at first quarter, 1 at full Moon",
                   abs(L.lit_fraction_simple(0)) < 1e-9 and abs(L.lit_fraction_simple(29.53 / 4) - 0.5) < 1e-9
                   and abs(L.lit_fraction_simple(29.53 / 2) - 1.0) < 1e-9))
    checks.append(("the eight phase names follow the age", [L.phase_name(a) for a in (0, 3.7, 7.4, 11.1, 14.8, 18.4, 22.1, 25.8)]
                   == ["new", "waxing crescent", "first quarter", "waxing gibbous", "full", "waning gibbous", "last quarter", "waning crescent"]))
    img = L.moon_image(90.0)
    inside = ~np.isnan(img)
    checks.append(("a picture of the first-quarter Moon is half bright (50 percent of the disc)",
                   abs(np.nanmean(img) - 0.5) < 0.02 and inside.sum() > 1000))
    checks.append(("edge: the age wraps after one month", L.phase_name(29.53) == "new" and abs(L.lit_fraction_simple(29.53 + 7.4) - L.lit_fraction_simple(7.4)) < 1e-9))
    checks.append(("the June-December swing at 40 N is 46.8 degrees, twice the tilt",
                   abs((h_jun - h_dec) - 46.8) < 0.05))
    checks.append(("60 N: noon Sun 53.4 degrees in June and 6.6 in December",
                   abs(L.noon_height(60, d_jun) - 53.4) < 0.1 and abs(L.noon_height(60, d_dec) - 6.6) < 0.1))
    checks.append(("equinoxes near day 80 and day 263: the Sun is over the equator and 40 N and 40 S both have a 50 degree noon Sun",
                   abs(L.declination(80)) < 0.01 and abs(L.declination(263)) < 0.3 and abs(L.noon_height(40, 0.0) - 50.0) < 1e-9))
    checks.append(("design: within 21.6 degrees of the equator the lowest noon Sun is 45 degrees",
                   abs(L.noon_height(21.6, L.declination(355)) - 45.0) < 0.1))
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
