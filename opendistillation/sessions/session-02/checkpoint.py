"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("Antoine gives the normal boiling points: ethanol 78.3 C, water 100.0 C",
                   abs(L.boiling_point("ethanol") - 78.32) < 0.05 and abs(L.boiling_point("water") - 100.0) < 0.05))
    checks.append(("water vapour pressure at 100 C is 760 mmHg (within 1 mmHg)", abs(float(L.psat(100.0, "water")) - 760.0) < 1.0))
    t, y = L.bubble_point(0.10)
    g1, g2 = L.activity(0.10)
    total = 0.10 * g1 * L.psat(t, "ethanol") + 0.90 * g2 * L.psat(t, "water")
    checks.append((f"worked example: x = 0.10 boils at {t:.2f} C (86.6 C) and the partial pressures add to 760 mmHg",
                   abs(t - 86.59) < 0.05 and abs(total - 760.0) < 1e-6))
    hand_y = 0.10 * 3.197 * 1046.4 / 760.0
    checks.append((f"worked example: y = 0.10 x 3.197 x 1046.4 / 760 = {hand_y:.3f}", abs(y - hand_y) < 2e-3))
    checks.append(("hand calculation: van Laar gamma for x = 0.10 is 3.197 (ethanol) and 1.027 (water)",
                   abs(g1 - 3.197) < 2e-3 and abs(g2 - 1.0265) < 2e-3))
    checks.append(("limit: gamma -> 1 for a pure component", abs(float(L.activity(1.0)[0]) - 1) < 1e-12 and abs(float(L.activity(0.0)[1]) - 1) < 1e-12))
    checks.append(("limit: van Laar constants of zero give Raoult's law (gamma = 1)",
                   np.allclose(L.activity(np.linspace(0.05, 0.95, 10), 0.0, 0.0), 1.0)))
    checks.append(("pure liquids: bubble point of x = 0 and x = 1 are the boiling points",
                   abs(L.bubble_point(0.0)[0] - L.boiling_point("water")) < 1e-6 and abs(L.bubble_point(1.0)[0] - L.boiling_point("ethanol")) < 1e-6))
    xs, ys, ts = L.equilibrium_curve(101)
    az = L.azeotrope()
    below = xs <= az[0]
    checks.append(("bubble temperature falls as ethanol is added, up to the azeotrope, and is lowest there",
                   bool(np.all(np.diff(ts[below]) < 1e-9)) and ts.min() >= az[1] - 1e-6))
    checks.append((f"the real mixture has an azeotrope (model x = {az[0]:.3f}, {az[1]:.2f} C) near the measured 0.894, 78.15 C",
                   az is not None and abs(az[0] - 0.894) < 0.03 and abs(az[1] - 78.15) < 0.2))
    checks.append(("the azeotrope boils below pure ethanol (a minimum-boiling azeotrope)", az[1] < L.boiling_point("ethanol")))
    checks.append(("Raoult's ideal law gives no azeotrope", L.azeotrope(ideal=True) is None))
    checks.append(("local alpha is large when ethanol is dilute (> 7) and below 1.1 near x = 0.85",
                   L.local_alpha(0.02) > 7 and L.local_alpha(0.85) < 1.1))
    vf, yf, tf = L.flash_from_liquid(0.10, 0.05)
    checks.append((f"flash: lever rule V/F = {vf:.3f} closes the ethanol balance", abs(vf * yf + (1 - vf) * 0.05 - 0.10) < 1e-12))
    checks.append(("mass percent of the measured azeotrope x = 0.894 is about 95.6 %", abs(L.mass_percent(0.894) - 95.6) < 0.1))
    checks.append(("lower pressure lowers the bubble temperature", L.bubble_point(0.10, 300.0)[0] < t))
    bad = 0
    for call in (lambda: L.bubble_point(1.5), lambda: L.bubble_point(0.5, -1.0), lambda: L.flash_from_liquid(0.10, 0.20)):
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
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
