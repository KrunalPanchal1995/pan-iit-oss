"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("osmotic constant at 25 C is 84.83 kPa per g/L (Session 1 law)", abs(L.K_PI - 84.833) < 1e-2))
    checks.append(("no water flows when the push is below the osmotic pressure",
                   L.water_flux(2000.0, 35.0) == 0.0 and L.water_flux(L.osmotic(35.0), 35.0) == 0.0))
    checks.append(("hand calculation: flux at 6000 kPa and 35 g/L is 1e-5 x 3031 = 0.0303 m3/(m2 h)",
                   abs(L.water_flux(6000.0, 35.0) - 1e-5 * (6000.0 - 2969.15)) < 1e-6))

    a = L.area_needed(6000.0, 0.30)
    checks.append((f"worked example: closed form needs {a:.1f} m2 for 30 percent recovery at 6000 kPa (hand 149.2)",
                   abs(a - 149.19) < 0.05))
    res = L.simulate_module(6000.0, b_s=0.0, area=a)
    checks.append(("validation: RK4 march over that area gives 30 percent recovery (within 1e-6)",
                   abs(res["recovery"] - 0.30) < 1e-6))
    checks.append(("worked example: brine is 35 / 0.7 = 50 g/L with no salt leak", abs(res["c_brine"] - 50.0) < 1e-6))
    sec = L.specific_energy(res, 0.8, 0.95)
    checks.append((f"worked example: SEC with pump 0.8 and ERD 0.95 is {sec:.3f} kWh/m3 (hand 3.25)", abs(sec - 3.25) < 1e-6))
    checks.append(("ideal pump and perfect ERD: SEC = P / 3600 = 1.667 kWh/m3",
                   abs(L.specific_energy(res, 1.0, 1.0) - 6000.0 / 3600.0) < 1e-12))

    r1 = L.simulate_module(6000.0, cp=1.1)
    checks.append(("salt balance: salt in = salt out in brine + permeate (within 1e-9 relative)",
                   abs(r1["salt_out"] - r1["salt_in"]) / r1["salt_in"] < 1e-9))
    checks.append(("water balance: feed = permeate + brine", abs(r1["q"][-1] + r1["q_perm"] - L.Q_FEED) < 1e-12))
    checks.append(("convergence: 50 and 800 steps agree within 1e-6 in recovery",
                   abs(L.simulate_module(6000.0, cp=1.1, n=50)["recovery"] - L.simulate_module(6000.0, cp=1.1, n=800)["recovery"]) < 1e-6))
    checks.append(("flux falls along the membrane as the feed gets saltier", bool(np.all(np.diff(r1["flux"]) < 0))))
    big = L.simulate_module(6000.0, b_s=0.0, area=20000.0)
    checks.append(("limit: a huge membrane approaches but never passes recovery 1 - pi_f / P = 0.505",
                   big["recovery"] < L.recovery_limit(6000.0) and L.recovery_limit(6000.0) - big["recovery"] < 0.01))
    secs = [L.specific_energy(L.simulate_module(6000.0, b_s=0.0, area=x), 1.0, 1.0) for x in (100, 400, 1600, 6400)]
    least = [L.least_work(35.0, L.simulate_module(6000.0, b_s=0.0, area=x)["recovery"]) for x in (100, 400, 1600, 6400)]
    checks.append(("second law: the simulated SEC is always above the Session 2 least work", all(s > w for s, w in zip(secs, least))))
    checks.append(("concentration polarisation costs water: CP = 1.2 gives less than CP = 1",
                   L.simulate_module(6000.0, cp=1.2)["recovery"] < L.simulate_module(6000.0, cp=1.0)["recovery"]))
    checks.append(("a leakier membrane (larger B) gives saltier fresh water",
                   L.simulate_module(6000.0, b_s=2e-4)["c_perm"] > L.simulate_module(6000.0, b_s=5e-5)["c_perm"]))
    checks.append(("losing the ERD costs a lot of energy",
                   L.specific_energy(r1, 0.8, 0.0) > 1.5 * L.specific_energy(r1, 0.8, 0.95)))

    best = L.choose_pressure()
    checks.append((f"mini-project: seawater 35 g/L needs P = {best[0]:.0f} kPa, recovery {best[1]['recovery']:.3f}, "
                   f"SEC {best[2]:.2f} kWh/m3", best[0] == 6750.0 and best[1]["recovery"] >= 0.45 and abs(best[2] - 3.02) < 0.01))
    checks.append(("mini-project: permeate below 500 mg/L of salt", best[1]["c_perm"] <= 0.5))
    checks.append(("mini-project: Gulf water 45 g/L cannot reach 45 percent recovery below 6900 kPa",
                   L.choose_pressure(45.0) is None))
    bad = 0
    for call in (lambda: L.simulate_module(-1.0), lambda: L.simulate_module(6000.0, cp=0.9),
                 lambda: L.area_needed(6000.0, 0.6), lambda: L.specific_energy(r1, 0.0, 0.9)):
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
