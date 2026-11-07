"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    P, Q, S, pf = L.power_triangle(230.0, 10.0, 60.0)
    checks.append(("power triangle: 230 V, 10 A, phi 60 degrees gives P = 1150 W, Q = 1992 var, S = 2300 VA, pf 0.5",
                   abs(P - 1150.0) < 0.5 and abs(Q - 1991.9) < 0.5 and abs(S - 2300.0) < 1e-9 and abs(pf - 0.5) < 1e-12))
    checks.append(("S^2 = P^2 + Q^2", abs(S ** 2 - P ** 2 - Q ** 2) < 1e-6))
    i1, i2 = L.current_for(100e3, 400.0, 0.7), L.current_for(100e3, 400.0, 0.95)
    checks.append(("worked example: 100 kW at 400 V needs 357.1 A at pf 0.70 and 263.2 A at pf 0.95",
                   abs(i1 - 357.1) < 0.05 and abs(i2 - 263.2) < 0.05))
    checks.append(("unity power factor current is P / V = 250 A", abs(L.current_for(100e3, 400.0, 1.0) - 250.0) < 1e-9))
    qc = L.capacitor_kvar(100e3, 0.7, 0.95)
    checks.append(("worked example: lifting 100 kW from pf 0.70 to 0.95 needs Qc = 69.15 kvar",
                   abs(qc / 1e3 - 69.15) < 0.01))
    checks.append(("hand calculation: tan(acos 0.70) = 1.0202 and tan(acos 0.95) = 0.3287",
                   abs(np.tan(np.arccos(0.7)) - 1.0202) < 1e-4 and abs(np.tan(np.arccos(0.95)) - 0.3287) < 1e-4))
    C = L.capacitance_for(qc, 400.0, 50.0)
    checks.append(("capacitance for 69.15 kvar at 400 V, 50 Hz is 1376 microfarad", abs(C * 1e6 - 1376.0) < 1.0))
    checks.append(("a capacitor of that size gives back Qc = 2 pi f C V^2", abs(2 * np.pi * 50.0 * C * 400.0 ** 2 - qc) < 1e-6))
    # after correction the apparent power is P / 0.95 and the new current follows
    q_after = L.reactive_for(100e3, 0.95)
    checks.append(("after correction Q = 32.87 kvar and S = 105.3 kVA (so I = 263.2 A)",
                   abs(q_after / 1e3 - 32.87) < 0.01 and abs(np.hypot(100e3, q_after) / 1e3 - 105.26) < 0.01
                   and abs(np.hypot(100e3, q_after) / 400.0 - i2) < 1e-6))
    checks.append(("before correction S = 142.9 kVA", abs(np.hypot(100e3, L.reactive_for(100e3, 0.7)) / 1e3 - 142.86) < 0.01))
    qd = L.capacitor_kvar(50e3, 0.75, 0.95)
    checks.append(("design problem: 50 kW from pf 0.75 to 0.95 needs 27.66 kvar, which is 550 microfarad at 400 V",
                   abs(qd / 1e3 - 27.66) < 0.01 and abs(L.capacitance_for(qd, 400.0) * 1e6 - 550.0) < 1.0))
    checks.append(("no correction needed: pf 0.95 to 0.95 gives 0 kvar", abs(L.capacitor_kvar(50e3, 0.95, 0.95)) < 1e-9))
    l10, l100 = L.line_loss(1e6, 10e3, 5.0), L.line_loss(1e6, 100e3, 5.0)
    checks.append(("1 MW over 5 ohm: loss is 50000 W at 10 kV and 500 W at 100 kV", abs(l10 - 50000.0) < 1e-6 and abs(l100 - 500.0) < 1e-6))
    checks.append(("ten times the voltage gives exactly one hundredth of the loss", abs(l10 / l100 - 100.0) < 1e-9))
    checks.append(("line loss grows by (0.95/0.70)^2 = 1.842 when pf drops from 0.95 to 0.70",
                   abs(L.line_loss(1e6, 10e3, 5.0, 0.7) / L.line_loss(1e6, 10e3, 5.0, 0.95) - 1.842) < 1e-3))
    s3 = 100e3 / (np.sqrt(3) * 400.0 * 0.95)
    checks.append(("three-phase: P = sqrt(3) V_line I pf holds for I = P / (sqrt(3) V pf)", abs(np.sqrt(3) * 400.0 * s3 * 0.95 - 100e3) < 1e-6))
    checks.append(("Section F answer B: 30 kW at 230 V, pf 0.8 needs 163.0 A, 130.4 A at unity, and 22.5 kvar of reactive power",
                   abs(L.current_for(30e3, 230.0, 0.8) - 163.04) < 0.01 and abs(L.current_for(30e3, 230.0, 1.0) - 130.43) < 0.01
                   and abs(L.reactive_for(30e3, 0.8) / 1e3 - 22.5) < 1e-9))
    checks.append(("Section F answer C: 100 kW at 400 V needs 500 A at pf 0.5, twice the 250 A at pf 1", abs(L.current_for(100e3, 400.0, 0.5) - 500.0) < 1e-9))
    checks.append(("line currents for 1 MW: 100 A at 10 kV and 10 A at 100 kV", abs(L.current_for(1e6, 10e3, 1.0) - 100.0) < 1e-9 and abs(L.current_for(1e6, 100e3, 1.0) - 10.0) < 1e-9))
    q1 = L.reactive_for(50e3, 0.75)
    pf_30 = 50e3 / np.hypot(50e3, q1 - 30e3)
    checks.append(("Section F answer D: the 50 kW load has Q = 44.10 kvar; a standard 30 kvar bank gives pf 0.9624, under-correcting; 27.66 kvar is the exact size for 0.95",
                   abs(q1 / 1e3 - 44.10) < 0.01 and abs(pf_30 - 0.9624) < 5e-4))
    checks.append(("before correction Q = 102.0 kvar, after Q = 32.9 kvar", abs(L.reactive_for(100e3, 0.7) / 1e3 - 102.0) < 0.05 and abs(L.reactive_for(100e3, 0.95) / 1e3 - 32.9) < 0.05))
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
