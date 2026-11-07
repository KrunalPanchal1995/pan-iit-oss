"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    t = L.transmission(1.0, 2.0, 0.5)
    checks.append((f"worked example: T = 0.0236 for E = 1 eV, V0 = 2 eV, a = 0.5 nm (got {t:.4f})", abs(t - 0.02355) < 1e-4))
    checks.append((f"worked example: the thick-barrier formula gives 0.0238, within 2 percent (got {L.transmission_thick(1.0, 2.0, 0.5):.4f})", abs(L.transmission_thick(1.0, 2.0, 0.5) / t - 1) < 0.02))
    checks.append(("hbar^2 / (2 m) = 0.0381 eV nm^2", abs(L.HB2M - 0.03810) < 1e-4))
    # validation 1: the transfer matrix reproduces the exact formula (one flat slice) for energies below, at and above the barrier
    worst = 0.0
    for e in np.linspace(0.1, 5.0, 25):
        for a in (0.1, 0.5, 1.2):
            x, y = L.transmission(e, 2.0, a), L.transfer_matrix_t(e, [(2.0, a)])
            worst = max(worst, abs(x - y) / x)
    checks.append((f"validation: the transfer matrix equals the exact formula for 75 cases (worst relative difference {worst:.1e})", worst < 1e-9))
    checks.append(("validation: cutting a flat barrier into 50 equal slices changes nothing", abs(L.transfer_matrix_t(1.0, [(2.0, 0.5 / 50)] * 50) - t) < 1e-9))
    checks.append(("validation: at E = V0 the exact limit agrees with the transfer matrix", abs(L.transmission(2.0, 2.0, 0.5) / L.transfer_matrix_t(2.0, [(2.0, 0.5)]) - 1) < 1e-3))
    checks.append(("validation: above the barrier, T = 1 when a whole number of half wavelengths fit in it",
                   abs(L.transmission(2.0 + L.HB2M * (np.pi / 0.5) ** 2, 2.0, 0.5) - 1) < 1e-9))
    checks.append(("a barrier of zero width lets everything through", abs(L.transmission(1.0, 2.0, 0.0) - 1) < 1e-12))
    checks.append(("T always lies between 0 and 1", all(0 <= L.transmission(e, v, a) <= 1 for e in (0.1, 1, 2, 5) for v in (0.5, 2, 4) for a in (0.0, 0.2, 1.0))))
    checks.append(("T falls with the width and rises with the energy for E below V0",
                   L.transmission(1, 2, 0.8) < L.transmission(1, 2, 0.5) < L.transmission(1, 2, 0.2) and L.transmission(0.5, 2, 0.5) < L.transmission(1, 2, 0.5) < L.transmission(1.5, 2, 0.5)))
    checks.append(("exponential law: each extra 0.1 nm of width cuts the thick-barrier T by the same factor exp(-2 kappa 0.1)",
                   abs(L.transmission_thick(1, 2, 0.7) / L.transmission_thick(1, 2, 0.6) - np.exp(-2 * np.sqrt(1 / L.HB2M) * 0.1)) < 1e-12))
    def parabola(a):
        return lambda x: 2.0 * (1 - ((x - a / 2) / (a / 2)) ** 2)
    ratios = []
    for a in (0.3, 0.5, 0.8, 1.2):
        slices = [(parabola(a)((j + 0.5) * a / 400), a / 400) for j in range(400)]
        ratios.append(L.transfer_matrix_t(1.0, slices) / L.wkb_transmission(1.0, parabola(a), a))
    checks.append((f"validation: the WKB estimate improves for wider smooth barriers (transfer matrix / WKB = {ratios[0]:.2f}, {ratios[1]:.2f}, {ratios[2]:.2f}, {ratios[3]:.2f})",
                   all(x > y for x, y in zip(ratios, ratios[1:]))))
    checks.append(("validation: for the 1.2 nm parabolic barrier WKB is within a factor 1.5 of the transfer matrix", ratios[3] < 1.5))
    checks.append((f"worked example: question B gives T = 9.79e-4 (got {L.transmission(0.5, 1.5, 0.8):.2e})", abs(L.transmission(0.5, 1.5, 0.8) / 9.79e-4 - 1) < 2e-3))
    r = L.stm_current_ratio(4.5, 0.1)
    checks.append((f"worked example: retracting an STM tip by 0.1 nm cuts the current to 0.114 of its value, about 1 in 8.8 (got {r:.3f})", abs(r - 0.114) < 0.001))
    w = L.min_width_nm(0.5, 3.0, 1e-9)
    checks.append((f"design: the least width with T of at most 1e-9 for E = 0.5 eV, V0 = 3 eV is 1.33 nm (got {w:.3f})", abs(w - 1.328) < 0.002 and L.transmission(0.5, 3.0, w) <= 1.0000001e-9))
    checks.append(("design: 1.30 nm leaks too much and 1.40 nm is enough", L.transmission(0.5, 3.0, 1.30) > 1e-9 > L.transmission(0.5, 3.0, 1.40)))
    for bad, label in ((lambda: L.transmission(0.0, 2.0, 0.5), "E = 0"), (lambda: L.transmission(1.0, -2.0, 0.5), "a negative barrier height"), (lambda: L.transmission(1.0, 2.0, -0.1), "a negative width"),
                       (lambda: L.transfer_matrix_t(0.0, [(2.0, 0.5)]), "a transfer matrix with E = 0")):
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
