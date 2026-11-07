"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # three-bar bracket, hand calculation at joint C: sin(a) = 1.5/2.5 = 0.6, cos(a) = 0.8
    f, reac = L.bracket(12.0, 2.0, 1.5)
    checks.append(("bracket hand calculation: tie AC = 12/0.6 = +20 kN, strut BC = -20*0.8 = -16 kN",
                   abs(f[0] - 20.0) < 1e-9 and abs(f[1] + 16.0) < 1e-9))
    checks.append(("bracket: the vertical wall bar AB carries zero force", abs(f[2]) < 1e-9))
    rx = {(n, d): v for n, d, v in reac}
    checks.append(("bracket reactions: A gives 12 kN up, A and B balance 16 kN horizontally",
                   abs(rx[(0, 1)] - 12.0) < 1e-9 and abs(rx[(0, 0)] + 16.0) < 1e-9 and abs(rx[(1, 0)] - 16.0) < 1e-9))

    nodes, members, forces, reac = L.warren_example(10.0)
    checks.append(("Warren truss has 7 joints, 11 bars, 3 reactions and m + r = 2 j",
                   len(nodes) == 7 and len(members) == 11 and L.determinacy(11, 3, 7) == "determinate"))
    checks.append(("worked example: the sloping bars carry +-5.77 kN (5 / sin 60)",
                   all(abs(abs(forces[k]) - 5.77) < 0.005 for k in range(5, 11))
                   and abs(5.0 / np.sin(np.radians(60)) - 5.7735) < 1e-3))
    checks.append(("worked example: bottom chord 2.89, 8.66, 2.89 kN (tension) and top chord -5.77, -5.77 kN",
                   np.allclose(forces[:3], [2.887, 8.660, 2.887], atol=0.005) and np.allclose(forces[3:5], -5.774, atol=0.005)))
    rr = {(n, d): v for n, d, v in reac}
    checks.append(("support reactions are 5 kN up at each foot and 0 horizontally",
                   abs(rr[(0, 1)] - 5.0) < 1e-9 and abs(rr[(3, 1)] - 5.0) < 1e-9 and abs(rr[(0, 0)]) < 1e-9))
    fb, ft = L.sections_midspan(10.0)
    checks.append(("method of sections gives the same middle bottom chord (+8.66 kN) and top chord (-5.77 kN)",
                   abs(fb - forces[1]) < 1e-9 and abs(ft - forces[3]) < 1e-9))
    # equilibrium of every joint: sum of member pulls + reaction + load = 0
    res = np.zeros((len(nodes), 2))
    for (i, k), fk in zip(members, forces):
        c = (nodes[k] - nodes[i]) / np.linalg.norm(nodes[k] - nodes[i])
        res[i] += fk * c
        res[k] -= fk * c
    for n, d, v in reac:
        res[n, d] += v
    res[5, 1] -= 10.0
    checks.append(("every joint is in equilibrium (sum Fx = 0 and sum Fy = 0)", np.allclose(res, 0.0, atol=1e-9)))
    # moment equilibrium of the whole truss about the left foot: 10 kN at x = 3 m, reaction 5 kN at x = 6 m
    checks.append(("moments about the left foot balance: 10 * 3 = R_right * 6", abs(10.0 * 3.0 - rr[(3, 1)] * 6.0) < 1e-9))
    checks.append(("linearity: doubling the load doubles every bar force",
                   np.allclose(L.warren_example(20.0)[2], 2 * forces, atol=1e-9)))
    # determinacy classes
    checks.append(("determinacy: one bar removed is a mechanism, one bar added is indeterminate",
                   L.determinacy(10, 3, 7) == "mechanism" and L.determinacy(12, 3, 7) == "indeterminate"))
    checks.append(("a triangle with a pin and a roller is determinate (3 + 3 = 2 * 3)", L.determinacy(3, 3, 3) == "determinate"))
    # design
    checks.append(("worked example: the 8.66 kN bar needs 57.7 mm^2 at 150 MPa",
                   abs(L.required_area(forces[1], 150.0) - 57.735) < 0.01))
    checks.append(("required area is the same for tension and compression of equal size",
                   abs(L.required_area(-8.0, 100.0) - L.required_area(8.0, 100.0)) < 1e-12 and abs(L.required_area(8.0, 100.0) - 80.0) < 1e-9))
    checks.append(("edge: a zero load gives zero force everywhere", np.allclose(L.warren_example(0.0)[2], 0.0)))
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
