"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d = np.radians
    checks.append(("two-link ring area 4 pi L1 L2 = 0.9425 m^2 equals pi (0.55^2 - 0.05^2)",
                   abs(L.annulus_area(0.55, 0.05) - 4 * np.pi * 0.30 * 0.25) < 1e-12 and abs(L.annulus_area(0.55, 0.05) - 0.9425) < 1e-4))
    checks.append(("grid sampling of the two-link ring gives 0.9427 m^2, within 0.2 percent of the formula",
                   abs(L.two_link_area_grid(0.30, 0.25) - L.annulus_area(0.55, 0.05)) < 0.002 * 0.9425))
    checks.append(("hand calculation: L1 = 0.40, L2 = 0.20 gives ring radii 0.60 and 0.20 and area 1.005 m^2",
                   abs(L.annulus_area(0.60, 0.20) - 1.0053) < 1e-3 and abs(L.two_link_area_grid(0.40, 0.20) - 1.0053) < 3e-3))
    checks.append(("forward kinematics: (0, 0, 0) gives (0.70, 0)", np.allclose(L.fk([0, 0, 0]), [0.70, 0.0])))
    q = L.solutions_for_tool((0.45, 0.20), 0.0)
    checks.append(("worked example: tool angle 0 gives (-9.6, 98.6, -89.0) degrees and (77.0, -98.6, 21.7) degrees",
                   len(q) == 2 and np.allclose(np.degrees(q[0]), [-9.59, 98.63, -89.04], atol=0.02)
                   and np.allclose(np.degrees(q[1]), [76.97, -98.63, 21.66], atol=0.02)))
    checks.append(("worked example: cos(q2) = -0.15 for the wrist at (0.30, 0.20)", abs(np.cos(q[0][1]) + 0.15) < 1e-9))
    ok = all(np.allclose(L.fk(s), [0.45, 0.20], atol=1e-9) and abs(L.wrap(sum(s))) < 1e-9 for s in q)
    checks.append(("both solutions put the gripper on the target pointing along +x", bool(ok)))
    checks.append(("a point beyond 0.70 m has no solution and a point at 0.70 m exactly has one",
                   L.solutions_for_tool((0.75, 0.0), 0.0) == [] and len(L.solutions_for_tool((0.70, 0.0), 0.0)) == 1))
    fam = L.solution_family((0.45, 0.20))
    ph = np.degrees([f[0] for f in fam])
    checks.append(("redundancy: 84 arm shapes for one target at 5 degree tool steps, tool directions -80 to 125 degrees",
                   len(fam) == 84 and abs(ph.min() + 80) < 1e-6 and abs(ph.max() - 125) < 1e-6
                   and all(np.allclose(L.fk(f[1:]), [0.45, 0.20], atol=1e-9) for f in fam)))
    checks.append(("with joint limits +-120 degrees only 67 of those shapes remain",
                   len(L.solution_family((0.45, 0.20), limit=d(120))) == 67))
    full = L.reachable_fraction(180)
    checks.append(("no limits: the whole disk of radius 0.70 m (area 1.539 m^2) is reachable",
                   full > 0.999 and abs(np.pi * 0.7 ** 2 - 1.5394) < 1e-3))
    f120, f90 = L.reachable_fraction(120), L.reachable_fraction(90)
    checks.append(("limits +-120 degrees keep 0.892 of the disk and +-90 degrees keep 0.613",
                   abs(f120 - 0.892) < 0.003 and abs(f90 - 0.613) < 0.003))
    checks.append(("limits +-60 degrees keep only 0.246 of the disk", abs(L.reachable_fraction(60) - 0.246) < 0.003))
    checks.append(("limits +-120 degrees: reachable area 1.373 m^2", abs(f120 * np.pi * 0.7 ** 2 - 1.373) < 0.006))
    f125 = L.reachable_fraction(125)
    checks.append(("125 degrees is the first 5-degree step that reaches 0.9 of the disk (0.918)",
                   f120 < 0.9 < f125 and abs(f125 - 0.918) < 0.003))
    checks.append(("longer third link helps: 0.17 m gives 0.906 at +-120 degrees, 0.15 m gives 0.892",
                   abs(L.reachable_fraction(120, np.array([0.30, 0.25, 0.17])) - 0.9064) < 0.003))
    checks.append(("far table corner is 0.716 m from the base", abs(np.hypot(0.70, 0.15) - 0.7159) < 1e-3))
    c70 = L.table_coverage(np.array([0.30, 0.25, 0.15]))
    l72 = np.array([0.30, 0.25, 0.17])
    checks.append(("table coverage: total 0.70 m reaches 0.956 of the grid points, total 0.72 m reaches all",
                   abs(c70 - 0.956) < 0.002 and L.table_coverage(l72) == 1.0))
    checks.append(("with L3 = 0.17 m the table is fully covered at +-105 degrees but not at +-100 (0.974) or +-90 (0.839)",
                   L.table_coverage(l72, 105) == 1.0 and abs(L.table_coverage(l72, 100) - 0.974) < 0.002
                   and abs(L.table_coverage(l72, 90) - 0.839) < 0.002))
    checks.append(("wrap puts angles in (-pi, pi]", abs(L.wrap(3 * np.pi) - np.pi) < 1e-12 and abs(L.wrap(-np.pi) - np.pi) < 1e-12))
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
