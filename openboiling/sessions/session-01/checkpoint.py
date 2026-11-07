"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    tb = L.time_to_boil(2000.0, 1.0)
    checks.append(("worked example: 1 kg at 2000 W reaches 100 C after 197 s", abs(tb - 197.0) < 0.5))
    temp, boiled = L.heating_state(tb + 300.0, 2000.0, 1.0)
    checks.append(("worked example: after 5 more minutes the water is still 100 C and 226 g has boiled away",
                   abs(temp - 100.0) < 1e-9 and abs(boiled - 0.226) < 0.001))
    checks.append(("hand calculation: m cp dT = 1 * 4186 * 80 = 334880 J", abs(L.CP * 1.0 * 80.0 - 334880.0) < 1e-6))
    t0, b0 = L.heating_state(0.0, 2000.0, 1.0)
    checks.append(("at time zero: 20 C and nothing boiled", abs(t0 - 20.0) < 1e-12 and b0 == 0.0))
    t1, b1 = L.heating_state(tb, 2000.0, 1.0)
    checks.append(("exactly at the boiling time nothing has boiled yet", abs(t1 - 100.0) < 1e-9 and b1 == 0.0))
    t_big, _ = L.heating_state(100000.0, 2000.0, 1.0)
    checks.append(("temperature never exceeds 100 C", t_big <= 100.0))
    checks.append(("doubling the power halves the time to boil", abs(L.time_to_boil(4000.0, 1.0) - tb / 2) < 1e-9))
    # energy conservation: energy in = sensible heat + latent heat
    tt = tb + 123.0
    temp, boiled = L.heating_state(tt, 1500.0, 2.0)
    e_in = L.EFF * 1500.0 * tt
    e_used = 2.0 * L.CP * (temp - 20.0) + boiled * L.LATENT
    checks.append(("energy in equals warming plus vaporising", abs(e_in - e_used) < 1e-6 * e_in))
    names = [L.stage_name(d) for d in (2.0, 10.0, 60.0, 200.0)]
    checks.append(("four stages in order of increasing superheat",
                   names == ["natural convection", "nucleate boiling", "transition boiling", "film boiling"]))
    q = L.flux_curve(np.array([2.0, 10.0, 30.0, 60.0, 120.0, 200.0]))
    checks.append(("the flux peaks at 30 K at about 1.1 MW/m2", np.argmax(q) == 2 and abs(q[2] - 1.1e6) < 1e3))
    checks.append(("flux falls after the peak down to the minimum, then rises", q[3] < q[2] and q[4] < q[3] and q[5] > q[4]))
    checks.append(("zero superheat gives zero flux", abs(float(L.flux_curve(0.0))) < 1e-12))
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
