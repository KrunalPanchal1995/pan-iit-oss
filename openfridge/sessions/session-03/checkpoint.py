"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r = L.cycle(-8, 35, 0.7)
    # worked example, recomputed by hand-style arithmetic with the toy numbers
    h1 = 0.8 * -8 + 300.0                      # 293.6 kJ/kg
    h3 = 0.8 * 35                               # 28.0 kJ/kg
    t2s = 265.15 * (L.psat_bar(35) / L.psat_bar(-8)) ** (0.10 / 0.8)
    w = 0.8 * (t2s - 265.15) / 0.7
    cop = (h1 - h3) / w
    checks.append((f"worked example: q_evap = 293.6 - 28.0 = 265.6 kJ/kg (got {r['q_evap']:.1f})", abs(r["q_evap"] - 265.6) < 1e-9))
    checks.append((f"worked example: work = 66.1 kJ/kg (got {r['work']:.1f})", abs(r["work"] - w) < 1e-9 and abs(r["work"] - 66.11) < 0.01))
    checks.append((f"worked example: COP = 265.6 / 66.1 = 4.02 (got {r['cop']:.2f})", abs(r["cop"] - cop) < 1e-9 and abs(r["cop"] - 4.02) < 0.005))
    checks.append(("energy balance: q_cond = q_evap + work", abs(r["q_cond"] - r["q_evap"] - r["work"]) < 1e-9))
    checks.append(("throttling keeps enthalpy: h4 = h3 and quality between 0 and 1", r["h4"] == r["h3"] and 0 < r["quality4"] < 1))
    checks.append(("pressures: 2.9 bar at 0 C, rising with temperature", abs(L.psat_bar(0) - 2.9) < 1e-12 and L.psat_bar(35) > L.psat_bar(0) > L.psat_bar(-8)))
    checks.append(("compressor exit is superheated (hotter than the condenser)", r["t2s"] > 35 and r["t2"] > r["t2s"]))

    # validation 1: the ideal compression is isentropic (entropy of state 2s equals state 1)
    te, tc = -8 + 273.15, 35 + 273.15
    s1 = 0.8 * np.log(te / 273.15) + 300.0 / te
    s2s = 0.8 * np.log(tc / 273.15) + 300.0 / tc + 0.8 * np.log((r["t2s"] + 273.15) / tc)
    checks.append(("validation: entropy at 2s equals entropy at state 1", abs(s1 - s2s) < 1e-9))

    # validation 2: never better than Carnot between the cycle temperatures, and entropy is generated
    ok_bound, ok_s = True, True
    for te_c in (-30, -15, -8, 0):
        for tc_c in (25, 35, 50):
            for eta in (1.0, 0.7, 0.4):
                c = L.cycle(te_c, tc_c, eta)
                ok_bound &= c["cop"] <= (te_c + 273.15) / (tc_c - te_c) + 1e-12
    for ti in (-18, 0, 4, 8):
        for tr in (15, 25, 40):
            ok_s &= L.fridge(ti, tr, 1.0)["s_gen"] > 0
    checks.append(("validation: cycle COP never exceeds Carnot between its own temperatures", bool(ok_bound)))
    checks.append(("validation: entropy generated is positive for every whole-fridge case", bool(ok_s)))
    f = L.fridge(4, 25, 0.7)
    checks.append((f"whole fridge 4 C / 25 C: eta2 = COP / Carnot is between 0.2 and 0.5 (got {f['eta2']:.2f})", 0.2 < f["eta2"] < 0.5))

    # sensitivity
    cops = [L.cycle(-8, t, 0.7)["cop"] for t in (25, 30, 35, 40, 45)]
    checks.append(("COP falls as the condenser gets hotter", all(a > b for a, b in zip(cops, cops[1:]))))
    checks.append(("COP rises with compressor efficiency", L.cycle(-8, 35, 0.9)["cop"] > L.cycle(-8, 35, 0.5)["cop"]))
    checks.append(("COP is proportional to eta_c", abs(L.cycle(-8, 35, 0.5)["cop"] / 0.5 - L.cycle(-8, 35, 1.0)["cop"]) < 1e-9))

    # door load and bill, hand calculations
    d = L.door_load_w(30, 25, 4)
    checks.append((f"hand calculation: 30 openings per day at 25 C / 4 C add 1.32 W (got {d:.2f})", abs(d - 1.2 * 1.006 * 0.15 * 21 * 1000 * 30 / 86400) < 1e-9 and abs(d - 1.32) < 0.005))
    checks.append(("no door openings means no door load", L.door_load_w(0, 25, 4) == 0.0))
    y = L.fridge_year(28)
    checks.append((f"mini-project: at 28 C the duty is 0.49 and the year costs about 198 kWh (got {y['duty']:.2f}, {y['kwh']:.0f})", abs(y["duty"] - 0.49) < 0.005 and abs(y["kwh"] - 198) < 1))
    checks.append(("a hotter room means a higher bill", L.fridge_year(34)["kwh"] > L.fridge_year(28)["kwh"] > L.fridge_year(22)["kwh"]))
    checks.append(("door openings matter less than the room: 80 openings add under 10 kWh per year", L.fridge_year(28, 80)["kwh"] - L.fridge_year(28, 0)["kwh"] < 10))
    hot = max(t for t in range(15, 46) if L.fridge_year(t)["duty"] <= 0.6)
    checks.append((f"design: warmest whole-degree room with duty <= 0.6 is 33 C (got {hot})", hot == 33))
    bad = L.fridge_year(40, 80, capacity_w=100.0)
    checks.append(("failure case: load above capacity cannot hold the temperature", bad["duty"] > 1 and not bad["holds_temperature"]))
    for fn, label in ((lambda: L.cycle(30, 30), "condenser as cold as evaporator"), (lambda: L.cycle(-8, 35, 0.0), "eta_c = 0"),
                      (lambda: L.cycle(-8, 35, 1.5), "eta_c above 1")):
        try:
            fn()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
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
