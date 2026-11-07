"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d = np.radians
    checks.append(("straight arm: gripper at (0.70, 0) m and longest reach 0.70 m",
                   np.allclose(L.gripper([0, 0, 0]), [0.70, 0.0], atol=1e-12) and abs(L.max_reach() - 0.70) < 1e-12))
    checks.append(("cumulative angles of (30, 40, -20) degrees are 30, 70, 50",
                   np.allclose(np.degrees(L.cumulative_angles(d([30, 40, -20]))), [30, 70, 50])))
    g = L.gripper(d([30, 40, -20]))
    checks.append(("worked example: gripper at (0.442, 0.500) m", np.allclose(g, [0.4417, 0.4998], atol=1e-3)))
    checks.append(("worked example: tool angle 50 degrees", abs(np.degrees(L.tool_angle(d([30, 40, -20]))) - 50) < 1e-9))
    checks.append(("pose (70, -60, -30) degrees puts the gripper at (0.490, 0.274) m",
                   np.allclose(L.gripper(d([70, -60, -30])), [0.490, 0.274], atol=1e-3)))
    hand = (0.30 * np.cos(d(30)) + 0.25 * np.cos(d(70)) + 0.15 * np.cos(d(50)),
            0.30 * np.sin(d(30)) + 0.25 * np.sin(d(70)) + 0.15 * np.sin(d(50)))
    checks.append(("hand calculation agrees with link_points", np.allclose(L.link_points(d([30, 40, -20]))[-1], hand)))
    ok = True
    for a in np.linspace(-3, 3, 7):
        for b in np.linspace(-3, 3, 7):
            for c in np.linspace(-3, 3, 7):
                p = L.link_points([a, b, c])
                ok &= np.allclose(np.linalg.norm(np.diff(p, axis=0), axis=1), L.LINKS, atol=1e-9)
                ok &= np.linalg.norm(p[-1]) <= L.max_reach() + 1e-9
    checks.append(("link lengths never change and the gripper never goes beyond 0.70 m", bool(ok)))
    checks.append(("pose (90, -90, 0) degrees touches the block (0.40, 0.30) exactly",
                   L.touches(d([90, -90, 0]), L.BLOCK, 1e-9) and np.allclose(L.gripper(d([90, -90, 0])), [0.40, 0.30])))
    checks.append(("the block is 0.50 m from the base, inside the 0.70 m reach",
                   abs(np.linalg.norm(L.BLOCK) - 0.5) < 1e-12 and np.linalg.norm(L.BLOCK) < L.max_reach()))
    far = np.array([0.75, 0.0])
    checks.append(("a block 0.75 m away cannot be touched (brute force finds nothing)", L.find_pose(far, step_deg=30) is None))
    pose = L.find_pose(L.BLOCK, step_deg=10)
    checks.append(("brute force at 10 degree steps finds (-10, 70, 40) degrees, 1.3 cm from the block",
                   pose is not None and np.allclose(np.degrees(pose), [-10, 70, 40])
                   and abs(np.linalg.norm(L.gripper(pose) - L.BLOCK) - 0.0134) < 1e-3))
    a = d(np.linspace(-180, 180, 3601))
    x = np.array([L.gripper([t, d(40), d(-20)])[0] for t in a])
    r = np.linalg.norm(L.gripper([0, d(40), d(-20)]))
    checks.append(("shoulder sweep with q2 = 40, q3 = -20: radius 0.667 m, largest x at q1 = -18.5 degrees",
                   abs(r - 0.6670) < 1e-3 and abs(x.max() - r) < 1e-6 and abs(np.degrees(a[x.argmax()]) + 18.5) < 0.05))
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
