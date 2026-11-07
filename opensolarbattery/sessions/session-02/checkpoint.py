"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # worked example: one charging hour then one discharging hour, eta = 0.81 so each way is 0.9
    r = L.run_day(np.array([3.0, 0.0]), np.array([1.0, 1.62]), cap_kwh=10.0, p_max_kw=5.0, eta=0.81, soc0=0.0)
    checks.append((f"worked example: 2 kW surplus stores 1.8 kWh (got {r['soc'][0]:.3f})", abs(r["soc"][0] - 1.8) < 1e-9))
    checks.append(("worked example: 1.62 kW drawn for an hour empties the battery, no import",
                   abs(r["soc"][1]) < 1e-9 and abs(r["imp"][1]) < 1e-9 and abs(r["discharge"][1] - 1.62) < 1e-9))
    checks.append(("round trip: 2 kWh in, 2 x 0.81 = 1.62 kWh out", abs(r["discharge"].sum() / r["charge"].sum() - 0.81) < 1e-9))

    # limits
    r2 = L.run_day(np.array([10.0]), np.array([0.0]), cap_kwh=3.0, p_max_kw=2.0, eta=1.0, soc0=0.0)
    checks.append(("charging is limited by the power limit (2 kW) and exports the rest", abs(r2["charge"][0] - 2.0) < 1e-9 and abs(r2["exp"][0] - 8.0) < 1e-9))
    r3 = L.run_day(np.array([0.0]), np.array([4.0]), cap_kwh=3.0, p_max_kw=10.0, eta=1.0, soc0=1.5)
    checks.append(("discharge is limited by the stored energy (1.5 kWh), the rest is imported", abs(r3["discharge"][0] - 1.5) < 1e-9 and abs(r3["imp"][0] - 2.5) < 1e-9))

    # state of charge always inside [0, capacity]
    sim = L.simulate(3.0, 10.0, 6.0, 3.0, 0.9, 0.5)
    checks.append(("state of charge stays between 0 and the capacity", bool(sim["soc"].min() >= -1e-12 and sim["soc"].max() <= 6.0 + 1e-12)))
    checks.append((f"energy conservation residual is zero (got {L.conservation_residual(sim, 0.9):.2e} kWh)", abs(L.conservation_residual(sim, 0.9)) < 1e-9))
    checks.append(("a steady day: the battery ends the day where it started", abs(sim["soc_final"] - sim["soc_start"]) < 1e-6))

    # edge case: no battery, no array
    nb = L.summary(L.simulate(0.0, 10.0, 0.0, 0.0, 0.9, 1.0))
    checks.append(("edge case: no array and no battery imports all the demand", abs(nb["self_sufficiency"]) < 1e-12 and abs(nb["import_kwh"] - 10.0) < 1e-9))
    s0 = L.summary(L.simulate(3.0, 10.0, 0.0, 0.0, 0.9, 0.5))["self_sufficiency"]
    s6 = L.summary(sim)["self_sufficiency"]
    checks.append(("adding a battery raises self-sufficiency", s6 > s0 + 0.3))
    imps = [L.summary(L.simulate(3.0, 10.0, 6.0, 3.0, e, 0.5))["import_kwh"] for e in (1.0, 0.9, 0.8)]
    checks.append(("lower round-trip efficiency means more grid import", imps[0] < imps[1] < imps[2]))

    # hand-calculated design problem
    best = L.cheapest_design(0.9)
    checks.append((f"worked example: cheapest 90 percent design is 3 kW and 6 kWh, cost 5400 (got {best[1]} kW, {best[2]} kWh, {best[0]:.0f})",
                   best[1] == 3.0 and best[2] == 6.0 and abs(best[0] - 5400.0) < 1e-6))
    checks.append(("illustrative cost = 1000 x 3 + 400 x 6 = 5400", abs(L.cost(3.0, 6.0) - 5400.0) < 1e-9))
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
