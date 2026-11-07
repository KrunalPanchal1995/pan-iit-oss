"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    e = L.coulomb_field(1e-9, 0.5)
    checks.append((f"hand calculation: 1 nC at 0.5 m gives 35.96 V/m (got {e:.2f})", abs(e - 35.96) < 0.01))
    checks.append(("doubling the distance makes the field 4 times weaker", abs(L.coulomb_field(1e-9, 1.0) * 4 - L.coulomb_field(1e-9, 0.5)) < 1e-9))
    checks.append(("field size does not depend on the sign of the charge", L.coulomb_field(-2e-9, 1.0) == L.coulomb_field(2e-9, 1.0)))

    # superposition on a grid: the dipole grid equals the sum of the two single-charge fields
    xs = np.linspace(-1, 1, 21) + 0.013
    X, Y = np.meshgrid(xs, xs)
    a = L.point_field(1e-9, (-0.1, 0.0), X, Y)
    b = L.point_field(-1e-9, (0.1, 0.0), X, Y)
    Ex, Ey = L.dipole_grid(1e-9, 0.2, xs, xs)
    checks.append(("superposition: dipole grid = field of +q plus field of -q", np.allclose(Ex, a[0] + b[0]) and np.allclose(Ey, a[1] + b[1])))
    checks.append(("dipole grid is symmetric: Ex(x, y) = Ex(x, -y) on a symmetric grid",
                   np.allclose(L.dipole_grid(1e-9, 0.2, np.linspace(-1, 1, 21), np.linspace(-1, 1, 21))[0],
                               L.dipole_grid(1e-9, 0.2, np.linspace(-1, 1, 21), np.linspace(-1, 1, 21))[0][::-1, :])))
    ratio = L.dipole_axis_far(1e-9, 0.1, 2.0) / L.dipole_axis_exact(1e-9, 0.1, 2.0)
    checks.append(("far dipole field 2kqd/r^3 agrees with the exact sum to 0.2 percent at r = 20 d", abs(ratio - 1) < 0.002))
    checks.append(("dipole falls as 1/r^3: doubling r divides the field by about 8",
                   abs(L.dipole_axis_exact(1e-9, 0.01, 10.0) / L.dipole_axis_exact(1e-9, 0.01, 20.0) - 8) < 0.01))

    # worked example: 2.4 GHz wifi
    lam = L.wavelength(2.4e9)
    k, w = L.wavenumber(lam), L.angular_frequency(2.4e9)
    checks.append((f"worked example: wifi wavelength is 12.5 cm (got {lam * 100:.2f})", abs(lam * 100 - 12.49) < 0.01))
    checks.append((f"worked example: k = 50.3 rad/m (got {k:.1f}) and w = 1.508e10 rad/s", abs(k - 50.3) < 0.1 and abs(w - 1.508e10) < 1e7))
    checks.append(("wave speed w/k equals c", abs(L.phase_speed(w, k) - L.C) < 1))
    checks.append(("a crest moves at v: y is the same at (x, t) and (x + v dt, t + dt)",
                   abs(L.wave_y(0.03, 1e-10, 1.0, k, w) - L.wave_y(0.03 + L.C * 1e-11, 1e-10 + 1e-11, 1.0, k, w)) < 1e-6))
    checks.append(("the wave repeats after one wavelength", abs(L.wave_y(0.01, 0.0, 2.0, k, w) - L.wave_y(0.01 + lam, 0.0, 2.0, k, w)) < 1e-9))

    # design problem: FM antenna
    checks.append((f"design: half-wave dipole for 100 MHz is 1.5 m (got {L.half_wave_length(100e6):.3f})", abs(L.half_wave_length(100e6) - 1.5) < 0.005))
    checks.append(("design: wifi dipole is 6.2 cm", abs(L.half_wave_length(2.4e9) - 0.0625) < 0.0005))
    checks.append(("antenna length is inversely proportional to frequency", abs(L.half_wave_length(200e6) * 2 - L.half_wave_length(100e6)) < 1e-9))

    checks.append(("polarisation: aligned receiver gets everything, crossed gets nothing, 45 degrees gets half",
                   L.received_fraction(0) == 1.0 and abs(L.received_fraction(90)) < 1e-12 and abs(L.received_fraction(45) - 0.5) < 1e-12))
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
