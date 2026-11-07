"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R1 = L.poiseuille_R(L.MU_BLOOD, 0.10, 1.0e-3)
    R2 = L.poiseuille_R(L.MU_BLOOD, 0.10, 0.5e-3)
    checks.append(("worked example: half the radius gives 16 times the resistance", abs(R2 / R1 - 16.0) < 1e-9))
    checks.append(("worked example: r = 1.0 mm, L = 0.10 m gives 6.685 mmHg per (mL/s)",
                   abs(L.to_mmHg_per_mLs(R1) - 6.685) < 1e-3))
    checks.append(("worked example: r = 0.5 mm gives 106.96 mmHg per (mL/s)", abs(L.to_mmHg_per_mLs(R2) - 106.96) < 1e-2))
    checks.append(("a 10 mmHg push through the 1.0 mm tube gives 1.496 mL/s",
                   abs(10.0 / L.to_mmHg_per_mLs(R1) - 1.4959) < 1e-3))
    checks.append(("hand calculation: R = 8 mu L / (pi r^4) = 8.913e8 Pa s/m^3 for r = 1 mm",
                   abs(R1 - 8 * 3.5e-3 * 0.1 / (np.pi * 1e-12)) < 1.0 and abs(R1 / 1e8 - 8.913) < 1e-3))
    checks.append(("cardiac output 70 x 70 mL is 4.9 L/min", abs(L.cardiac_output(70, 70) - 4.9) < 1e-12))
    checks.append(("worked example: TPR = 93 / 5 = 18.6 mmHg per (L/min)", abs(L.tpr_from(93.0, 5.0) - 18.6) < 1e-12))
    checks.append(("rule of thumb: 120/80 gives a mean pressure of 93.3 mmHg", abs(L.map_from_bp(120, 80) - 93.333) < 1e-3))
    checks.append(("worked example: +20% resistance at 5 L/min gives 111.6 mmHg",
                   abs(L.map_from_co(5.0, 1.2 * L.TPR_TYPICAL) - 111.6) < 1e-9))
    checks.append(("the radius that gives +20% resistance is 0.9554 of normal (4.5% narrower)",
                   abs(L.radius_ratio_for(1.2) - 0.9554) < 1e-4 and abs(L.resistance_factor(L.radius_ratio_for(1.2)) - 1.2) < 1e-12))
    checks.append(("radius 5% smaller gives 1.228 times the resistance", abs(L.resistance_factor(0.95) - 1.2277) < 1e-4))
    checks.append(("typical heart (70 x 70 mL), normal vessels: MAP 91.1 mmHg", abs(L.map_model(70, 70) - 91.14) < 1e-9))
    checks.append(("radius 5% smaller at 70 x 70 mL: MAP 111.9 mmHg", abs(L.map_model(70, 70, 0.95) - 111.896) < 1e-2))
    checks.append(("design: 60 bpm x 70 mL with radius 0.95 keeps MAP at 95.9 mmHg (below 100)",
                   abs(L.map_model(60, 70, 0.95) - 95.911) < 1e-2 and L.map_model(60, 70, 0.95) < 100.0))
    checks.append(("halving the radius at constant 4.9 L/min would need 1458 mmHg: impossible",
                   abs(L.map_model(70, 70, 0.5) - 1458.24) < 1e-2))
    checks.append(("radius ratio 1 changes nothing", abs(L.resistance_factor(1.0) - 1.0) < 1e-15))
    checks.append(("resistance and radius ratios are inverse to each other",
                   abs(L.radius_ratio_for(L.resistance_factor(0.7)) - 0.7) < 1e-12))
    bad = 0
    for args in ((0, 1, 1), (1, 0, 1), (1, 1, 0)):
        try:
            L.poiseuille_R(*args)
        except ValueError:
            bad += 1
    checks.append(("zero viscosity, length or radius is rejected", bad == 3))
    try:
        L.tpr_from(93.0, 0.0)
        ok0 = False
    except ValueError:
        ok0 = True
    checks.append(("zero cardiac output is rejected instead of dividing by zero", ok0))

    # --- numbers used in the text
    checks.append(("worked example: 8 mu L = 2.8e-3 and pi r^4 = 3.142e-12", abs(8 * L.MU_BLOOD * 0.10 - 2.8e-3) < 1e-12 and abs(np.pi * 1e-12 - 3.142e-12) < 1e-15))
    checks.append(("worked example: the flow for 10 mmHg through the 0.5 mm tube is 0.0935 mL/s", abs(10.0 / L.to_mmHg_per_mLs(R2) - 0.0935) < 1e-4))
    m09 = L.map_from_co(5.0, L.TPR_TYPICAL * L.resistance_factor(0.9))
    m11 = L.map_from_co(5.0, L.TPR_TYPICAL * L.resistance_factor(1.1))
    checks.append(("MAP at 5 L/min is 141.7 at radius 0.9 and 63.5 at radius 1.1 (changes +48.7 and -29.5)",
                   abs(m09 - 141.74) < 0.01 and abs(m11 - 63.52) < 0.01 and abs(m09 - 93 - 48.74) < 0.01 and abs(93 - m11 - 29.48) < 0.01))
    checks.append(("factors 1.524 (r = 0.9), 0.683 (r = 1.1) and 2.44 (r = 0.8)",
                   abs(L.resistance_factor(0.9) - 1.5242) < 1e-4 and abs(L.resistance_factor(1.1) - 0.6830) < 1e-4 and abs(L.resistance_factor(0.8) - 2.4414) < 1e-4))
    checks.append(("80 beats x 60 mL is 4.8 L/min and MAP 89.3", abs(L.cardiac_output(80, 60) - 4.8) < 1e-12 and abs(L.map_from_co(4.8, 18.6) - 89.28) < 1e-9))
    tpr_n = 18.6 * L.resistance_factor(0.95)
    checks.append(("design: TPR 22.8 and the largest output for MAP 100 is 4.38 L/min", abs(tpr_n - 22.84) < 0.01 and abs(100.0 / tpr_n - 4.379) < 1e-3))
    checks.append(("a 5 L/min case from 100 x 50 mL gives exactly 93 mmHg", abs(L.map_model(100, 50) - 93.0) < 1e-9))
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
