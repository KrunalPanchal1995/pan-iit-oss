"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    q = L.rotate_about(np.array([[2.0, 1.0]]), np.pi / 2, [1.0, 1.0])
    checks.append(("rotating (2, 1) by 90 degrees about (1, 1) gives (1, 2)", np.allclose(q, [[1.0, 2.0]], atol=1e-9)))
    j = L.arm_joints(0.0, 0.0)
    checks.append(("straight arm reaches 0.55 m along x", np.allclose(j[2], [0.55, 0.0], atol=1e-9)))
    j = L.arm_joints(np.radians(40), np.radians(50))
    checks.append(("worked example: hand at (0.230, 0.443) m", np.allclose(j[2], [0.2298, 0.4428], atol=1e-3)))
    checks.append(("reach formula agrees with the geometry",
                   abs(np.linalg.norm(j[2]) - L.reach(np.radians(50))) < 1e-9))
    ok = True
    for a in np.linspace(-3, 3, 7):
        for b in np.linspace(-2.5, 2.5, 7):
            jj = L.arm_joints(a, b)
            ok &= abs(np.linalg.norm(jj[1] - jj[0]) - L.L1) < 1e-9
            ok &= abs(np.linalg.norm(jj[2] - jj[1]) - L.L2) < 1e-9
    checks.append(("bone lengths never change", bool(ok)))
    checks.append(("longest reach is L1+L2 and shortest is |L1-L2|",
                   abs(L.reach(0.0) - 0.55) < 1e-9 and abs(L.reach(np.pi) - 0.05) < 1e-9))
    sols = L.solve_reach(0.35, 0.20)
    good = len(sols) == 2 and all(np.allclose(L.arm_joints(a, b)[2], [0.35, 0.20], atol=1e-9) for a, b in sols)
    checks.append(("two ways to reach (0.35, 0.20): elbow up and elbow down", bool(good)))
    checks.append(("a target 1 m away is unreachable", L.solve_reach(1.0, 0.0) == []))
    full = L.solve_reach(0.55, 0.0)
    checks.append(("the fully stretched point (0.55, 0) has exactly one solution, b = 0",
                   len(full) == 1 and abs(full[0][1]) < 1e-6 and abs(full[0][0]) < 1e-6))
    folded = L.solve_reach(0.05, 0.0)
    checks.append(("the fully folded point (0.05, 0) has exactly one solution",
                   len(folded) == 1 and np.allclose(L.arm_joints(*folded[0])[2], [0.05, 0.0], atol=1e-9)))
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
