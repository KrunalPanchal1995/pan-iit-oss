"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("angular diameters: Sun 0.533, Moon 0.518 degrees",
                   abs(L.angular_diameter_deg(1.3927e6, 1.496e8) - 0.533) < 0.001
                   and abs(L.angular_diameter_deg(3474, 384400) - 0.518) < 0.001))

    Lu = L.umbra_length()
    checks.append(("hand calculation: L = D r / (R - r) = 1.496e8 * 1737 / 694263 = 374289 km",
                   abs(1.496e8 * 1737 / (696000 - 1737) - 374289) < 1 and abs(Lu - 374289) < 1))
    checks.append(("umbra length 374289 km is 10111 km short of the mean Moon-Earth distance 384400 km",
                   abs((384400 - Lu) - 10111) < 1))
    # similar triangles, independent check: the line through the Sun's and Moon's edges reaches the axis at L
    slope = (L.R_SUN - L.R_MOON) / L.D_SUN
    checks.append(("similar triangles: the tangent line has slope (R - r)/D and crosses the axis at r/slope",
                   abs(L.R_MOON / slope - Lu) < 1e-6 and abs(L.umbra_radius_at(0.0) - L.R_MOON) < 1e-9
                   and abs(L.umbra_radius_at(Lu)) < 1e-9))

    checks.append(("nearest ground is 378022 km from the mean Moon, so the tip stops 3733 km short; antumbra radius 17.3 km",
                   L.ground_distance(384400.0) == 378022.0 and abs(Lu - 378022 + 3733) < 1
                   and abs(abs(L.umbra_radius_at(378022.0)) - 17.3) < 0.1))
    v = 2 * np.pi * 356500.0 / (27.321661 * 86400.0) - 0.465
    checks.append(("shadow speed at perigee is 0.484 km/s, and 224.3 km / 0.484 km/s is 463 s",
                   abs(v - 0.484) < 0.001 and abs(L.path_width_km(356500.0) / v - 463) < 1.5))
    checks.append(("total if the Earth-Moon distance is below 380667 km (L + R_EARTH)",
                   abs(L.critical_total_distance() - 380667) < 1))
    checks.append(("mean Moon (384400 km) gives annular; perigee 356500 km total; apogee 406700 km annular",
                   L.eclipse_kind_overhead(384400.0) == "annular" and L.eclipse_kind_overhead(356500.0) == "total"
                   and L.eclipse_kind_overhead(406700.0) == "annular"))
    s = 356500.0 - 6378.0
    hand = 2 * 1737.0 * (374289.0 - s) / 374289.0
    checks.append((f"worked example: perigee totality path is about 224 km wide (hand {hand:.1f} km)",
                   abs(L.path_width_km(356500.0) - 224.3) < 0.2 and abs(hand - 224.3) < 0.2))
    checks.append(("path width stays below 300 km for every Moon distance from 356000 to 407000 km",
                   max(L.path_width_km(d) for d in np.linspace(356000, 407000, 60)) < 300))
    checks.append(("mean Moon: the ring (antumbra) circle is only 34.6 km wide; apogee 241.6 km",
                   abs(L.path_width_km(384400.0) - 34.6) < 0.2 and abs(L.path_width_km(406700.0) - 241.6) < 0.2))
    checks.append(("totality lasts about 7.7 minutes at perigee on the equator (224 km / 0.484 km/s)",
                   abs(L.totality_minutes(356500.0) - 7.7) < 0.1))
    checks.append(("penumbra radius at the ground is 3500 km, so the partial region is about 7000 km wide",
                   abs(L.penumbra_radius_at(384400.0 - 6378.0) - 3500) < 2))
    checks.append(("lunar eclipse: Earth's shadow at the Moon is 4606 km in radius, 2.65 Moon radii",
                   abs(L.earth_umbra_radius_at_moon() - 4606) < 2 and abs(L.earth_umbra_radius_at_moon() / 1737 - 2.65) < 0.01))

    # eclipse limit
    bp, bc = L.beta_limit_partial(384400.0), L.beta_limit_central(384400.0)
    checks.append(("mean Moon: parallax 0.951; latitude limits 1.476 (partial) and 0.951 degrees (central)",
                   abs(L.parallax_deg(384400.0) - 0.951) < 0.001 and abs(bp - 1.476) < 0.001 and abs(bc - 0.951) < 0.001))
    hand = np.degrees(np.arcsin(np.sin(np.radians(1.4762)) / np.sin(np.radians(5.145))))
    checks.append((f"hand calculation: asin(sin 1.4762 / sin 5.145) = {hand:.1f} degrees",
                   abs(hand - 16.7) < 0.05 and abs(L.node_limit_deg(bp) - 16.7) < 0.05))
    checks.append(("limits from the node: partial about 16.7 degrees, central about 10.7 degrees (mean Moon)",
                   abs(L.node_limit_deg(bp) - 16.7) < 0.05 and abs(L.node_limit_deg(bc) - 10.7) < 0.05))
    checks.append(("brute-force 3-D vectors agree with the formula to 0.01 degrees",
                   abs(L.node_limit_numeric(bp) - L.node_limit_deg(bp)) < 0.01
                   and abs(L.node_limit_numeric(bc) - L.node_limit_deg(bc)) < 0.01))
    big, sure, cen = L.limit_range()
    checks.append(("extremes: partial possible up to 18.4, certain within 15.4; central up to 11.8 degrees",
                   abs(big - 18.4) < 0.05 and abs(sure - 15.4) < 0.05 and abs(cen - 11.8) < 0.05))
    checks.append(("edge: a latitude limit larger than the orbit tilt allows every angle (90 degrees)",
                   L.node_limit_deg(10.0) == 90.0))

    # seasons
    checks.append(("eclipse seasons are 173.31 days apart; the Sun passes the node at 1.0386 degrees per day",
                   abs(L.season_spacing_days() - 173.31) < 1e-9 and abs(L.sun_node_rate_deg_per_day() - 1.0386) < 1e-4))
    checks.append(("a season of limit 16.7 degrees lasts 32.1 days, longer than a synodic month 29.53 days",
                   abs(L.season_length_days(16.7) - 32.1) < 0.1 and L.season_length_days(16.7) > L.SYNODIC))
    checks.append(("with the certain limit 15.4 degrees the season is 29.65 days: still longer than 29.53, so every season has a new moon in it",
                   abs(L.season_length_days(15.4) - 29.65) < 0.02 and L.season_length_days(15.4) > L.SYNODIC))
    checks.append(("2.107 seasons per year; seasons arrive 18.62 days earlier each year; about 21 in 10 years",
                   abs(L.seasons_per_tropical_year() - 2.107) < 0.001 and abs(L.seasons_drift_days_per_year() - 18.62) < 0.01
                   and round(10 * L.seasons_per_tropical_year()) == 21))
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
