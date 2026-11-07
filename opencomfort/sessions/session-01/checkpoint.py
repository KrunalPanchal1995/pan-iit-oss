"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    ua = L.ua_total(L.ROOM["surfaces"])
    checks.append(("example room: UA = 2 x 10 + 5 x 2 + 2.5 x 16 = 70 W/K", abs(ua - 70.0) < 1e-9))
    checks.append(("worked example: 2 m2 glass, SHGC 0.8, 500 W/m2, 80% shaded gives 160 W",
                   abs(L.solar_gain(2.0, 0.8, 500.0, 0.8) - 160.0) < 1e-9))
    checks.append(("hand calculation: 10 ACH in 48 m3 is 0.1333 m3/s and 160 W/K",
                   abs(L.flow_rate(10, 48) - 48 / 360) < 1e-12 and abs(L.ventilation_conductance(10, 48) - 160.0) < 1e-9))
    t = L.steady_indoor_temperature(34.0, 70.0, 160.0, 160.0, 250.0)
    checks.append(("worked example: steady indoor = 34 + 410 / 230 = 35.78 C", abs(t - (34 + 410 / 230)) < 1e-9))
    checks.append(("energy balance: net heat flow is zero at the steady temperature",
                   abs(L.heat_balance(34.0, t, 70.0, 160.0, 160.0, 250.0)) < 1e-9))
    checks.append(("no gains means the room sits at outdoor temperature",
                   abs(L.steady_indoor_temperature(30.0, 70.0, 50.0, 0.0, 0.0) - 30.0) < 1e-12))
    t_lo = L.steady_indoor_temperature(34.0, 70.0, L.ventilation_conductance(1, 48), 800, 250)
    t_hi = L.steady_indoor_temperature(34.0, 70.0, L.ventilation_conductance(1000, 48), 800, 250)
    checks.append(("limit: huge air flow pulls the room to outdoor temperature (within 0.1 K)", abs(t_hi - 34.0) < 0.1 and t_lo > t_hi))
    checks.append(("more shade never makes the room hotter",
                   L.solar_gain(2, 0.8, 500, 0.9) < L.solar_gain(2, 0.8, 500, 0.5) < L.solar_gain(2, 0.8, 500, 0.0)))
    checks.append(("full shade blocks all direct sun", L.solar_gain(2, 0.8, 500, 1.0) == 0.0))
    checks.append(("ventilation with cooler outside air removes heat",
                   L.ventilation_gain(10, 48, 28.0, 32.0) < 0 and abs(L.ventilation_gain(10, 48, 28.0, 32.0) + 640.0) < 1e-9))
    checks.append(("conduction: 2 W/(m2 K) x 10 m2 x 6 K = 120 W", abs(L.conduction_gain(2.0, 10.0, 34.0, 28.0) - 120.0) < 1e-9))
    checks.append(("two people and 100 W of lamps give 250 W", abs(L.internal_gain(2, 100.0) - 250.0) < 1e-12))
    bad = 0
    for call in (lambda: L.solar_gain(2, 0.8, 500, 1.5), lambda: L.flow_rate(5, 0),
                 lambda: L.steady_indoor_temperature(30, 0, 0, 100, 0), lambda: L.conduction_gain(-1, 2, 30, 20)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 4))
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
