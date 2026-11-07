"""Checkpoint for Session 3. Prints PASS or FAIL."""
import datetime as dt

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # the Saros near-equalities
    s223, d242, a239 = 223 * L.SYNODIC, 242 * L.DRACONIC, 239 * L.ANOMALISTIC
    checks.append(("223 synodic = 6585.32 days; 242 draconic = 6585.36; 239 anomalistic = 6585.54",
                   abs(s223 - 6585.32) < 0.01 and abs(d242 - 6585.36) < 0.01 and abs(a239 - 6585.54) < 0.01))
    m1, m2 = L.saros_mismatches()
    checks.append(("mismatches are 0.036 and 0.216 days: all within a fraction of a day",
                   abs(m1 - 0.036) < 0.002 and abs(m2 - 0.216) < 0.002 and max(abs(m1), abs(m2)) < 0.25))
    checks.append(("0.036 days is about 52 minutes; 0.216 days is about 5.2 hours",
                   abs(m1 * 1440 - 52) < 1 and abs(m2 * 24 - 5.2) < 0.1))
    days, hours = L.saros_calendar()
    checks.append(("18 years + 11 days + 7.7 hours (about 8 hours) when the 18 years hold 4 leap days",
                   days == 11 and abs(hours - 7.7) < 0.1 and abs(s223 / 365.2425 - 18.03) < 0.01))
    checks.append(("the leftover 0.32 day shifts the eclipse track about 115.7 degrees west (about 120)",
                   abs(L.saros_longitude_shift_deg() - 115.7) < 0.2 and abs(L.saros_longitude_shift_deg() - 120) < 5))
    checks.append(("three Saros periods = 19755.96 days = 54.09 years, and the track returns to within 13 degrees of its start",
                   abs(3 * s223 - 19755.96) < 0.01 and abs(3 * s223 / 365.2425 - 54.09) < 0.01
                   and abs((3 * L.saros_longitude_shift_deg()) % 360 - 347.05) < 0.2))
    checks.append(("one Saros moves the Moon 0.478 degrees along its orbit relative to the node; a series holds about 69 eclipses",
                   abs(abs(L.saros_node_drift_deg()) - 0.478) < 0.005 and L.saros_series_length(16.7) == 69))

    # timing errors against published eclipses
    e1 = np.abs(L.timing_errors_hours(True))
    e0 = np.abs(L.timing_errors_hours(False))
    checks.append(("with the seven time corrections every one of 13 eclipses is predicted within 0.5 hours (largest 0.2)",
                   e1.max() < 0.5 and abs(e1.max() - 0.2) < 0.1))
    checks.append(("with mean motion only, the largest error is 12.7 hours (under 14)",
                   e0.max() < 14 and abs(e0.max() - 12.7) < 0.2))
    checks.append(("predicted gamma is within 0.04 Earth radii of the published value for all 13",
                   np.abs(L.gamma_errors()).max() < 0.04))
    checks.append(("failure case: the predicted kind matches the published kind for 11 of 13 eclipses",
                   L.kinds_match() == 11))

    # worked example: 8 April 2024
    when = dt.datetime(2024, 4, 8, 18, 17)
    k = L.nearest_k(when)
    mean_t = L.jd_to_datetime(L.new_moon_mean_jd(k))
    corr_min = (L.new_moon_jd(k) - L.new_moon_mean_jd(k)) * 1440.0
    e = L.predict(k)
    checks.append(("worked example: k = 300; mean new moon 18:35, correction -12.4 min, corrected 18:22, published 18:17",
                   k == 300 and mean_t.hour == 18 and mean_t.minute == 35 and abs(corr_min + 12.4) < 0.2
                   and e["date"].hour == 18 and e["date"].minute == 22))
    checks.append(("worked example: node distance 1.9 degrees, latitude 0.36 degrees, gamma 0.35, predicted total",
                   abs(L.node_distance(L.clocks(k)[2]) - 1.9) < 0.1 and abs(e["beta"] - 0.356) < 0.01
                   and abs(e["gamma"] - 0.351) < 0.005 and e["kind"] == "total"))

    # Saros repeat
    a = L.predict(L.nearest_k(dt.datetime(2017, 8, 21, 18, 25)))
    b = L.saros_partner(a["k"])
    checks.append(("one Saros after the 2017 total eclipse the model gives another total eclipse, 6585.3 days later",
                   b["kind"] == a["kind"] == "total" and abs((b["jd"] - a["jd"]) - 6585.3) < 0.1))
    counts = [L.count_eclipses(k0, 223) for k0 in (0, 223, 446, -223)]
    checks.append(("every block of 223 new moons (one Saros, 18 years) holds 40 predicted solar eclipses",
                   counts == [40, 40, 40, 40]))
    checks.append(("one degree of latitude error changes a partial eclipse magnitude by about 1.9",
                   abs(L.magnitude_change_per_degree() - 1.88) < 0.01))

    # mini-project
    got = [(x["date"].strftime("%Y-%m-%d"), x["kind"])
           for x in L.eclipses_between(dt.datetime(2027, 1, 1), dt.datetime(2029, 12, 31, 23, 59))]
    want = [("2027-02-06", "annular"), ("2027-08-02", "total"), ("2028-01-26", "annular"), ("2028-07-22", "total"),
            ("2029-01-14", "partial"), ("2029-06-12", "partial"), ("2029-07-11", "partial"), ("2029-12-05", "partial")]
    checks.append(("mini-project: 3-year window 2027 to 2029 holds 8 eclipses (2 total, 2 annular, 4 partial)", got == want))
    # edge: node distance symmetry and boundaries
    checks.append(("edge: node distance is 0 at F = 0 and 180, 90 at F = 90, and never above 90",
                   L.node_distance(0.0) == 0.0 and L.node_distance(180.0) == 0.0 and L.node_distance(90.0) == 90.0
                   and max(L.node_distance(f) for f in np.linspace(0, 720, 97)) <= 90.0))
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
