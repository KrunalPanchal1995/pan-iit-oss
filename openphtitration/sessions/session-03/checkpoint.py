"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    pka = L.PKA_ACETIC
    # the root finder itself
    checks.append(("bisection finds sqrt(2) as the root of x^2 - 2", abs(L.bisect(lambda x: x * x - 2.0, 0.0, 2.0) - np.sqrt(2.0)) < 1e-9))
    try:
        L.bisect(lambda x: x * x + 1.0, -1.0, 1.0)
        raised = False
    except ValueError:
        raised = True
    checks.append(("bisection refuses an interval without a sign change", raised))

    # limit 1: strong acid, closed form from Session 2
    def strong_exact(Ca, Va, Cb, Vb):
        x = (Ca * Va - Cb * Vb) / (Va + Vb)
        h = (x + np.sqrt(x * x + 4e-14)) / 2 if x >= 0 else 2e-14 / (-x + np.sqrt(x * x + 4e-14))
        return -np.log10(h)
    checks.append(("limit: with pka=None the solver equals the strong-acid formula",
                   all(abs(L.weak_ph(0.1, 25.0, 0.1, v, None) - strong_exact(0.1, 25.0, 0.1, v)) < 1e-6 for v in (0.0, 10.0, 24.9, 25.0, 25.1, 40.0))))
    # limit 2: weak acid alone, quadratic formula
    ka = 1.8e-5
    x = (-ka + np.sqrt(ka * ka + 4 * ka * 0.1)) / 2
    checks.append((f"limit: 0.1 M acetic acid alone has pH {-np.log10(x):.3f} (quadratic formula)", abs(L.pure_weak_acid_ph(0.1, pka) - (-np.log10(x))) < 1e-6))
    # the solution satisfies the charge balance
    ph = L.weak_ph(0.1, 25.0, 0.1, 17.0, pka)
    checks.append(("the solved pH makes the charge residual zero", abs(L.charge_residual(ph, 0.1 * 25 / 42, 0.1 * 17 / 42, pka)) < 1e-10))

    # worked example: 10 mL of base, Henderson-Hasselbalch against the exact solution
    hh = L.henderson_hasselbalch(0.1, 25.0, 0.1, 10.0, pka)
    ex = L.weak_ph(0.1, 25.0, 0.1, 10.0, pka)
    checks.append((f"worked example: 10 mL of base gives HH pH {hh:.3f} = pKa + log10(1.0/1.5); exact {ex:.3f}",
                   abs(hh - (pka + np.log10(1.0 / 1.5))) < 1e-12 and abs(hh - ex) < 0.01))
    checks.append(("Henderson-Hasselbalch is within 0.01 of exact from 5 to 24.5 mL",
                   all(abs(L.henderson_hasselbalch(0.1, 25.0, 0.1, v, pka) - L.weak_ph(0.1, 25.0, 0.1, v, pka)) < 0.01 for v in (5.0, 10.0, 12.5, 20.0, 24.5))))
    checks.append(("but not near the start: at 1 mL the difference exceeds 0.03",
                   abs(L.henderson_hasselbalch(0.1, 25.0, 0.1, 1.0, pka) - L.weak_ph(0.1, 25.0, 0.1, 1.0, pka)) > 0.03))
    checks.append(("half-equivalence pH equals pKa (within 0.005)", abs(L.weak_ph(0.1, 25.0, 0.1, 12.5, pka) - pka) < 0.005))
    # equivalence pH of a weak acid: only acetate left, pOH = -log10(sqrt(Kb C))
    kb = 1e-14 / ka
    expect = 14 + np.log10(np.sqrt(kb * 0.05))
    pe = L.weak_ph(0.1, 25.0, 0.1, 25.0, pka)
    checks.append((f"equivalence pH is above 7 ({pe:.2f}) and matches sqrt(Kb C) ({expect:.2f})", pe > 7.5 and abs(pe - expect) < 0.01))
    checks.append(("weak acid starts higher in pH than a strong acid of equal concentration", L.weak_ph(0.1, 25.0, 0.1, 0.0, pka) > L.weak_ph(0.1, 25.0, 0.1, 0.0, None) + 1.5))
    v = np.linspace(0, 50, 101)
    ph_arr = np.array([L.weak_ph(0.1, 25.0, 0.1, t, pka) for t in v])
    checks.append(("the weak-acid curve rises monotonically and stays finite", bool(np.all(np.isfinite(ph_arr)) and np.all(np.diff(ph_arr) > 0))))

    # buffer capacity
    Ct = 0.05
    h = 10 ** (-pka)
    na = Ct * 1.8e-5 / (1.8e-5 + h) + 1e-14 / h - h
    bf, bn = L.beta_formula(pka, Ct, pka), L.beta_numeric(Ct, na, pka)
    checks.append(("buffer capacity: formula equals the numerical derivative (0.1 percent)", abs(bf - bn) / bf < 1e-3))
    checks.append(("buffer capacity at pH = pKa is ln(10) Ct / 4 (0.5 percent)", abs(bf - np.log(10) * Ct / 4) / bf < 5e-3))
    checks.append(("buffer capacity is lower away from pKa", L.beta_formula(pka + 2.0, Ct, pka) < 0.2 * bf))

    # noise and the derivative peak
    vc, pc = L.make_data(0.1, 25.0, 0.1, pka, 40.0, 0.2)
    checks.append(("noise-free derivative peak is within 0.01 mL of Ve", abs(L.find_equivalence(vc, pc) - 25.0) < 0.01))
    errs = []
    for s in range(60):
        vn, pn = L.make_data(0.1, 25.0, 0.1, pka, 40.0, 0.2, 0.03, 0.02, seed=900 + s)
        errs.append(L.find_equivalence(vn, pn) - 25.0)
    errs = np.array(errs)
    checks.append((f"with noise the peak is unbiased (mean {errs.mean():+.3f} mL) and scatter {errs.std():.3f} mL is under 0.1 mL",
                   abs(errs.mean()) < 0.03 and errs.std() < 0.1))
    perm = np.random.default_rng(3).permutation(vc.size)
    checks.append(("find_equivalence does not depend on the order of the readings", abs(L.find_equivalence(vc[perm], pc[perm]) - L.find_equivalence(vc, pc)) < 1e-9))

    # sensitivity and failure case
    jump = lambda c: L.weak_ph(c, 25.0, c, 25.25, pka) - L.weak_ph(c, 25.0, c, 24.75, pka)
    checks.append(("the jump across the equivalence point shrinks as the acid gets more dilute", jump(0.1) > jump(0.01) > jump(0.001)))
    checks.append(("failure case: 1e-8 mol/L HCl, naive pH 8 is wrong, with water the pH is below 7",
                   abs(L.naive_strong_ph(1e-8) - 8.0) < 1e-9 and L.solve_ph(1e-8, 0.0, None) < 7.0))
    checks.append(("1e-7 mol/L HCl has pH 6.79 (not 7)", abs(L.solve_ph(1e-7, 0.0, None) - 6.791) < 0.002))

    # mini-project: vinegar
    c_true = 50.0 / 60.05
    ve_true = L.equivalence_volume(c_true / 10.0, 25.0, 0.1)
    vn, pn = L.make_data(c_true / 10.0, 25.0, 0.1, pka, 35.0, 0.2, 0.03, 0.02, seed=7)
    c_est = L.vinegar_concentration(L.find_equivalence(vn, pn))
    checks.append((f"mini-project: 5 g/100 mL vinegar is {c_true:.3f} mol/L and needs {ve_true:.2f} mL of 0.1 M NaOH after 1:10 dilution",
                   abs(c_true - 0.8326) < 1e-3 and abs(ve_true - 20.816) < 0.01))
    checks.append((f"mini-project: the noisy run recovers {c_est:.3f} mol/L, within 2 percent", abs(c_est / c_true - 1) < 0.02))
    checks.append(("vinegar_percent turns 0.8326 mol/L back into 5.0 g/100 mL", abs(L.vinegar_percent(c_true) - 5.0) < 1e-9))
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
