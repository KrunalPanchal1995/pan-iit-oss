"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    s = L.solve()
    q = s["Q"]
    checks.append(("worked example: hand calculation of the main pipe, 30 L/s in 200 mm over 1200 m, loses 5.64 m",
                   abs(L.head_loss(0.030, 0.20, 1200.0, 0.00015) - 5.636) < 0.005 and abs(s["h"][1] - 5.636) < 0.005))
    checks.append(("worked example: pressure head at A is 70 - 5.64 - 20 = 44.36 m",
                   abs(s["pressure_head"]["A"] - 44.36) < 0.01))
    checks.append(("worked example: flows 16.17, 13.83 and -1.83 L/s in pipes 2, 3, 4",
                   abs(q[2] * 1000 - 16.17) < 0.01 and abs(q[3] * 1000 - 13.83) < 0.01 and abs(q[4] * 1000 + 1.83) < 0.01))
    checks.append(("worst pressure head is 30.07 m, at node C", abs(min(s["pressure_head"].values()) - 30.07) < 0.01
                   and min(s["pressure_head"], key=s["pressure_head"].get) == "C"))

    # validation 1: single pipe against the Session 2 formula
    a, b = L.single_pipe_check()
    checks.append(("single pipe: network way equals the Session 2 formula", abs(a - b) < 1e-12))
    # validation 2: mass conservation at every node, loop energy closure
    bal = L.node_balance(s)
    checks.append(("mass conservation: net flow at every node is zero (< 1e-12 m3/s)", max(abs(v) for v in bal.values()) < 1e-12))
    checks.append(("energy: head losses around the loop cancel (< 1e-6 m)", abs(L.loop_closure(s)) < 1e-6))
    # validation 3: symmetry, and Hardy Cross converges quickly
    sym = {i: {"L": 500.0, "D": 0.1} for i in (1, 2, 3, 4)}
    x, _ = L.hardy_cross(sym, 0.01, 0.01, 0.00015)
    checks.append(("symmetry: identical pipes and equal demands give no flow in the cross pipe", abs(x) < 1e-12))
    checks.append(("Hardy Cross converges in 10 iterations or fewer", s["iterations"] <= 10))
    # validation 4: laminar analytic result (Hagen-Poiseuille), with a very viscous liquid
    nu, qq, d, length = 1e-4, 1e-5, 0.02, 5.0
    hp = 128 * nu * length * qq / (math.pi * L.G * d ** 4)
    checks.append(("laminar analytic: head_loss equals Hagen-Poiseuille", abs(L.head_loss(qq, d, length, 0.0, nu) - hp) < 1e-9))

    # sensitivity directions and sizes
    sens = L.sensitivity({"total_lps": 40.0})
    checks.append(("sensitivity: rough pipes, then cold water, lower the worst pressure; warm water raises it",
                   sens["rough x2"] < sens["base"] and sens["cold water (nu 1.31e-6)"] < sens["base"]
                   and sens["warm water (nu 0.66e-6)"] > sens["base"]))
    checks.append(("sensitivity: doubling roughness costs more than 3 m at 40 L/s, viscosity changes under 1 m",
                   sens["base"] - sens["rough x2"] > 3.0 and abs(sens["base"] - sens["cold water (nu 1.31e-6)"]) < 1.0))

    # failure / limit cases
    checks.append(("failure: 50 L/s drops node C below the 20 m target with these pipes",
                   L.min_pressure_head(total_lps=50.0) < 20.0))
    checks.append(("failure: 80 L/s gives negative pressure (the model would need air to enter)",
                   L.min_pressure_head(total_lps=80.0) < 0.0))
    checks.append(("a bigger main pipe restores the pressure at 50 L/s (220 mm main, 150 mm branches)",
                   L.min_pressure_head(d_main=0.22, d_branch=0.15, total_lps=50.0) > 20.0))
    zero = L.solve(total_lps=1e-6)
    checks.append(("limit: almost no demand gives almost no head loss", abs(zero["pressure_head"]["A"] - 50.0) < 1e-3))

    # mini-project tool
    p150 = L.pipe_run_power(0.015, 0.150, 900.0, 0.00015, 45.0, 3.0, 0.65)
    p125 = L.pipe_run_power(0.015, 0.125, 900.0, 0.00015, 45.0, 3.0, 0.65)
    checks.append((f"mini-project: 150 mm needs {p150 / 1e3:.2f} kW (within 12 kW), 125 mm needs {p125 / 1e3:.2f} kW (over)",
                   p150 < 12000.0 < p125))
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
