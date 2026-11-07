"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    T = L.weather()
    checks.append(("weather is reproducible (same seed, same winter)", np.array_equal(T, L.weather())))
    checks.append(("weather has 151 x 24 = 3624 hours", len(T) == 3624))
    checks.append(("the coldest hour is between -13 and -9 C", -13.0 < T.min() < -9.0))

    # exact solution with no heating at all: T = T_out + (T0 - T_out) exp(-t / tau)
    r = L.simulate(np.zeros(48), ua=0.2, cap_c=4.0, rated_kw=0.0, backup_kw=0.0)
    exact = 20.0 * np.exp(-np.arange(49) / (4.0 / 0.2))
    checks.append(("a house with no heating cools like exp(-t / tau), tau = C / UA = 20 h", np.allclose(r["t_in"], exact, atol=1e-9)))

    # energy conservation, three different situations
    rated = L.size_rated_kw(0.20, 20.0, -10.0)
    hp = L.simulate(T, rated_kw=rated)
    ht = L.simulate(T, mode="heater", backup_kw=20.0)
    sag = L.simulate(T[1600:1900], rated_kw=5.0, backup_kw=0.0)
    checks.append(("energy conservation: heat pump season residual below 1e-6 kWh", abs(L.energy_residual(hp)) < 1e-6))
    checks.append(("energy conservation: heater season residual below 1e-6 kWh", abs(L.energy_residual(ht)) < 1e-6))
    checks.append(("energy conservation holds when the house cools (undersized, no backup)", abs(L.energy_residual(sag)) < 1e-6))

    # steady state against the hand calculation
    st = L.simulate(np.zeros(300), rated_kw=9.0)
    hand = 0.20 * 20.0 / (0.45 * 308.15 / 35.0 * 0.9)
    checks.append((f"worked example: steady state at 0 C: heat 0.20 x 20 = 4.00 kW, COP 3.962 x 0.9 = 3.566, electricity 1.122 kW (got {st['elec'][-1]:.4f})",
                   abs(st["elec"][-1] - hand) < 1e-4 and abs(st["elec"][-1] - L.steady_electric_kw(0.20, 20.0, 0.0, 35.0)) < 1e-9))
    st2 = L.simulate(np.full(300, 5.0), rated_kw=9.0, dt=0.5)
    checks.append(("steady state does not depend on the time step (dt = 0.5 h)", abs(st2["elec"][-1] / 0.5 - L.steady_electric_kw(0.20, 20.0, 5.0, 35.0)) < 1e-4))
    checks.append(("no heat is needed when it is as warm outside as the set point", L.simulate(np.full(24, 20.0))["elec_kwh"] < 1e-9))

    # machine model
    checks.append(("defrost derate: COP just below 2 C is 0.9 times the COP just above", abs(float(L.cop_hp(1.99, 35.0)) / float(L.cop_hp(2.0, 35.0)) - 0.9 * (35 - 2.0) / (35 - 1.99)) < 1e-9))
    checks.append(("capacity at the design temperature equals the sizing target (6 kW)", abs(float(L.capacity_kw(-10.0, rated)) - 6.0) < 1e-9))
    checks.append(("capacity never falls below 30 percent of rated", float(L.capacity_kw(-60.0, 10.0)) == 3.0))

    # season results
    checks.append(("a heater needs electricity equal to the heat it delivers", abs(ht["elec_kwh"] - ht["heat_kwh"]) < 1e-9))
    checks.append((f"heat pump seasonal COP is between 3 and 4.5 (got {hp['seasonal_cop']:.2f})", 3.0 < hp["seasonal_cop"] < 4.5))
    checks.append(("heat pump costs less than 30 percent of the heater", hp["cost"] < 0.30 * ht["cost"]))
    checks.append(("a properly sized heat pump holds the set point all winter", hp["min_t_in"] > 19.99))

    # sensitivity
    c = [L.simulate(T, ua=u, rated_kw=L.size_rated_kw(u, 20.0, -10.0))["cost"] for u in (0.12, 0.20, 0.30)]
    checks.append(("sensitivity: more heat loss (larger UA) costs more", c[0] < c[1] < c[2]))
    s = [L.simulate(T, t_sup=t, rated_kw=rated)["cost"] for t in (30.0, 35.0, 45.0, 55.0)]
    checks.append(("sensitivity: a higher supply temperature costs more", s[0] < s[1] < s[2] < s[3]))
    checks.append(("sensitivity: cost is proportional to the tariff", abs(hp["elec_kwh"] * 0.5 - L.simulate(T, rated_kw=rated, tariff=0.5)["cost"]) < 1e-9))

    # failure case: undersized pump on the coldest night
    i0 = int(T.argmin())
    sl = slice(i0 - 48, i0 + 24)
    small = L.simulate(T[sl], rated_kw=5.0, backup_kw=0.0)
    backed = L.simulate(T[sl], rated_kw=5.0, backup_kw=9.0)
    good = L.simulate(T[sl], rated_kw=rated, backup_kw=9.0)
    checks.append((f"failure: a 5 kW heat pump without backup lets the house fall below 15 C (got {small['min_t_in']:.1f})", small["min_t_in"] < 15.0))
    checks.append(("failure fixed by backup, at a cost: the backup holds 20 C but uses more electricity", backed["min_t_in"] > 19.99 and backed["elec_kwh"] > 1.4 * good["elec_kwh"]))

    # mini-project reference
    mp = L.simulate(T, ua=0.26, t_sup=45.0, rated_kw=8.5, backup_kw=6.0)
    mp_small = L.simulate(T, ua=0.26, t_sup=45.0, rated_kw=8.0, backup_kw=6.0)
    checks.append(("mini-project reference: 8.5 kW has backup share below 2 percent, 8.0 kW does not",
                   mp["backup_kwh"] / mp["heat_kwh"] < 0.02 < mp_small["backup_kwh"] / mp_small["heat_kwh"]))
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
