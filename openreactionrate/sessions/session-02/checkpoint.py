"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("both laws start at A0", abs(float(L.conc_first(0, 2.0, 0.1)) - 2.0) < 1e-12 and abs(float(L.conc_second(0, 2.0, 0.1)) - 2.0) < 1e-12))
    h1 = L.half_life(1, 1.0, 0.03)
    checks.append(("first-order half-life is ln 2 / k = 23.1 s", abs(h1 - 23.105) < 1e-2))
    checks.append(("first-order half-life does not depend on A0", abs(L.half_life(1, 5.0, 0.03) - h1) < 1e-12))
    checks.append(("second-order [A] at its half-life is A0/2", abs(float(L.conc_second(L.half_life(2, 0.5, 0.03), 0.5, 0.03)) - 0.25) < 1e-12))
    checks.append(("second-order half-life doubles when A0 is halved", abs(L.half_life(2, 0.5, 0.03) - 2 * L.half_life(2, 1.0, 0.03)) < 1e-12))
    # worked example: design problem, 90 percent conversion
    t1 = L.time_to_conversion(1, 1.0, 0.02, 0.9)
    checks.append((f"worked example: first order, k = 0.02 1/s, 90 percent takes ln(10)/k = 115.1 s (got {t1:.1f})", abs(t1 - 115.13) < 0.05))
    checks.append(("the conversion time agrees with the formula for [A]", abs(float(L.conc_first(t1, 1.0, 0.02)) - 0.1) < 1e-9))
    t2 = L.time_to_conversion(2, 1.0, 0.02, 0.9)
    checks.append(("second order, A0 = 1, k = 0.02: 90 percent takes 9/(k A0) = 450 s", abs(t2 - 450.0) < 1e-9 and abs(float(L.conc_second(t2, 1.0, 0.02)) - 0.1) < 1e-9))
    # reading the order
    tt = np.linspace(0, 100, 12)
    checks.append(("first-order data is read as order 1", L.order_from_data(tt, L.conc_first(tt, 1.0, 0.03))[0] == 1))
    checks.append(("second-order data is read as order 2", L.order_from_data(tt, L.conc_second(tt, 1.0, 0.03))[0] == 2))
    rng = np.random.default_rng(3)
    noisy = L.conc_second(tt, 1.0, 0.03) * (1 + 0.01 * rng.standard_normal(tt.size))
    checks.append(("second-order data with 1 percent noise is still read as order 2", L.order_from_data(tt, noisy)[0] == 2))
    # Arrhenius and catalyst
    ratio = float(L.k_at_temperature(1.0, 50000.0, 310.0))
    checks.append((f"Ea = 50 kJ/mol: 10 K warmer is about 1.9 times faster (got {ratio:.2f})", abs(ratio - 1.909) < 0.01))
    checks.append(("k_at_temperature returns k_ref at T = T_ref", abs(float(L.k_at_temperature(0.02, 50000.0, 300.0)) - 0.02) < 1e-15))
    s = L.catalyst_speedup(20000.0, 300.0)
    checks.append((f"hand calculation: dEa = 20 kJ/mol at 300 K gives exp(8.018) = 3037 times (got {s:.0f})", abs(s - np.exp(20000 / (8.314 * 300))) < 1e-9 and abs(s - 3037) < 1))
    checks.append(("a catalyst with dEa = 0 changes nothing", abs(L.catalyst_speedup(0.0, 300.0) - 1.0) < 1e-15))
    checks.append(("speed-up from a catalyst is smaller at higher temperature", L.catalyst_speedup(20000, 350) < L.catalyst_speedup(20000, 300)))
    a1 = float(L.arrhenius_k(1e10, 50000.0, 300.0))
    checks.append(("arrhenius_k and k_at_temperature agree", abs(float(L.arrhenius_k(1e10, 50000.0, 310.0)) / a1 - ratio) < 1e-9))
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
