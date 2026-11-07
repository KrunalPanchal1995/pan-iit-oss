"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    import numpy as np
    checks = []
    tri = [("fix", 0, 0, 0), ("horiz", 0, 1), ("dist", 0, 1, 4), ("dist", 0, 2, 3), ("dist", 1, 2, 5)]
    p, info = L.solve([(0, 0), (3, 0.5), (0.5, 2)], tri)
    checks.append((f"worked example: the 3-4-5 triangle solves to (0, 0), (4, 0), (0, 3) (got {p.round(3).tolist()})",
                   np.allclose(p, [[0, 0], [4, 0], [0, 3]], atol=1e-6)))
    checks.append((f"worked example: it is fully constrained, 0 degrees of freedom (got {info['dof']})", info["dof"] == 0 and L.status(info) == "fully constrained"))
    checks.append(("validation: the angle at the origin is a right angle although we never said so", abs(np.dot(p[1] - p[0], p[2] - p[0])) < 1e-9))
    pm, _ = L.solve([(0, 0), (3, 0.5), (0.5, -2)], tri)
    checks.append((f"starting below the axis gives the mirror image (0, -3) (got {pm[2].round(3).tolist()})", np.allclose(pm[2], [0, -3], atol=1e-6)))
    _, i2 = L.solve([(0, 0), (3, 0.5), (0.5, 2)], tri[:-1])
    checks.append((f"without the last distance one degree of freedom is left (got {i2['dof']})", i2["dof"] == 1 and "under-constrained" in L.status(i2)))
    _, i3 = L.solve([(0, 0), (3, 0.5), (0.5, 2)], tri + [("perp", 1, 0, 2)])
    checks.append((f"a perpendicular statement that is already true is redundant but consistent (got {i3['redundant']} redundant)", i3["dof"] == 0 and i3["redundant"] == 1))
    try:
        L.solve([(0, 0), (3, 0.5), (0.5, 2)], tri[:4] + [("dist", 1, 2, 8)])
        raised = False
    except ValueError:
        raised = True
    checks.append(("two statements that contradict each other give an error", raised))
    pts, inf = L.build_l_bracket(50, 50, 5)
    checks.append((f"worked example: the L 50 x 50 x 5 is fully constrained (got {inf['dof']} degrees of freedom)", inf["dof"] == 0))
    checks.append((f"worked example: area 475 mm2 (got {L.shoelace_area(pts):.1f})", abs(L.shoelace_area(pts) - 475.0) < 1e-6))
    checks.append((f"worked example: 200 mm long weighs 0.746 kg (got {L.bracket_mass_kg(50, 50, 5, 200):.3f})", abs(L.bracket_mass_kg(50, 50, 5, 200) - 0.7458) < 0.0005))
    ok = True
    for b, h, t in ((50, 50, 5), (60, 40, 10), (80, 30, 4), (100, 100, 15), (30, 90, 2)):
        q, _ = L.build_l_bracket(b, h, t)
        ok &= abs(L.shoelace_area(q) - (b * t + (h - t) * t)) < 1e-6
    checks.append(("validation: the solved area equals b t + (h - t) t for five different brackets (the formula of Session 2)", ok))
    r, _ = L.system(pts.ravel(), L.l_bracket_constraints(50, 50, 5))
    checks.append(("validation: every statement is true at the solution (all residuals below 1e-9)", float(np.abs(r).max()) < 1e-9))
    guess, ok2 = None, True
    for t in np.linspace(2, 15, 14):
        q, _ = L.build_l_bracket(60, 40, float(t), guess)
        guess = q
        ok2 &= abs(L.shoelace_area(q) - (60 * t + (40 - t) * t)) < 1e-6 and q[2][1] > 0
    checks.append(("rebuilding 14 times with the previous solution as the guess keeps the same orientation and the right area", ok2))
    mir = [(x, -y) for x, y in L.ROUGH_L]
    qm, _ = L.build_l_bracket(60, 40, 5, mir)
    checks.append(("a mirrored guess gives the mirrored bracket with the same area", qm[2][1] < 0 and abs(L.shoelace_area(qm) - 475.0) < 1e-6))
    checks.append(("design: t = 5.38 mm keeps a 60 x 40 bracket 200 mm long at or below 0.8 kg and t = 5.39 mm does not",
                   L.bracket_mass_kg(60, 40, 5.38, 200) <= 0.8 < L.bracket_mass_kg(60, 40, 5.39, 200)))
    for bad, label in ((lambda: L.build_l_bracket(50, 50, 60), "a thickness larger than the legs"),
                       (lambda: L.solve([(0, 0), (1, 1)], [("bogus", 0, 1)]), "an unknown kind of statement"),
                       (lambda: L.solve([(0, 0), (1, 1)], [("dist", 0, 1, -2)]), "a negative distance"),
                       (lambda: L.solve([1.0, 2.0, 3.0], [("fix", 0, 0, 0)]), "an odd number of coordinates")):
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
