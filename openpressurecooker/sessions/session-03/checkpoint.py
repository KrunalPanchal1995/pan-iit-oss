"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    ck = L.simulate(gauge_kpa=100.0)
    op = L.open_pot()

    # --- worked example: 1 kg water, 1000 W, 80 % efficiency, 100 kPa gauge ---
    hand = L.heatup_time_hand() / 60.0
    sim = ck["t_boil"] / 60.0
    checks.append((f"worked example: hand heat-up time {hand:.2f} min (9.73), simulated {sim:.2f} min (9.90), within 3 percent",
                   abs(hand - 9.73) < 0.02 and abs(sim - 9.90) < 0.05 and abs(sim - hand) / hand < 0.03))
    m_s = L.steam_mass(ck["tb"], 3e-3) * 1000.0
    checks.append((f"worked example: headspace holds {m_s:.2f} g of steam at 120.6 C (ideal gas, 3 L)", abs(m_s - 3.32) < 0.02))
    checks.append((f"worked example: cooker done at {ck['t_done'] / 60:.1f} min, open pot at {op['t_done'] / 60:.1f} min",
                   abs(ck["t_done"] / 60 - 18.3) < 0.1 and abs(op["t_done"] / 60 - 46.3) < 0.1))

    # --- validation ---
    checks.append(("energy balance closes (cooker) to 1e-6", abs(L.energy_closure(ck)) < 1e-6))
    checks.append(("energy balance closes (open pot) to 1e-6", abs(L.energy_closure(op)) < 1e-6))
    bl = L.blocked_vent()
    checks.append(("energy balance closes (blocked vent) to 1e-6", abs(L.energy_closure(bl)) < 1e-6))
    checks.append(("plateau temperature equals the Clausius-Clapeyron boiling point (120.6 C)", abs(ck["temp_c"][-1] - 120.61) < 0.02))
    checks.append(("open pot never exceeds 100 C", float(op["temp_c"].max()) <= 100.0 + 1e-6))
    checks.append(("saturation pressure at the boiling point returns the set pressure", abs(L.psat_kpa(L.tsat_k(201.325)) - 201.325) < 1e-9))
    checks.append(("Clausius-Clapeyron at 200 kPa is within 0.5 C of the steam table (120.2 C)", abs(L.tsat_k(200.0) - 273.15 - 120.2) < 0.5))
    fine = L.simulate(gauge_kpa=100.0, dt=0.25)
    checks.append(("halving the time step twice changes the finish time by under 0.02 min", abs(fine["t_done"] - ck["t_done"]) / 60 < 0.02))
    analytic = 0.8 * 0.25 * 1000.0 * (ck["t_done"] - ck["t_boil"]) / L.L_MASS
    checks.append(("water lost matches hold power times time over latent heat (2 percent)", abs(ck["lost_kg"] - analytic) / analytic < 0.02))
    checks.append(("Arrhenius rate is 1 at 100 C and about 2 at 110 C", abs(L.arrhenius(373.15) - 1.0) < 1e-12 and abs(L.arrhenius(383.15) - 2.0) < 0.02))

    # --- model behaviour: sensitivity and edge cases ---
    times = [L.simulate(gauge_kpa=g)["t_done"] for g in (25.0, 50.0, 100.0, 150.0)]
    checks.append(("a higher regulator pressure always finishes sooner", all(a > b for a, b in zip(times, times[1:]))))
    boils = [L.simulate(power_w=w)["t_boil"] for w in (500.0, 1000.0, 2000.0)]
    checks.append(("more heater power reaches boiling sooner (about 1/P)", boils[0] > boils[1] > boils[2] and abs(boils[0] / boils[2] - 4.0) < 0.1))
    checks.append(("the cooker finishes in less than half the open-pot time", ck["t_done"] < 0.5 * op["t_done"]))
    checks.append(("the cooker loses less water than the open pot", ck["lost_kg"] < op["lost_kg"]))
    near_zero = L.simulate(gauge_kpa=0.0, v_head=0.0)
    checks.append(("regulator at 0 kPa with no headspace reproduces the open pot", abs(near_zero["t_done"] - op["t_done"]) < 1e-9))

    # --- failure case: blocked vent ---
    p = bl["p_abs"]
    checks.append(("blocked vent: pressure never falls", bool(np.all(np.diff(p) >= -1e-9))))
    reg_t = bl["t"][int(np.argmax(p >= 201.325))]
    stop_t = bl["t"][-1]
    checks.append((f"blocked vent: pressure goes from 201 to 300 kPa absolute in {(stop_t - reg_t):.0f} s (under 120 s)", 60.0 < stop_t - reg_t < 120.0))
    i = int(np.argmax(p >= 200.0))
    rate = L.pressure_rise_rate_kpa_per_s(bl["temp_c"][i] + 273.15, bl["temp_c"][i + 1] - bl["temp_c"][i])
    checks.append((f"blocked vent: pressure rises about {rate:.2f} kPa/s near 200 kPa absolute", 0.8 < rate < 1.2))

    # --- mini-project helper ---
    h = L.cooker_hold_minutes(40.0, 100.0)
    checks.append((f"mini-project: 40 min open-pot recipe needs {h:.2f} min at 100 kPa gauge (about 8.8)", abs(h - 8.76) < 0.1))
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
