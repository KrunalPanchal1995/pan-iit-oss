"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R = 8.314462618
    # worked example: Ea = 80 kJ/mol, n = 0: k(1200 K) / k(1000 K) = exp(Ea/R * (1/1000 - 1/1200)) = 4.97
    A = L.prefactor_from(10.0, 0.0, 80e3)
    ratio = float(L.arrhenius(1200.0, A, 0.0, 80e3) / L.arrhenius(1000.0, A, 0.0, 80e3))
    hand = float(np.exp(80e3 / R * (1 / 1000 - 1 / 1200)))
    checks.append((f"worked example: k(1200 K) / k(1000 K) = {hand:.2f} for Ea = 80 kJ/mol (got {ratio:.2f})",
                   abs(ratio - hand) < 1e-9 and abs(ratio - 4.97) < 0.01))
    checks.append(("prefactor_from reproduces k at the reference temperature", abs(float(L.arrhenius(1000.0, A, 0.0, 80e3)) - 10.0) < 1e-9))
    checks.append(("a larger Ea makes k fall faster as T falls",
                   float(L.arrhenius(800.0, L.prefactor_from(10.0, 0.0, 160e3), 0.0, 160e3)) < float(L.arrhenius(800.0, L.prefactor_from(10.0, 0.0, 40e3), 0.0, 40e3))))
    # straight line in 1000/T gives Ea back
    T = np.linspace(600, 2000, 8)
    A2, Ea2 = L.fit_arrhenius(T, L.arrhenius(T, A, 0.0, 80e3))
    checks.append((f"noise-free line fit returns Ea = 80 kJ/mol (got {Ea2 / 1000:.3f})", abs(Ea2 - 80e3) < 1.0 and abs(A2 / A - 1) < 1e-6))
    A3, Ea3 = L.fit_arrhenius(T, L.arrhenius(T, 2.0, 1.5, 50e3), n=1.5)
    checks.append(("fit with a temperature exponent n = 1.5 returns Ea = 50 kJ/mol", abs(Ea3 - 50e3) < 1.0))
    # edge: T^n with n = 0 reduces to the simple form
    checks.append(("edge: n = 0 gives A exp(-Ea/RT)", abs(float(L.arrhenius(1000.0, 5.0, 0.0, 30e3)) - 5.0 * np.exp(-30e3 / (R * 1000.0))) < 1e-12))

    # toy ignition delay by hand at 1000 K: g = 30 - 10 = 20, tau = ln(1 + 20 / 0.004) / 20 = ln(5001)/20
    hand_tau = np.log(5001.0) / 20.0
    checks.append((f"hand calculation: tau at 1000 K = ln(5001)/20 = {hand_tau:.4f} s", abs(float(L.tau_approx(1000.0)) - hand_tau) < 1e-9))
    checks.append(("hotter gives shorter ignition delay", bool(np.all(np.diff(L.tau_approx(np.linspace(900, 1400, 6))) < 0))))
    checks.append(("edge: no ignition (nan) when k2 F0 <= k3", bool(np.isnan(L.tau_approx(900.0, 1.0, (1.0, 0.1, 1.0))))))

    # finite-difference sensitivity equals calculus
    Tt = np.array([900.0, 1100.0, 1400.0])
    gap = max(float(np.abs(L.sensitivity(Tt, i) - L.sensitivity_exact(Tt, i)).max()) for i in range(3))
    checks.append((f"finite-difference sensitivities match calculus (largest gap {gap:.1e})", gap < 1e-3))
    # doubling k2 at 1000 K: the sensitivity predicts a shorter delay; check with a direct recomputation
    s2 = float(L.sensitivity(1000.0, 1))
    direct = (np.log(L.tau_approx(1000.0, 1.0, (1.0, 1.01, 1.0))) - np.log(L.tau_approx(1000.0, 1.0))) / np.log(1.01)
    checks.append((f"sensitivity to k2 at 1000 K is {s2:.3f} (a 1 percent faster k2 gives about {abs(s2):.2f} percent shorter tau)",
                   s2 < -1.0 and abs(direct - s2) < 0.05))
    checks.append(("signs: faster k1 and k2 shorten tau, faster k3 lengthens it",
                   float(L.sensitivity(1000.0, 0)) < 0 and float(L.sensitivity(1000.0, 1)) < 0 and float(L.sensitivity(1000.0, 2)) > 0))

    # design
    wide = L.design_std([900, 1400])
    narrow = L.design_std([1300, 1400])
    checks.append((f"design: temperatures 900 and 1400 K pin ln s2 to {wide[1]:.3f}, far better than 1300 and 1400 K ({narrow[1]:.3f})", wide[1] < narrow[1] / 10))
    checks.append(("design: ln s1 is always less well known than ln s2", wide[0] > wide[1] and narrow[0] > narrow[1]))
    more = L.design_std(np.linspace(900, 1400, 8))
    checks.append(("more experiments reduce the uncertainty", bool(np.all(more < wide))))
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
