"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    res = L.launch()
    el, b = res["orbit"], res["budget"]
    v_end = np.hypot(res["vx"][-1], res["vy"][-1])
    checks.append((f"worked example: kick 3 degrees reaches orbit, perigee {el['hp'] / 1e3:.1f} km, apogee {el['ha'] / 1e3:.1f} km",
                   res["status"] == "orbit" and 190e3 < el["hp"] < 210e3 and el["ha"] < 220e3))
    checks.append(("worked example: nearly circular orbit (e below 0.002)", el["e"] < 0.002))
    checks.append(("worked example: staging at t = 160 s near 75 km and 3.2 km/s",
                   abs(res["events"][0][1] - 160.0) < 0.5 and abs(res["events"][0][2] - 74.8e3) < 2e3
                   and abs(res["events"][0][3] - 3195) < 30))
    checks.append(("hand calculation: stage 1 burn time = 90 t / (1.6 MN / (290 g0)) = 160.0 s",
                   abs(90000.0 / (1.6e6 / (290 * 9.80665)) - res["events"][0][1]) < 0.01))
    checks.append(("delta-v budget closes: ideal - gravity - drag - steering = final speed (within 1 m/s)",
                   abs(b[0] - b[1] - b[2] - b[3] - v_end) < 1.0))
    burnt = [L.LAUNCHER[0]["prop"], L.LAUNCHER[1]["prop"] - res["prop_left"]]
    checks.append(("the ideal term equals the Session 1 rocket equation for the propellant used (within 1 m/s)",
                   abs(L.rocket_equation_dv(L.LAUNCHER, L.PAYLOAD, burnt) - b[0]) < 1.0))
    checks.append((f"the losses are realistic: gravity {b[1]:.0f}, drag {b[2]:.0f}, steering {b[3]:.0f} m/s",
                   1000 < b[1] < 2000 and 20 < b[2] < 300 and b[3] < 800))
    checks.append(("cut-off at the energy of a 200 km circular orbit", abs(el["a"] - (L.R_EARTH + 200e3)) < 2e3))
    xs, ys, vxs, vys = L.coast(res["x"][-1], res["y"][-1], res["vx"][-1], res["vy"][-1], 3000.0)
    eps = 0.5 * (vxs ** 2 + vys ** 2) - L.MU / np.hypot(xs, ys)
    checks.append(("energy is conserved in a 3000 s coast (relative drift below 1e-9)",
                   abs(eps[-1] - eps[0]) / abs(eps[0]) < 1e-9))
    checks.append(("the coast stays above 190 km (it really is an orbit)", np.hypot(xs, ys).min() - L.R_EARTH > 190e3))
    vac = L.launch(gravity=False, drag=False, kick=0.0, cutoff=False, upper="prograde")
    vac_v = np.hypot(vac["vx"][-1], vac["vy"][-1])
    total = L.rocket_equation_dv(L.LAUNCHER, L.PAYLOAD)
    checks.append((f"limit: no gravity and no air, the full burn gives the rocket equation ({vac_v:.0f} m/s)",
                   abs(vac_v - total) < 1.0))
    checks.append(("no pitch kick: the rocket goes up and falls back", L.launch(kick=0.0)["status"] != "orbit"))
    checks.append(("keeping the empty first stage fails to reach orbit", L.launch(drop_stages=False)["status"] != "orbit"))
    scan = {k: s for k, s, hp, left in L.kick_scan([1.0, 2.0, 3.0, 4.0, 5.0])}
    checks.append(("pitch-kick window: 1 and 5 degrees fail, 2 to 4 degrees reach orbit",
                   scan[1.0] != "orbit" and scan[5.0] != "orbit" and all(scan[k] == "orbit" for k in (2.0, 3.0, 4.0))))
    fine = L.launch(dt=0.1)
    checks.append(("a smaller time step gives the same orbit (perigee within 10 km)", abs(fine["orbit"]["hp"] - el["hp"]) < 10e3))
    checks.append(("max dynamic pressure is between 20 and 50 kPa, in the lower atmosphere",
                   20e3 < res["max_q"] < 50e3 and 50 < res["max_q_time"] < 100))
    pmax, kbest = L.max_payload(start=1750.0)
    checks.append((f"mini-project: 2000 kg reaches orbit, 2250 kg does not (found {pmax} kg)", pmax == 2000.0))
    bad = 0
    for call in (lambda: L.launch(payload=-1), lambda: L.launch(dt=0), lambda: L.launch(kick=-2)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
