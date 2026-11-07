"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    pk = L.peak_emf(400, 0.15, 0.002, 10.0)
    checks.append((f"worked example: hand crank peak 7.54 V and RMS 5.33 V (got {pk:.2f}, {L.rms_from_peak(pk):.2f})",
                   abs(pk - 7.5398) < 1e-3 and abs(L.rms_from_peak(pk) - 5.3317) < 1e-3))
    d = L.design_transformer(230.0, 12.0, 24.0, 24)
    checks.append((f"worked example: 230 V to 12 V, 24 W gives N1 = 460 for N2 = 24, I2 = 2 A, I1 = 0.104 A",
                   abs(d["n1"] - 460.0) < 1e-9 and abs(d["i2"] - 2.0) < 1e-12 and abs(d["i1"] - 24 / 230) < 1e-12))

    t = np.linspace(0, 0.2, 20001)           # two periods at 10 Hz
    e_exact = L.emf(t, 400, 0.15, 0.002, 10.0)
    e_num = L.emf_numeric(t, 400, 0.15, 0.002, 10.0)
    checks.append(("Faraday: -N dPhi/dt (numerical) matches N B A w sin(w t)", float(np.abs(e_exact - e_num)[1:-1].max()) < 1e-3))
    checks.append(("EMF is zero when the flux is largest (t = 0)", abs(e_exact[0]) < 1e-12))
    quarter = int(round(0.025 / 0.2 * 20000))
    checks.append(("EMF is largest when the flux is zero (quarter period)", abs(abs(e_exact[quarter]) - L.peak_emf(400, 0.15, 0.002, 10.0)) < 1e-6
                   and abs(L.rotating_flux(0.025, 0.15, 0.002, 10.0)) < 1e-12))
    t50 = np.linspace(0, 0.04, 40001)[:-1]
    w = L.emf(t50, 1, 1.0, 1.0 / (2 * np.pi * 50), 50.0)       # peak exactly 1 V
    checks.append(("RMS of a sine over whole periods is peak / sqrt(2)", abs(L.rms_numeric(w) - 1 / np.sqrt(2)) < 1e-4))
    checks.append(("50 Hz has a period of 20 ms", abs(L.period(50) - 0.020) < 1e-15))
    checks.append(("mains 230 V RMS has a peak near 325 V", abs(230 * np.sqrt(2) - 325.27) < 0.01))

    v1, n1, n2, i1 = 230.0, 460, 24, 0.1043478
    checks.append(("V2 / V1 = N2 / N1 (230 V on 460 turns gives 12 V on 24 turns)", abs(L.secondary_voltage(v1, n1, n2) - 12.0) < 1e-9))
    checks.append(("power in = power out for the ideal transformer",
                   abs(v1 * i1 - L.secondary_voltage(v1, n1, n2) * L.secondary_current(i1, n1, n2)) < 1e-6))
    checks.append(("a step-down transformer raises the current", L.secondary_current(i1, n1, n2) > i1))
    checks.append(("doubling the field doubles the peak EMF",
                   abs(L.peak_emf(400, 0.30, 0.002, 10.0) / pk - 2) < 1e-12))
    flat = L.emf_numeric(t, 400, 0.15, 0.002, 0.0 + 1e-12)       # a coil that does not turn
    checks.append(("a coil that does not turn makes no EMF (DC gives nothing)", float(np.abs(flat).max()) < 1e-6))
    try:
        L.design_transformer(230.0, 0.0, 24.0, 24)
        ok = False
    except ValueError:
        ok = True
    checks.append(("a zero secondary voltage is rejected", ok))
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
