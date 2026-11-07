"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    e = [L.energy_ev(n, 1.0) for n in (1, 2, 3)]
    checks.append((f"worked example: E1 = 0.376 eV for L = 1 nm (got {e[0]:.4f})", abs(e[0] - 0.3760) < 1e-4))
    checks.append((f"worked example: E2 = 1.504 eV and E3 = 3.384 eV (got {e[1]:.3f}, {e[2]:.3f})", abs(e[1] - 1.5041) < 1e-3 and abs(e[2] - 3.3843) < 1e-3))
    checks.append(("the levels grow as n squared: E2 = 4 E1 and E3 = 9 E1", abs(e[1] / e[0] - 4) < 1e-12 and abs(e[2] / e[0] - 9) < 1e-12))
    checks.append(("the levels grow as 1 / L^2: halving the width multiplies the energy by 4", abs(L.energy_ev(1, 0.5) / L.energy_ev(1, 1.0) - 4) < 1e-12))
    checks.append(("a heavier particle has lower levels: doubling the mass halves the energy", abs(L.energy_ev(1, 1.0, 2 * L.ME) / L.energy_ev(1, 1.0) - 0.5) < 1e-12))
    checks.append(("the lowest energy is never zero, even in a very wide box", L.energy_ev(1, 1000.0) > 0))
    lam = L.photon_wavelength_nm(2, 1, 1.0)
    checks.append((f"worked example: the jump 2 to 1 in a 1 nm box emits 1099 nm (got {lam:.0f})", abs(lam - 1099) < 1))
    checks.append(("the wavelength obeys lambda = 1239.84 nm eV / (E_photon in eV)", abs(lam - 1239.84198 / (L.energy_ev(2, 1.0) - L.energy_ev(1, 1.0))) < 1e-3))
    checks.append((f"worked example: P(middle third) is 0.609 for n = 1 and 0.196 for n = 2 (got {L.probability_between(1, 1 / 3, 2 / 3):.3f}, {L.probability_between(2, 1 / 3, 2 / 3):.3f})",
                   abs(L.probability_between(1, 1 / 3, 2 / 3) - 0.6090) < 1e-3 and abs(L.probability_between(2, 1 / 3, 2 / 3) - 0.1955) < 1e-3))
    checks.append(("the particle is somewhere in the box: P(0 to 1) = 1 for several levels", all(abs(L.probability_between(n, 0, 1) - 1) < 1e-12 for n in (1, 2, 3, 7))))
    trap = getattr(np, "trapezoid", None) or np.trapz        # the name changed between NumPy versions
    u = np.linspace(0, 1, 20001)
    checks.append(("the density integrates to 1 (trapezoid rule)", all(abs(trap(L.density_times_l(n, u), u) - 1) < 1e-6 for n in (1, 2, 3, 4))))
    checks.append(("the exact probability agrees with a numerical integral of the density",
                   abs(L.probability_between(3, 0.1, 0.4) - trap(L.density_times_l(3, np.linspace(0.1, 0.4, 20001)), np.linspace(0.1, 0.4, 20001))) < 1e-6))
    checks.append(("level n = 2 has a node at the centre, level n = 1 has its maximum there", abs(L.density_times_l(2, 0.5)) < 1e-12 and abs(L.density_times_l(1, 0.5) - 2) < 1e-12))
    w = L.width_for_wavelength_nm(2, 1, 530)
    checks.append((f"design: a green 530 nm photon from the jump 2 to 1 needs a box of 0.694 nm (got {w:.3f})", abs(w - 0.694) < 1e-3))
    checks.append(("design: the width and the wavelength convert back and forth (round trip)", abs(L.photon_wavelength_nm(2, 1, w) - 530) < 1e-6))
    checks.append(("design: a 0.70 nm box gives a wavelength between 500 and 560 nm", 500 <= L.photon_wavelength_nm(2, 1, 0.70) <= 560))
    for bad, label in ((lambda: L.energy_ev(0, 1.0), "level 0"), (lambda: L.energy_ev(1.5, 1.0), "a level that is not a whole number"), (lambda: L.energy_ev(1, 0.0), "width 0"),
                       (lambda: L.photon_wavelength_nm(1, 2, 1.0), "a jump upwards"), (lambda: L.probability_between(1, 0.7, 0.2), "u1 above u2")):
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
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
