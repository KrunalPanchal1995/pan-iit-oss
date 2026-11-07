"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    T = np.array([600.0, 700.0, 800.0, 900.0, 1000.0])
    checks.append(("worked example: Sxx of 1000/T for 600..1000 K step 100 is 0.2788", abs(L.sxx(T) - 0.2788) < 0.0001))
    checks.append(("worked example: SE(Ea) = 8.3145 * 0.05 / sqrt(0.2788) = 0.787 kJ/mol", abs(L.ea_se(T, 0.05) - 0.787) < 0.001))
    A, Ea = L.fit_arrhenius(T, L.synthetic(T, 0.05, seed=1))
    checks.append(("worked example: seed 1 gives Ea = 149.70 kJ/mol and A = 9.65e12 per s", abs(Ea - 149.70) < 0.01 and abs(A / 9.65e12 - 1.0) < 0.002))
    checks.append(("that Ea is within 2 standard errors of the true 150", abs(Ea - 150.0) < 2 * L.ea_se(T, 0.05)))
    A0, E0 = L.fit_arrhenius([500.0, 1000.0], L.arrhenius_k([500.0, 1000.0]))
    checks.append(("noise-free two-point fit returns 150 kJ/mol and 1e13", abs(E0 - 150.0) < 1e-6 and abs(A0 / 1e13 - 1.0) < 1e-9))
    A1, E1 = L.fit_arrhenius(T, L.synthetic(T, 0.05, seed=1), sigma_ln=np.full(5, 0.05))
    checks.append(("equal weights change nothing", abs(E1 - Ea) < 1e-9 and abs(A1 / A - 1.0) < 1e-9))
    wide = L.even_in_inverse_T(500, 1500, 6)
    narrow = L.even_in_inverse_T(850, 1000, 6)
    checks.append(("even_in_inverse_T includes both end temperatures", abs(wide[0] - 1500) < 1e-9 and abs(wide[-1] - 500) < 1e-9))
    checks.append(("wide window (500-1500 K): Sxx 1.244 and SE(Ea) 0.37 kJ/mol", abs(L.sxx(wide) - 1.2444) < 1e-3 and abs(L.ea_se(wide, 0.05) - 0.373) < 0.001))
    checks.append(("narrow window (850-1000 K): Sxx 0.0218 and SE(Ea) 2.82 kJ/mol", abs(L.sxx(narrow) - 0.0218) < 1e-4 and abs(L.ea_se(narrow, 0.05) - 2.82) < 0.01))
    checks.append(("the narrow window is 7.6 times worse than the wide one", abs(L.ea_se(narrow, 0.05) / L.ea_se(wide, 0.05) - 7.55) < 0.05))
    sd, mean = L.simulated_ea_std(wide, 0.05)
    checks.append(("simulation: spread of Ea (0.37) matches theory within 5 percent, mean unbiased", abs(sd / L.ea_se(wide, 0.05) - 1.0) < 0.05 and abs(mean - 150.0) < 0.02))
    sd2, _ = L.simulated_ea_std(narrow, 0.05)
    checks.append(("simulation: narrow-window spread matches theory within 5 percent", abs(sd2 / L.ea_se(narrow, 0.05) - 1.0) < 0.05))
    ends = np.array([500.0, 500.0, 500.0, 1500.0, 1500.0, 1500.0])
    checks.append(("design: three points at each end give SE 0.255, 32 percent below the even design", abs(L.ea_se(ends, 0.05) - 0.2546) < 0.001 and abs(1 - L.ea_se(ends, 0.05) / L.ea_se(wide, 0.05) - 0.317) < 0.005))
    T2 = np.linspace(500.0, 1500.0, 12)
    A2, n2, E2 = L.fit_modified(T2, L.arrhenius_k(T2, 1e8, 100.0, 1.5))
    checks.append(("modified Arrhenius recovers A = 1e8, n = 1.5, Ea = 100 kJ/mol", abs(A2 / 1e8 - 1) < 1e-6 and abs(n2 - 1.5) < 1e-8 and abs(E2 - 100.0) < 1e-6))
    checks.append(("n = 0 reduces the modified form to the plain law", abs(float(L.arrhenius_k(800.0, 1e13, 150.0, 0.0)) / 1607.67 - 1) < 1e-4))
    xs = 1000.0 / T
    checks.append(("hand calculation: mean of 1000/T is 1.2913", abs(xs.mean() - 1.2913) < 1e-4))
    checks.append(("doubling the error doubles SE(Ea): sigma 0.10 gives 1.57 kJ/mol", abs(L.ea_se(T, 0.10) - 1.575) < 0.001))
    Tm = np.linspace(500.0, 1500.0, 12)
    Mx = np.column_stack([np.ones(12), np.log(Tm), -1000.0 / Tm])
    Cv = np.linalg.inv(Mx.T @ Mx)
    checks.append(("modified form: ln A and n are almost perfectly anti-correlated (r = -0.9998)", abs(Cv[0, 1] / np.sqrt(Cv[0, 0] * Cv[1, 1]) + 0.9998) < 0.0001))
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
