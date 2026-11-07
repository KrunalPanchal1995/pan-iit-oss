"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    cx, cy = L.circle(80)
    c = L.solve_panels(cx, cy, 0.0, kutta=False)
    exact = 1 - 4 * np.sin(np.arctan2(c["y"], c["x"])) ** 2
    checks.append(("validation: circle Cp matches the exact 1 - 4 sin^2 within 1e-9", np.max(np.abs(c["cp"] - exact)) < 1e-9))
    checks.append(("validation: circle has zero lift and zero drag (d'Alembert)", abs(c["cl"]) < 1e-9 and abs(c["cd_pressure"]) < 1e-9))
    checks.append(("mass conservation: the sources on a closed body add up to zero", abs(c["source_total"]) < 1e-9))
    X, Y = L.naca4("0012", 80)
    s0 = L.solve_panels(X, Y, 0.0)
    checks.append(("symmetric airfoil at 0 degrees gives no lift", abs(s0["cl"]) < 1e-9))
    s5 = L.solve_panels(X, Y, 5.0)
    checks.append((f"worked example: NACA 0012 at 5 degrees CL = {s5['cl']:.4f} (0.6025)", abs(s5["cl"] - 0.6025) < 1e-3))
    thin = 2 * np.pi * np.radians(5.0)
    checks.append(("thickness correction: CL within 1 % of 2 pi (1 + 0.77 t/c) alpha = 0.599",
                   abs(s5["cl"] / (thin * (1 + 0.77 * 0.12)) - 1) < 0.01))
    checks.append(("lift from pressure and from circulation (Kutta-Joukowski) agree within 1 %",
                   abs(s5["cl"] / s5["cl_circulation"] - 1) < 0.01))
    checks.append(("Kutta condition: equal speeds leave both sides of the trailing edge",
                   abs(abs(s5["vt"][0]) - abs(s5["vt"][-1])) < 1e-9))
    checks.append(("inviscid pressure drag is almost zero (below 0.001)", abs(s5["cd_pressure"]) < 1e-3))
    s5b = L.solve_panels(*L.naca4("0012", 40), 5.0)
    checks.append(("convergence: 80 and 160 panels agree within 0.2 %", abs(s5b["cl"] / s5["cl"] - 1) < 2e-3))
    checks.append(("CL(-a) = -CL(a) for a symmetric airfoil", abs(L.solve_panels(X, Y, -5.0)["cl"] + s5["cl"]) < 1e-9))
    a0 = -L.airfoil_cl("2412", 0.0) / ((L.airfoil_cl("2412", 4.0) - L.airfoil_cl("2412", 0.0)) / 4.0)
    checks.append((f"camber: NACA 2412 zero-lift angle {a0:.2f} degrees is near thin theory -2.08", abs(a0 + 2.08) < 0.15))
    u, v = L.velocity_field(X, Y, 5.0, np.array([[-30.0, 30.0]]), np.array([[20.0, -25.0]]))
    checks.append(("far from the airfoil the air moves at the free-stream speed (within 1 %)",
                   np.all(np.abs(np.hypot(u, v) - 1) < 0.01)))
    re = L.reynolds(50.0, 1.5)
    checks.append(("hand calculation: Re = 50 x 1.5 / 1.5e-5 = 5 million, Cf = 0.074 / Re^0.2 = 0.00338",
                   abs(re - 5e6) < 1e-6 and abs(L.skin_friction(re) - 0.00338) < 1e-5))
    checks.append(("worked example: NACA 0012 profile drag cd = 0.00848", abs(L.cd_profile(0.12, re) - 0.00848) < 1e-5))
    checks.append(("thicker sections have more drag; higher Re less friction",
                   L.cd_profile(0.15, re) > L.cd_profile(0.12, re) and L.skin_friction(1e7) < L.skin_friction(1e6)))
    best, rows = L.choose_section(["2408", "2412", "2415", "4412", "0012"])
    checks.append(("mini-project: NACA 2412 is chosen; 2408, 4412 and 0012 break a rule",
                   best == "2412" and [r[4] for r in rows] == [False, True, True, False, False]))
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
