"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d = 31.5
    sc = L.plan(d, 2.5, 1.0, 1.5)
    tr = L.plan(d, 2.5, 1.0)
    checks.append(("hand calculation: S-curve T = d/v + v/a + a/j = 12.6 + 2.5 + 0.667 = 15.77 s",
                   abs(sc["T"] - (d / 2.5 + 2.5 / 1.0 + 1.0 / 1.5)) < 1e-9 and abs(sc["T"] - 15.767) < 0.001))
    checks.append(("hand calculation: trapezoid T = d/v + v/a = 12.6 + 2.5 = 15.10 s", abs(tr["T"] - 15.1) < 1e-9))
    t, a, v, x = L.reference(sc)
    checks.append(("the planned S-curve ends at 31.5 m with zero speed", abs(x[-1] - d) < 0.02 and abs(v[-1]) < 0.005))
    r = L.simulate(d, 400.0, sc)
    checks.append(("worked example: the simulated half-load ride takes 15.77 s, within 0.02 s of the formula",
                   abs(r["time"] - sc["T"]) < 0.02))
    drawn, back, net, work = L.energies(r)
    ideal = (1000.0 + 400.0 - 1360.0) * L.G * d
    checks.append(("worked example: mechanical work equals the potential-energy change, 40 kg * g * 31.5 m = 12.4 kJ",
                   abs(ideal / 1000 - 12.36) < 0.01 and abs(work - ideal) < 0.01 * abs(ideal) + 20.0))
    r_down = L.simulate(-d, 800.0, sc)
    drawn_d, back_d, net_d, work_d = L.energies(r_down)
    ideal_down = (1000.0 + 800.0 - 1360.0) * L.G * d
    checks.append(("energy balance, heavy car going down: work is -136.0 kJ and the grid draws nothing",
                   abs(work_d + ideal_down) < 0.01 * ideal_down and drawn_d < 1.0))
    checks.append(("regeneration: the energy fed back is eta * 136.0 kJ = 115.6 kJ",
                   abs(back_d - 0.85 * ideal_down) < 0.01 * ideal_down))
    r_bal = L.simulate(d, 360.0, sc)
    checks.append(("balanced car (load 360 kg): the net mechanical work is about zero",
                   abs(L.energies(r_bal)[3]) < 0.01 * ideal_down))
    checks.append(("S-curve is comfortable (score < 1): peak a about 1.04 m/s^2, peak jerk about 2.1 m/s^3",
                   L.comfort_score(r["peak_a"], r["peak_jerk"]) < 1.0 and r["peak_a"] < 1.1))
    r_tr = L.simulate(d, 400.0, tr)
    checks.append(("trapezoid is not comfortable: peak jerk more than 10 times the S-curve's",
                   L.comfort_score(r_tr["peak_a"], r_tr["peak_jerk"]) > 1.0 and r_tr["peak_jerk"] > 10 * r["peak_jerk"]))
    checks.append(("trapezoid is faster by about 0.67 s",
                   abs((r["time"] - r_tr["time"]) - (sc["T"] - tr["T"])) < 0.02))
    weak = L.simulate(d, 800.0, sc, 6000.0)
    checks.append(("torque limit: with F_max = 6000 N the full-load ride saturates and is uncomfortable",
                   weak["saturated"] and L.comfort_score(weak["peak_a"], weak["peak_jerk"]) > 1.0))
    ok_motor = L.simulate(d, 800.0, sc, 8000.0)
    checks.append(("torque limit: with F_max = 8000 N the same ride follows the plan",
                   (not ok_motor["saturated"]) and abs(ok_motor["time"] - sc["T"]) < 0.02))
    # mini-project: smallest force limit from the list that passes both worst-case rides
    passing = []
    for Fm in (6000.0, 7000.0, 7500.0, 8000.0, 9000.0):
        good = True
        for sgn, ml in ((1, 800.0), (-1, 0.0)):
            rr = L.simulate(sgn * d, ml, sc, Fm)
            good &= ((not rr["saturated"]) and L.comfort_score(rr["peak_a"], rr["peak_jerk"]) < 1.0
                     and abs(rr["time"] - sc["T"]) < 0.02)
        if good:
            passing.append(Fm)
    checks.append(("mini-project: the smallest passing force limit in the list is 7500 N", passing[:1] == [7500.0]))
    tab = L.sensitivity([0.0, 400.0, 800.0], [1000.0, 1360.0], d, sc)
    checks.append(("sensitivity: more load means more energy going up, for both counterweights",
                   bool(np.all(np.diff(tab, axis=1) > 0))))
    checks.append(("sensitivity: with the lighter counterweight, a full-load ride up costs more energy",
                   tab[0, 2] > tab[1, 2]))
    ps = L.plan(0.5, 2.5, 1.0, 1.5)
    checks.append(("edge: a 0.5 m ride has finite time and the cruise speed is reduced",
                   bool(np.isfinite(ps["T"])) and ps["v"] < 2.5))
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
