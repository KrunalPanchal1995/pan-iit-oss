"""Checkpoint for Session 3. Prints PASS or FAIL."""
import itertools

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # hand-calculated thresholds
    lo, hi = L.lux_at_voltage(2.25), L.lux_at_voltage(2.75)
    checks.append((f"hand calculation: 2.25 V is 13.0 lux and 2.75 V is 23.1 lux (got {lo:.1f}, {hi:.1f})",
                   abs(lo - 13.0) < 0.05 and abs(hi - 23.1) < 0.05))
    checks.append(("the divider at the threshold light levels returns the threshold voltages",
                   abs(float(L.sensor_voltage(lo)) - 2.25) < 1e-9 and abs(float(L.sensor_voltage(hi)) - 2.75) < 1e-9))

    # schmitt behaviour
    v = np.array([3.0, 2.6, 2.3, 2.2, 2.4, 2.7, 2.8, 2.6, 2.3])
    checks.append(("Schmitt: on below 2.25 V, holds between 2.25 and 2.75 V, off above 2.75 V",
                   list(L.schmitt(v)) == [False, False, False, True, True, True, False, False, False]))
    checks.append(("a plain comparator at 2.5 V flips at every crossing, the Schmitt does not",
                   L.count_switches(L.plain_comparator(np.array([2.6, 2.4, 2.6, 2.4, 2.6]))) == 4
                   and L.count_switches(L.schmitt(np.array([2.6, 2.4, 2.6, 2.4, 2.6]))) == 0))
    checks.append(("a Schmitt with equal thresholds behaves like a plain comparator",
                   list(L.schmitt(v, 2.5, 2.5)) == list(L.plain_comparator(v, 2.5))))

    # chatter
    plain = L.simulate_day(seed=7, hysteresis=False)
    hyst = L.simulate_day(seed=7, hysteresis=True)
    checks.append((f"worked example: seed 7 day gives {plain['switches']} switches without hysteresis and {hyst['switches']} with",
                   plain["switches"] == 20 and hyst["switches"] == 2))
    many = all(L.simulate_day(seed=s, hysteresis=False)["switches"] > L.simulate_day(seed=s)["switches"] for s in range(1, 9))
    checks.append(("for 8 different cloudy days hysteresis always gives fewer switches", many))
    checks.append(("a clean (no cloud) day has exactly 2 switches even without hysteresis",
                   L.simulate_day(sigma=0.0, hysteresis=False)["switches"] == 2))

    # validation against the analytic crossing times
    clean = L.simulate_day(sigma=0.0, hysteresis=True)
    t_on = L.analytic_cross_times(lo)[0]
    t_off = L.analytic_cross_times(hi)[1]
    analytic_hours = (24.0 - t_on) + t_off
    checks.append((f"simulated on-hours {clean['on_hours']:.3f} match the analytic {analytic_hours:.3f} to one step",
                   abs(clean["on_hours"] - analytic_hours) < 2 * L.DT_MIN / 60))
    first_on = clean["minutes"][np.argmax(clean["led"] & (clean["minutes"] > 720))] / 60
    checks.append((f"first evening switch-on is at {first_on:.2f} h, analytic {t_on:.2f} h",
                   abs(first_on - t_on) < 2 * L.DT_MIN / 60))
    checks.append(("clean light crosses 20 lux at about 06:00 and 18:00", np.allclose(L.analytic_cross_times(20.0), [18.0, 6.0], atol=0.01)))

    # power and energy
    i_led = L.led_path_current()
    checks.append(("LED path current is (5 - 2 - 0.2) / 330 = 8.48 mA", abs(i_led * 1e3 - 8.485) < 0.01))
    e_expected = hyst["on_hours"] * 5.0 * (i_led + (5.0 - 0.7) / 4700.0)
    checks.append(("energy is at least the LED on-hours times the LED supply power",
                   hyst["energy_wh"] >= e_expected and hyst["energy_wh"] < e_expected + 0.05))

    # Monte Carlo
    fixed, _ = L.monte_carlo_trip(ratiometric=False, r10_sigma=0.0, r_tol=0.0)
    ratio, _ = L.monte_carlo_trip(ratiometric=True, r10_sigma=0.0, r_tol=0.0)
    checks.append(("supply only: a Vcc / 2 reference gives one trip point (17.35 lux), a fixed 2.5 V reference spreads it",
                   np.ptp(ratio) < 1e-9 and abs(ratio[0] - 17.35) < 0.05 and np.ptp(fixed) > 5.0))
    allp, _ = L.monte_carlo_trip(ratiometric=True)
    p5, p50, p95 = np.percentile(allp, [5, 50, 95])
    checks.append((f"with all tolerances the trip point is 9.8 to 26.2 lux (5th-95th percentile), median 17.4 (got {p5:.1f}, {p95:.1f}, {p50:.1f})",
                   abs(p5 - 9.8) < 0.5 and abs(p95 - 26.2) < 1.0 and abs(p50 - 17.4) < 0.5))

    # logic
    names = ["A", "B"]
    expect_or = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
    checks.append(("worked example: the alarm OR gate gives the truth table 0, 1, 1, 1", L.truth_table(L.ALARM_OR, names, "alarm") == expect_or))
    checks.append(("NOT A NAND NOT B equals OR on every row (De Morgan)",
                   L.truth_table(L.ALARM_NAND, names, "alarm") == expect_or))
    checks.append(("XOR is the wrong alarm: it stays silent when both conditions are violated",
                   L.truth_table(L.ALARM_XOR, names, "alarm")[3][1] == 0))
    for g, f in (("AND", lambda a, b: a and b), ("OR", lambda a, b: a or b), ("NAND", lambda a, b: not (a and b)), ("NOR", lambda a, b: not (a or b))):
        ok = all(L.GATES[g](a, b) == int(f(a, b)) for a, b in itertools.product((0, 1), repeat=2))
        checks.append((f"gate {g} matches Python logic on all 4 rows", ok))
    ok = all(L.truth_table(L.OVERRIDE, ["DARK", "FORCE_ON", "FORCE_OFF"], "led")[i][1] ==
             int((d or fo) and not ff) for i, (d, fo, ff) in enumerate(itertools.product((0, 1), repeat=3)))
    checks.append(("override controller: LED = (DARK or FORCE_ON) and not FORCE_OFF on all 8 rows", ok))

    # override day
    n = 1440
    fo = np.zeros(n, bool)
    fo[720:780] = True
    ff = np.zeros(n, bool)
    ff[1320:1410] = True
    day = L.simulate_day(seed=7, force_on=fo, force_off=ff)
    checks.append((f"override day: 12:00-13:00 on, 22:00-23:30 off gives {day['on_hours']:.2f} h on (baseline {hyst['on_hours']:.2f})",
                   abs(day["on_hours"] - 11.53) < 0.02 and abs(hyst["on_hours"] - 12.03) < 0.02 and day["switches"] == 6))
    both = L.simulate_day(seed=7, force_on=np.ones(n, bool), force_off=np.ones(n, bool))
    checks.append(("edge: if both override buttons are held, the LED is off (off wins)", both["on_hours"] == 0.0))

    # failure case: not saturated
    peak = max(L.unsaturated_power(rb, 30.0)[2] for rb in np.linspace(2000, 200000, 2000))
    sat = L.unsaturated_power(2200.0, 30.0)[2]
    checks.append((f"failure: a half-on transistor for a 100 mA lamp dissipates {peak * 1e3:.0f} mW, over 3 times the saturated {sat * 1e3:.0f} mW",
                   peak > 3 * sat and abs(peak * 1e3 - 75.0) < 1.0))
    ic, vce, _ = L.unsaturated_power(470e3, 330.0)
    checks.append(("failure: R_B = 470 kohm gives under 1 mA in the LED (dim)", ic < 0.001))
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
