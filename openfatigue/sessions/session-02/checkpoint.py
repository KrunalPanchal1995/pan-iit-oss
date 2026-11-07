"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    a, b = L.basquin_constants()
    checks.append(("Basquin anchors: 540 MPa at 1000 cycles and 300 MPa at 1e6 cycles",
                   abs(a * 1e3 ** b - 540) < 1e-6 and abs(a * 1e6 ** b - 300) < 1e-6))
    checks.append((f"b is about -0.085 for the bar (got {b:.4f}) and about -0.137 for the part (S_e = 210)",
                   abs(b + 0.0851) < 1e-4 and abs(L.basquin_constants(600, 210)[1] + 0.1367) < 1e-4))
    checks.append(("stress_for_life and life are inverse functions", abs(L.life(L.stress_for_life(1e5)) / 1e5 - 1) < 1e-9))

    # Goodman line, verified numerically
    sms = np.linspace(0, 590, 12)
    on_line = [L.goodman_sum(L.SE * (1 - s / L.SU), s) for s in sms]
    checks.append(("Goodman line: S_a/S_e + S_m/S_u = 1 on 12 points of the line", bool(np.allclose(on_line, 1.0))))
    eq = [L.equivalent_amplitude(L.SE * (1 - s / L.SU), s) for s in sms]
    checks.append(("every point on the Goodman line has equivalent amplitude S_e = 300 MPa", bool(np.allclose(eq, L.SE))))
    checks.append(("a point inside the line, (100, 150), has sum 0.583 and infinite life", abs(L.goodman_sum(100, 150) - 0.5833) < 1e-3 and L.life_with_mean(100, 150) == np.inf))
    n_a = L.life_with_mean(200, 300)
    checks.append((f"(S_a, S_m) = (200, 300) has sum 1.167 and equals a 400 MPa reversed load: about 34,000 cycles (got {n_a:,.0f})",
                   abs(L.goodman_sum(200, 300) - 1.1667) < 1e-3 and abs(L.equivalent_amplitude(200, 300) - 400) < 1e-9 and abs(n_a - 34017) < 5))
    checks.append(("a tensile mean stress shortens life", L.life_with_mean(250, 100) < L.life_with_mean(250, 0) or L.life_with_mean(250, 0) == np.inf and L.life_with_mean(340, 100) < L.life_with_mean(340, 0)))
    try:
        L.equivalent_amplitude(100, 600)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: mean stress equal to S_u is rejected", raised))

    # stress concentration
    kt = L.stress_concentration_hole()
    checks.append((f"K_t of a hole in a wide plate is 3 (got {kt:.4f})", abs(kt - 3.0) < 1e-6))
    checks.append(("hole: stress at 90 degrees is 3 and at 0 degrees is -1 (compression)", abs(L.hole_hoop_stress(90) - 3) < 1e-12 and abs(L.hole_hoop_stress(0) + 1) < 1e-12))
    checks.append(("hole: far from the hole the stress approaches the nominal value 1 (at 0 and 90 degrees mean)", abs(L.hole_hoop_stress(90, 50.0) - 1.0) < 2e-3))
    n_hole = L.life_with_notch(100, 50, 3.0)
    checks.append((f"plate with a hole, nominal (100, 50) MPa: about 34,000 cycles; without the hole infinite (got {n_hole:,.0f})",
                   abs(n_hole - 34017) < 5 and L.life_with_notch(100, 50, 1.0) == np.inf))

    # worked example: shaft
    d = L.design_diameter_mm(200, 2.0, 1.0)
    s27 = L.bending_stress_mpa(200, 0.027)
    hand = (32 * 200 * 2 / (np.pi * 210e6)) ** (1 / 3) * 1000
    checks.append((f"worked example: shaft M = 200 N m, n = 2 needs d = 26.87 mm (got {d:.2f}); take 27 mm", abs(d - 26.87) < 0.01 and abs(d - hand) < 1e-9))
    checks.append((f"worked example: 27 mm gives 103.5 MPa and margin 2.03 (got {s27:.1f}, {210 / s27:.2f})", abs(s27 - 103.5) < 0.05 and abs(210 / s27 - 2.03) < 0.01))
    checks.append(("worked example: with a shoulder K_t = 2 the diameter becomes 33.86 mm", abs(L.design_diameter_mm(200, 2.0, 2.0) - 33.86) < 0.01))
    checks.append(("27 mm shaft has indefinite life in this model", L.shaft_life(200, 27) == np.inf))
    n20 = L.shaft_life(200, 20)
    checks.append((f"a 20 mm shaft (254.6 MPa, above 210) lasts about 244,000 cycles (got {n20:,.0f})", abs(L.bending_stress_mpa(200, 0.02) - 254.6) < 0.1 and abs(n20 - 244157) < 20))
    checks.append(("design diameter grows with moment, safety factor and K_t",
                   L.design_diameter_mm(300) > L.design_diameter_mm(200) and L.design_diameter_mm(200, 3) > L.design_diameter_mm(200, 2) and L.design_diameter_mm(200, 2, 2) > L.design_diameter_mm(200, 2, 1)))
    checks.append(("Section F: M = 150 N m, n = 2, K_t = 1.5 gives 27.95 mm; with K_t = 1 it is 24.41 mm",
                   abs(L.design_diameter_mm(150, 2, 1.5) - 27.95) < 0.01 and abs(L.design_diameter_mm(150, 2, 1.0) - 24.41) < 0.01))
    s28 = 1.5 * L.bending_stress_mpa(150, 0.028)
    checks.append((f"Section F: 28 mm with K_t = 1.5 gives local stress 104.4 MPa (got {s28:.1f}); 22 mm fails after about 835,000 cycles",
                   abs(s28 - 104.4) < 0.05 and abs(L.shaft_life(150, 22, 1.5) - 835170) < 50))
    # extra numbers used in the text
    checks.append(("1500 revolutions per minute is 25 Hz, so 1 million cycles take 11.1 hours", abs(1e6 / (1500 / 60.0) / 3600 - 11.11) < 0.01))
    checks.append(("S-N values: 365 MPa gives 100,000 cycles and 444 MPa gives 10,000 cycles", abs(L.stress_for_life(1e5) - 364.9) < 0.1 and abs(L.stress_for_life(1e4) - 443.9) < 0.1))
    checks.append((f"Section F: (S_a, S_m) = (240, 250) has S_eq = 411.4 MPa and life about 24,400 cycles (got {L.life_with_mean(240, 250):,.0f})",
                   abs(L.equivalent_amplitude(240, 250) - 411.4) < 0.05 and abs(L.life_with_mean(240, 250) - 24430) < 10))
    checks.append(("Section F: (S_a, S_m) = (150, 300) lies exactly on the Goodman line (sum 1.000)", abs(L.goodman_sum(150, 300) - 1.0) < 1e-12))
    m25 = 210 / (1.5 * L.bending_stress_mpa(150, 0.025))
    m28 = 210 / (1.5 * L.bending_stress_mpa(150, 0.028))
    checks.append((f"Section F: margins for M = 150 N m, K_t = 1.5: 25 mm gives {m25:.2f} (too low), 28 mm gives {m28:.2f}", abs(m25 - 1.43) < 0.005 and abs(m28 - 2.01) < 0.005))
    checks.append(("Section F: hole plate with nominal amplitude 80 MPa has infinite life, with 110 MPa about 326,000 cycles",
                   L.life_with_notch(80, 0, 3) == np.inf and abs(L.life_with_notch(110, 0, 3) - 326247) < 20))
    checks.append(("challenge: K_t = 3 with nominal (60, 30) MPa gives Goodman sum 0.75 and infinite life", abs(L.goodman_sum(180, 90) - 0.75) < 1e-12 and L.life_with_notch(60, 30, 3) == np.inf))
    checks.append(("a shoulder with K_t = 2 costs about 7 mm of diameter (33.86 - 26.87 = 6.99)", abs((L.design_diameter_mm(200, 2, 2) - L.design_diameter_mm(200, 2, 1)) - 6.99) < 0.01 and abs(L.design_diameter_mm(200, 2, 2) / L.design_diameter_mm(200, 2, 1) - 2 ** (1 / 3)) < 1e-9))
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
