"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    p = L.rotation(np.pi / 2) @ np.array([1.0, 0.0])
    checks.append(("90 degrees turns (1, 0) into (0, 1)", np.allclose(p, [0.0, 1.0], atol=1e-9)))
    h = L.hand_position(np.radians(30))
    checks.append(("worked example: 30 degrees puts the hand at (0.866, 0.500)",
                   np.allclose(h, [0.8660, 0.5000], atol=1e-3)))
    lengths = [L.arm_length(L.rotate_points(L.ARM, t)) for t in np.linspace(0, 2 * np.pi, 13)]
    checks.append(("arm length stays 1 for every angle", np.allclose(lengths, 1.0, atol=1e-9)))
    back = L.rotate_points(L.rotate_points(L.ARM, 0.7), -0.7)
    checks.append(("rotating by +a then -a restores the arm", np.allclose(back, L.ARM, atol=1e-9)))
    R = L.rotation(1.1)
    checks.append(("R^T R = I: columns are unit length and perpendicular, so lengths are kept", np.allclose(R.T @ R, np.eye(2), atol=1e-12)))
    checks.append(("det(R) = 1, so area is kept", abs(np.linalg.det(R) - 1.0) < 1e-12))
    shear = np.array([[1.0, 1.0], [0.0, 1.0]])
    checks.append(("a shear has det 1 but stretches: (1, 1) becomes (2, 1)",
                   abs(np.linalg.det(shear) - 1.0) < 1e-12 and np.allclose(shear @ [1.0, 1.0], [2.0, 1.0])))
    a = L.hand_position(np.radians(45))
    checks.append(("at 45 degrees the hand's x equals its y", abs(a[0] - a[1]) < 1e-9))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
