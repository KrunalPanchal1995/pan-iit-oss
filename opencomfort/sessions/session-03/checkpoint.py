"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # validation against Session 1: constant weather gives the steady formula
    const = lambda h: (34.0, 34.0, 160.0, 10.0)
    v = L.simulate_day(forcing=const)
    t_s1 = 34.0 + (160.0 + 250.0) / (70.0 + 160.0)
    checks.append(("validation: constant inputs reproduce Session 1 (35.78 C) at every step",
                   float(np.max(np.abs(v["t_air"] - t_s1))) < 1e-6))
    checks.append(("validation: with constant inputs the mass sits at air temperature + 0.7 x 160 / 400",
                   abs(v["t_mass"][0] - (t_s1 + 0.7 * 160.0 / 400.0)) < 1e-6))
    base = L.simulate_day(0.0, 0.8, "closed")
    best = L.simulate_day(0.6, 0.3, "night")
    checks.append(("periodic steady state: the mass ends the day where it started", base["periodic_error"] < 1e-6 and best["periodic_error"] < 1e-6))
    checks.append(("energy balance: heat in over the day = heat stored (within 0.1 percent)",
                   abs(base["energy_residual"]) < 1e-3 * base["energy_scale"] and abs(best["energy_residual"]) < 1e-3 * best["energy_scale"]))
    checks.append(("worked example: as built peaks at 46.3 C; shade + white roof + night flush at 36.9 C",
                   abs(base["peak"] - 46.33) < 0.05 and abs(best["peak"] - 36.86) < 0.05))
    checks.append(("worked example: sol-air of a dark roof at 15:00 = 35.5 + 0.8 x 715.7 / 20 - 3.9 = 60.2 C",
                   abs(L.sol_air(35.5, 715.74, 0.8) - 60.23) < 0.01 and abs(float(L.roof_sun(15.0)) - 715.74) < 0.05))
    checks.append(("outdoor model: 35.5 C at 15:00, 26.5 C at 03:00",
                   abs(L.outdoor_temperature(15.0) - 35.5) < 1e-12 and abs(L.outdoor_temperature(3.0) - 26.5) < 1e-12))
    checks.append(("comfort limit: 0.31 x 31 + 17.8 + 3.5 = 30.91 C, plus 1.8 K with a fan",
                   abs(L.comfort_upper_limit(31.0) - 30.91) < 1e-9 and abs(L.comfort_upper_limit(31.0, fan_bonus=1.8) - 32.71) < 1e-9))
    checks.append(("degree-hours: 2 K above the limit for 3 h is 6 K h",
                   abs(L.degree_hours([0, 1, 2, 3], [34, 34, 34, 34], 32.0) - 6.0) < 1e-12))
    checks.append(("each passive measure lowers the peak: white roof, overhang, ventilation",
                   L.simulate_day(0.0, 0.3, "closed")["peak"] < base["peak"]
                   and L.simulate_day(0.6, 0.8, "closed")["peak"] < base["peak"]
                   and L.simulate_day(0.0, 0.8, "open")["peak"] < base["peak"]))
    light = L.simulate_day(0.6, 0.3, "night", room=dict(L.ROOM, c_mass=1.0e6))
    heavy = L.simulate_day(0.6, 0.3, "night", room=dict(L.ROOM, c_mass=20.0e6))
    checks.append(("more thermal mass gives a smaller daily swing",
                   (heavy["t_air"].max() - heavy["t_air"].min()) < (best["t_air"].max() - best["t_air"].min()) < (light["t_air"].max() - light["t_air"].min())))
    checks.append(("night flush beats all-day opening when nights are much cooler (28 +/- 9 C)",
                   L.simulate_day(0.6, 0.3, "night", t_mean=28.0, t_amp=9.0)["peak"] < L.simulate_day(0.6, 0.3, "open", t_mean=28.0, t_amp=9.0)["peak"]))
    checks.append(("time step: 5 and 15 minute steps agree within 0.01 K",
                   abs(L.simulate_day(0.6, 0.3, "night", dt_min=15)["peak"] - best["peak"]) < 0.01))
    limit = L.comfort_upper_limit(31.0, fan_bonus=1.8)
    pick = L.choose_design(25.0, limit)
    checks.append(("mini-project: cheapest design under 25 K h is a white roof with windows open (8000 rupees)",
                   pick is not None and pick[0] == 8000 and pick[2] == 0.3 and pick[3] == "open" and pick[4] <= 25.0))
    bad = 0
    for call in (lambda: L.sol_air(30, 500, 1.2), lambda: L.comfort_upper_limit(40), lambda: L.ach_schedule("sometimes", 3.0),
                 lambda: L.simulate_day(dt_min=7)):
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
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
