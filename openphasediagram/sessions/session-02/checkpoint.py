"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    cl, cs, fl, fs = L.tie_line(50.0, 1300.0)
    # hand calculation: C_L = 50*(1300-1085)/(1320-1085)*... read sideways off the straight pieces
    cl_hand = (1300.0 - 1085.0) / (1320.0 - 1085.0) * 50.0          # liquidus piece 0..50
    cs_hand = 50.0 + (1300.0 - 1240.0) / (1455.0 - 1240.0) * 50.0   # solidus piece 50..100
    checks.append((f"tie line at 1300 C: C_L = {cl_hand:.1f} and C_S = {cs_hand:.1f} wt% Ni",
                   abs(cl - cl_hand) < 1e-9 and abs(cs - cs_hand) < 1e-9 and round(cl, 1) == 45.7 and round(cs, 1) == 64.0))
    fl_hand = (cs_hand - 50.0) / (cs_hand - cl_hand)
    checks.append((f"worked example: 50 wt% Ni at 1300 C is {100 * fl_hand:.1f} percent liquid (lever rule)",
                   abs(fl - fl_hand) < 1e-12 and round(100 * fl, 1) == 76.6))
    checks.append(("fractions add to 1", abs(fl + fs - 1.0) < 1e-12))
    checks.append(("mass balance: f_L C_L + f_S C_S = C0 for many (C0, T)",
                   all(abs(f * a + (1 - f) * b - c0) < 1e-9
                       for c0 in (20.0, 35.0, 50.0, 80.0)
                       for T in np.linspace(L.solidus(c0) + 1, L.liquidus(c0) - 1, 7)
                       for a, b, f, _ in [L.tie_line(c0, float(T))])))
    checks.append(("edge: at the liquidus f_L = 1 and at the solidus f_L = 0",
                   abs(L.liquid_fraction(50.0, 1320.0) - 1.0) < 1e-12 and abs(L.liquid_fraction(50.0, 1240.0)) < 1e-12))
    checks.append(("edge: above the liquidus the alloy is all liquid, below the solidus all solid",
                   L.liquid_fraction(50.0, 1400.0) == 1.0 and L.liquid_fraction(50.0, 1100.0) == 0.0))
    checks.append(("liquid fraction never increases as the alloy cools",
                   bool(np.all(np.diff([L.liquid_fraction(60.0, float(t)) for t in np.linspace(1400, 1100, 61)]) <= 1e-12))))
    t50 = L.temperature_for_liquid_fraction(50.0, 0.5)
    checks.append((f"design: 50 wt% Ni is half liquid at {t50:.1f} C (check f_L = 0.5)",
                   abs(L.liquid_fraction(50.0, t50) - 0.5) < 1e-9 and abs(t50 - 1278.2) < 0.05))
    c1300 = L.composition_for_liquid_fraction(1300.0, 0.5)
    checks.append((f"design: at 1300 C the alloy that is half liquid is {c1300:.1f} wt% Ni (middle of the tie line)",
                   abs(c1300 - 54.85) < 0.01 and abs(L.liquid_fraction(c1300, 1300.0) - 0.5) < 1e-9))
    t70 = L.temperature_for_liquid_fraction(70.0, 0.5)
    checks.append((f"design: 70 wt% Ni is half liquid at {t70:.1f} C",
                   abs(t70 - 1355.5) < 0.05))
    checks.append(("pure metals have no two-phase band: liquidus = solidus at 0 and 100 wt% Ni",
                   L.liquidus(0.0) == L.solidus(0.0) and L.liquidus(100.0) == L.solidus(100.0)))
    cl2, cs2, fl2, fs2 = L.tie_line(50.0, 1280.0)
    checks.append((f"50 wt% Ni at 1280 C: C_L = {cl2:.1f}, C_S = {cs2:.1f} wt% Ni, f_L = {fl2:.3f}",
                   (round(cl2, 1), round(cs2, 1), round(fl2, 3)) == (41.5, 59.3, 0.522)))
    cl3, cs3, fl3, _ = L.tie_line(30.0, 1200.0)
    checks.append((f"30 wt% Ni at 1200 C: C_L = {cl3:.1f}, C_S = {cs3:.1f}, f_L = {fl3:.3f}",
                   (round(cl3, 1), round(cs3, 1), round(fl3, 3)) == (24.5, 37.1, 0.562)))
    checks.append(("half liquid needs 43.7 wt% Ni at 1250 C and 68.3 wt% Ni at 1350 C",
                   round(L.composition_for_liquid_fraction(1250.0, 0.5), 1) == 43.7 and round(L.composition_for_liquid_fraction(1350.0, 0.5), 1) == 68.3))
    f_app = L.liquid_fraction(70.0, 1355.0)
    checks.append((f"app challenge: 70 wt% Ni at 1355 C is {100 * f_app:.1f} percent liquid, within 3 points of half",
                   abs(f_app - 0.5) < 0.03 and abs(L.liquid_fraction(50.0, 1280.0) - 0.5) >= 0.02))
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
