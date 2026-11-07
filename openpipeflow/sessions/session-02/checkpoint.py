"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    q, d, length, e, k = 0.020, 0.125, 500.0, 0.00015, 5.0
    v = L.velocity(q, d)
    re = L.reynolds(q, d)
    f = L.friction_factor(re, e / d)
    checks.append(("worked example: 20 L/s in 125 mm: v = 1.630 m/s, Re = 203700",
                   abs(v - 1.6297) < 1e-3 and abs(re - 203718) < 10))
    checks.append(("worked example: f = 0.0219, friction loss 11.87 m, minor loss 0.68 m",
                   abs(f - 0.0219) < 5e-5 and abs(f * length / d * v ** 2 / 19.62 - 11.87) < 0.02
                   and abs(k * v ** 2 / 19.62 - 0.68) < 0.01))
    h = L.pump_head(q, d, length, e, 10.0, k)
    p = L.pump_power(q, d, length, e, 10.0, k, 0.65)
    checks.append((f"worked example: head 22.55 m, water power 4.42 kW, electric 6.79 kW (got {p / 1e3:.2f})",
                   abs(h - 22.55) < 0.01 and abs(998 * 9.81 * q * h - 4415) < 5 and abs(p - 6793) < 5))
    checks.append(("design: smallest standard size within 7 kW is 125 mm",
                   L.smallest_diameter(7000.0, q, length, e, 10.0, k, 0.65) == 125))
    checks.append(("design: 100 mm needs more than 14 kW", L.pump_power(q, 0.100, length, e, 10.0, k) > 14000))
    checks.append(("an impossible budget returns None", L.smallest_diameter(100.0, q, length, e, 10.0, k) is None))

    # hand calculation, laminar: Hagen-Poiseuille h = 128 nu L Q / (pi g D^4)
    ql, dl = 2e-5, 0.025
    hp = 128 * L.NU * 10.0 * ql / (math.pi * L.G * dl ** 4)
    checks.append(("laminar flow (Re = 1019): f = 64/Re and loss equals Hagen-Poiseuille",
                   L.reynolds(ql, dl) < 2000 and abs(L.head_loss(ql, dl, 10.0, 0.0) - hp) < 1e-9))

    # Swamee-Jain against the Colebrook reference
    worst = 0.0
    for re_ in (5e3, 2e4, 1e5, 1e6, 1e7):
        for rr in (1e-5, 1e-4, 1e-3, 1e-2):
            worst = max(worst, abs(L.friction_factor(re_, rr) / L.colebrook(re_, rr) - 1))
    checks.append((f"Swamee-Jain is within 3% of Colebrook for Re 5000-1e7 (worst {100 * worst:.1f}%)", worst < 0.03))

    # limits: continuity at the regime joins, scaling laws
    j1 = abs(L.friction_factor(1999.999, 1e-3) - L.friction_factor(2000.001, 1e-3))
    j2 = abs(L.friction_factor(3999.999, 1e-3) - L.friction_factor(4000.001, 1e-3))
    checks.append(("friction factor is continuous at Re = 2000 and 4000", j1 < 1e-4 and j2 < 1e-4))
    a = L.head_loss(0.010, 0.1, 100.0, 0.0001)
    b = L.head_loss(0.020, 0.1, 100.0, 0.0001)
    checks.append(("doubling the flow roughly quadruples the loss (3.7 to 4.1 times)", 3.7 < b / a < 4.1))
    checks.append(("smoother pipe gives less loss", L.head_loss(q, d, length, 0.0) < L.head_loss(q, d, length, 0.001)))
    checks.append(("zero length and zero K give zero loss", L.head_loss(q, d, 0.0, e, 0.0) == 0.0))
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
