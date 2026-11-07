"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("NACA 2412 means m = 0.02, p = 0.4, t = 0.12",
                   np.allclose(L.parse_naca("2412"), (0.02, 0.4, 0.12))))
    x = np.linspace(0, 1, 401)
    yc, dyc = L.camber_line(x, 0.02, 0.4)
    checks.append(("camber line peaks at height m = 0.02 at x = p = 0.4 with zero slope",
                   abs(yc.max() - 0.02) < 1e-12 and abs(x[np.argmax(yc)] - 0.4) < 1e-12 and abs(dyc[160]) < 1e-12))
    checks.append(("camber line starts and ends on the chord line", abs(yc[0]) < 1e-15 and abs(yc[-1]) < 1e-15))
    checks.append(("NACA 0012 is 12 % thick (largest 2 yt is 0.120 near x = 0.3)",
                   abs(2 * L.thickness(x, 0.12).max() - 0.12) < 5e-4 and abs(x[np.argmax(L.thickness(x, 0.12))] - 0.3) < 0.01))
    X, Y = L.naca4("0012", 60)
    checks.append(("symmetric outline: lower surface is the mirror of the upper", np.allclose(Y[:61][::-1], -Y[60:])))
    checks.append(("symmetric airfoil: zero-lift angle is 0", abs(L.alpha_zero_lift(0.0, 0.4)) < 1e-12))
    checks.append(("NACA 2412 zero-lift angle is -2.08 degrees (textbook value)", abs(L.alpha_zero_lift(0.02, 0.4) + 2.077) < 2e-3))
    checks.append(("zero-lift angle doubles with double camber (thin theory is linear)",
                   abs(L.alpha_zero_lift(0.04, 0.4) - 2 * L.alpha_zero_lift(0.02, 0.4)) < 1e-9))
    checks.append(("lift slope is 2 pi per radian (0.1097 per degree)",
                   abs((L.cl_thin(5, "2412") - L.cl_thin(4, "2412")) - 2 * np.pi * np.pi / 180) < 1e-12))
    checks.append(("worked example: NACA 2412 at 4 degrees gives CL = 0.666", abs(L.cl_thin(4, "2412") - 0.6664) < 1e-3))
    checks.append(("worked example: CL 0.40 on NACA 2412 needs 1.57 degrees",
                   abs(L.alpha_for_cl(0.40, "2412") - 1.57) < 0.01 and abs(L.cl_thin(L.alpha_for_cl(0.4, "2412"), "2412") - 0.4) < 1e-12))
    k = L.induced_factor(8, 0.8)
    checks.append(("induced-drag factor k = 1 / (pi 0.8 8) = 0.04974", abs(k - 0.04974) < 1e-5))
    cls, ld = L.best_glide(0.025, 8, 0.8)
    cl = np.linspace(0.05, 2, 20001)
    num = cl / L.cd_polar(cl, 0.025, 8, 0.8)
    checks.append(("best L/D 14.18 at CL* 0.709 and it matches a brute-force search",
                   abs(ld - 14.18) < 0.01 and abs(cls - 0.709) < 1e-3 and abs(num.max() - ld) < 1e-6 and abs(cl[np.argmax(num)] - cls) < 1e-3))
    checks.append(("at CL* the induced drag equals the parasite drag", abs(k * cls**2 - 0.025) < 1e-12))
    bad = 0
    for call in (lambda: L.parse_naca("241"), lambda: L.parse_naca("2012"), lambda: L.induced_factor(0, 0.8),
                 lambda: L.induced_factor(8, 1.2)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 4))
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
