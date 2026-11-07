"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    v1, v2 = np.array([4.0, 0.0]), np.zeros(2)
    a, b = L.disc_collision(1, 1, v1, v2, 0.5, 0.5, 0.5, 1.0)
    checks.append((f"worked example: disc 1 leaves with (1.00, -1.73) m/s (got {a.round(2)})", np.allclose(a, [1.0, -np.sqrt(3)])))
    checks.append((f"worked example: disc 2 leaves with (3.00, 1.73) m/s (got {b.round(2)})", np.allclose(b, [3.0, np.sqrt(3)])))
    checks.append(("worked example: the discs leave at 90 degrees to each other", abs(np.dot(a, b)) < 1e-12 and abs(L.angle_deg(b) - L.angle_deg(a) - 90) < 1e-9))
    cases = [(1, 1, 0.5, 1.0), (2, 1, 0.3, 0.6), (1, 3, 0.8, 0.0), (5, 2, 0.1, 0.9)]
    ok_p = ok_e = True
    for m1, m2, bb, e in cases:
        x, y = L.disc_collision(m1, m2, v1, v2, bb, 0.5, 0.5, e)
        ok_p &= np.allclose(m1 * x + m2 * y, m1 * v1 + m2 * v2)
        ke0 = 0.5 * m1 * v1 @ v1
        ok_e &= abs(ke0 - (0.5 * m1 * x @ x + 0.5 * m2 * y @ y) - L.ke_lost(m1, m2, v1, v2, bb, 0.5, 0.5, e)) < 1e-9
    checks.append(("the momentum vector of the pair is kept", ok_p))
    checks.append(("kinetic energy before - after equals the formula 1/2 mu (1 - e^2) v_n^2", ok_e))
    # the head-on case must agree with the one-dimensional formula of Session 2
    a0, b0 = L.disc_collision(2, 1, np.array([4.0, 0.0]), np.array([-1.0, 0.0]), 0.0, 0.5, 0.5, 0.5)
    checks.append(("head-on (b = 0) gives the one-dimensional answer of Session 2: 1.5 and 4.0 m/s", abs(a0[0] - 1.5) < 1e-9 and abs(b0[0] - 4.0) < 1e-9 and abs(a0[1]) < 1e-12))
    # the contact simulation is an independent check of the formula
    worst = 0.0
    for e in (1.0, 0.8, 0.5):
        fa, fb = L.disc_collision(1, 1, v1, v2, 0.5, 0.5, 0.5, e)
        sa, sb = L.simulate_contact(1, 1, v1, v2, 0.5, 0.5, 0.5, e)
        worst = max(worst, np.abs(fa - sa).max(), np.abs(fb - sb).max())
        checks.append((f"validation: the contact simulation conserves momentum for e = {e}", np.allclose(sa + sb, v1 + v2, atol=1e-9)))
    checks.append((f"validation: simulation and formula agree within 1.5 percent of the 4 m/s approach speed (worst {worst:.3f} m/s)", worst < 0.06))
    cr = L.crash(1200, 50, 0.6)
    checks.append((f"worked example: car 1200 kg, 50 km/h, 0.6 m crumple absorbs 116 kJ at 16.4 g and 193 kN (got {cr['energy_kj']:.0f} kJ, {cr['decel_g']:.1f} g, {cr['force_kn']:.0f} kN)",
                   abs(cr["energy_kj"] - 115.7) < 0.2 and abs(cr["decel_g"] - 16.4) < 0.05 and abs(cr["force_kn"] - 193) < 0.5))
    checks.append(("design: a crumple distance of 0.50 m keeps the average at or below 20 g, 0.49 m and 0.40 m do not",
                   L.crash(1200, 50, 0.50)["decel_g"] <= 20 < L.crash(1200, 50, 0.49)["decel_g"] < L.crash(1200, 50, 0.40)["decel_g"]))
    checks.append(("edge case: a grazing hit (b close to R1 + R2) hands over almost no speed", np.hypot(*L.disc_collision(1, 1, v1, v2, 0.999, 0.5, 0.5, 1.0)[1]) < 0.2))
    for bad, label in ((lambda: L.disc_collision(1, 1, v1, v2, 1.0, 0.5, 0.5, 1.0), "the discs miss (b = R1 + R2)"),
                       (lambda: L.disc_collision(1, 1, v1, v2, 0.2, 0.5, 0.5, 1.5), "e above 1"),
                       (lambda: L.disc_collision(1, 1, -v1, v2, 0.2, 0.5, 0.5, 1.0), "the discs moving apart"),
                       (lambda: L.disc_collision(0, 1, v1, v2, 0.2, 0.5, 0.5, 1.0), "mass 0")):
        try:
            bad()
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
