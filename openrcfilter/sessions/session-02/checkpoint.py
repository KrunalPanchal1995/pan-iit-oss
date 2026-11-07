"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R, C = 16e3, 100e-9
    tau, fc = L.time_constant(R, C), L.cutoff_hz(R, C)
    checks.append(("worked example: 16 kohm and 100 nF give tau = 1.60 ms and f_c = 99.47 Hz",
                   abs(tau - 1.6e-3) < 1e-9 and abs(fc - 99.47) < 0.01))
    checks.append(("worked example: the 50 Hz hum keeps gain 0.8935, only 0.98 dB removed",
                   abs(float(L.gain(50, fc)) - 0.8935) < 5e-4 and abs(L.hum_removed_db(fc) - 0.98) < 0.01))
    checks.append(("worked example: removing 50 Hz by 20 dB needs f_c = 5.025 Hz",
                   abs(L.fc_for_attenuation(20.0) - 5.025) < 0.001))
    checks.append(("step response is 0 at t = 0 and 0.632 at one tau",
                   abs(float(L.step_response(0.0, tau))) < 1e-12 and abs(float(L.step_response(tau, tau)) - 0.6321) < 1e-4))
    checks.append(("step response reaches 0.950 at three tau", abs(float(L.step_response(3 * tau, tau)) - 0.9502) < 1e-4))
    n = 600
    num = L.step_response_numeric(tau, tau / 100, n)
    ana = L.step_response(np.arange(n + 1) * tau / 100, tau)
    checks.append(("numeric (Euler) step response agrees with 1 - exp(-t/tau) within 0.003", float(np.max(np.abs(num - ana))) < 0.003))
    checks.append(("gain at f_c is 1/sqrt(2), which is -3.01 dB", abs(float(L.gain(fc, fc)) - 2 ** -0.5) < 1e-12
                   and abs(float(L.gain_db(fc, fc)) + 3.0103) < 1e-3))
    checks.append(("phase at f_c is -45 degrees", abs(float(L.phase_deg(fc, fc)) + 45.0) < 1e-9))
    checks.append(("roll-off far above f_c is -20 dB per decade (within 0.1 dB)", abs(L.rolloff_db_per_decade(100.0, 5000.0) + 20.0) < 0.1))
    checks.append(("DC (f = 0) passes unchanged: gain 1, 0 dB, phase 0", float(L.gain(0.0, fc)) == 1.0 and float(L.phase_deg(0.0, fc)) == 0.0))
    checks.append(("design: 100 nF and 100 Hz give R = 15.915 kohm, nearest stock value 16 kohm",
                   abs(L.design_R(100.0, 100e-9) - 15915.5) < 1.0 and L.nearest_e24(15.915) == 16.0))
    checks.append(("nearest_e24 edge cases: 10 stays 10, 9.99 becomes 10, 950 becomes 910 or 1000 (nearest)",
                   L.nearest_e24(10.0) == 10.0 and L.nearest_e24(9.99) == 10.0 and L.nearest_e24(950.0) in (910.0, 1000.0)))
    checks.append(("hand calculation: a 33 kohm and 1 uF filter removes 20.35 dB of 50 Hz hum",
                   abs(L.hum_removed_db(L.cutoff_hz(33e3, 1e-6)) - 20.35) < 0.01))
    g0, fl = L.loaded_rc(16e3, 100e-9, 16e3)
    checks.append(("a load equal to R halves the DC gain and doubles the cutoff", abs(g0 - 0.5) < 1e-12 and abs(fl / fc - 2.0) < 1e-9))
    g0b, flb = L.loaded_rc(16e3, 100e-9, 1e12)
    checks.append(("a huge load changes nothing (gain 1, same cutoff)", abs(g0b - 1.0) < 1e-6 and abs(flb / fc - 1.0) < 1e-6))
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
