"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r = L.simulate(4.0, 3.0, 0.0)
    checks.append(("worked example: parabolic current peak 3 m/s, boat 4 m/s straight across: drift 30 m (= (2/3) 3 * 60 / 4) in 15 s",
                   abs(r["landing_x"] - 30.0) < 1e-3 and abs(r["time"] - 15.0) < 1e-3))
    r = L.simulate(4.0, 3.0, 0.5)
    checks.append(("adding a 0.5 m/s wind adds 0.5 * 15 = 7.5 m: 37.5 m", abs(r["landing_x"] - 37.5) < 1e-3))
    ru = L.simulate(4.0, 2.0, 0.0, profile="uniform")
    checks.append(("uniform current 2 m/s, straight heading: 30 m, as in Session 2", abs(ru["landing_x"] - 30.0) < 1e-3))
    ho = float(np.degrees(np.arcsin(2.0 / 4.0)))
    checks.append(("uniform current, heading 30 degrees: lands opposite, 17.32 s",
                   abs(L.simulate(4.0, 2.0, 0.0, heading0_deg=ho, profile="uniform")["landing_x"]) < 1e-3
                   and abs(L.simulate(4.0, 2.0, 0.0, heading0_deg=ho, profile="uniform")["time"] - 17.32) < 0.01))
    err = max(abs(L.simulate(4.0, 3.0, 0.5, heading0_deg=h)["landing_x"] - L.analytic_fixed(4.0, 3.0, 0.5, h)[0])
              for h in range(-40, 61, 10))
    checks.append(("simulation matches the exact fixed-heading formula to within 1 mm at 11 headings", err < 1e-3))
    e1 = abs(L.simulate(4.0, 3.0, 0.0, dt=0.5, method="euler")["landing_x"] - 30.0)
    e2 = abs(L.simulate(4.0, 3.0, 0.0, dt=0.25, method="euler")["landing_x"] - 30.0)
    checks.append(("Euler error shrinks when the time step is halved", e2 < e1))
    a = L.simulate(4.0, 3.0, 0.5, K=4.0, dt=0.05)["landing_x"]
    b = L.simulate(4.0, 3.0, 0.5, K=4.0, dt=0.0125)["landing_x"]
    checks.append(("feedback result changes by less than 0.1 m when dt is divided by 4", abs(a - b) < 0.1))
    naive = L.simulate(4.0, 3.0, 0.5, K=0.0)
    fb = L.simulate(4.0, 3.0, 0.5, K=4.0)
    checks.append(("feedback K = 4 lands within 2 m while the naive heading misses by 37.5 m",
                   abs(fb["landing_x"]) < 2.0 and abs(naive["landing_x"]) > 37.0))
    checks.append(("the price of correcting: the crossing takes longer (20.8 s against 15 s)",
                   fb["time"] > naive["time"] + 5.0 and abs(fb["time"] - 20.79) < 0.05))
    checks.append(("the heading never exceeds the 60 degree rudder limit", float(np.max(np.abs(fb["heading_deg"]))) <= 60.0 + 1e-9))
    # sensitivity
    d2 = L.simulate(4.0, 2.0, 0.0)["landing_x"]
    d3 = L.simulate(4.0, 3.0, 0.0)["landing_x"]
    checks.append(("sensitivity: the naive drift grows 10 m for every extra 1 m/s of peak current", abs((d3 - d2) - 10.0) < 1e-3))
    # edge: nothing pushes the boat
    z = L.simulate(4.0, 0.0, 0.0, K=4.0)
    checks.append(("no current and no wind: feedback keeps the boat on the line (lands at 0)", abs(z["landing_x"]) < 1e-9))
    # failure case: current faster than the boat
    best = L.best_possible_drift(4.0, 5.0)
    s1 = L.simulate(4.0, 5.0, 0.0, profile="uniform")["landing_x"]
    s2 = L.simulate(4.0, 5.0, 0.0, K=4.0, profile="uniform")["landing_x"]
    s3 = L.simulate(4.0, 5.0, 0.0, heading0_deg=float(np.degrees(np.arcsin(4.0 / 5.0))), profile="uniform")["landing_x"]
    checks.append(("failure case: uniform current 5 m/s > boat 4 m/s: best drift is 45 m and no run beats it",
                   abs(best - 45.0) < 1e-9 and abs(s3 - 45.0) < 1e-3 and s1 >= 45.0 and s2 >= 45.0 - 1e-6))
    checks.append(("failure case: for current < boat speed the best drift is 0", L.best_possible_drift(4.0, 3.9) == 0.0))
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
