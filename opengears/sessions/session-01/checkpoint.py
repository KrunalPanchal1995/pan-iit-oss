"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    w, t = L.mesh(120, 5, 20, 60)
    checks.append(("worked example: 20 teeth driving 60 at 120 rpm and 5 N m gives -40 rpm and -15 N m",
                   abs(w + 40) < 1e-9 and abs(t + 15) < 1e-9))
    checks.append(("worked example: power in equals power out (62.83 W)",
                   abs(L.power_watts(5, 120) - 62.832) < 1e-3 and abs(L.power_watts(t, w) - L.power_watts(5, 120)) < 1e-9))
    w2, t2 = L.mesh(100, 4, 40, 20)
    checks.append(("hand calculation: 40 driving 20 (a speed-up) gives -200 rpm and -2 N m",
                   abs(w2 + 200) < 1e-9 and abs(t2 + 2) < 1e-9))
    checks.append(("a driven gear with twice the teeth runs at half the speed with twice the torque",
                   np.allclose(L.mesh(60, 3, 15, 30), (-30.0, -6.0))))
    w3, t3 = L.train(120, 5, [20, 30, 60])
    checks.append(("an idler (30 teeth) between 20 and 60 gives +40 rpm and +15 N m: same direction",
                   abs(w3 - 40) < 1e-9 and abs(t3 - 15) < 1e-9))
    w4, _ = L.train(120, 5, [20, 77, 60])
    checks.append(("the idler tooth count does not change the speed", abs(w4 - w3) < 1e-9))
    checks.append(("direction is (-1)^k for k meshes: 1 mesh -1, 2 meshes +1, 3 meshes -1",
                   [L.direction(k) for k in (1, 2, 3)] == [-1, 1, -1]))
    w5, t5 = L.train(120, 5, [20, 30, 25, 60])
    checks.append(("power is conserved through a four-gear train",
                   abs(abs(L.power_watts(t5, w5)) - L.power_watts(5, 120)) < 1e-9))
    w7, t7 = L.mesh(120, 5, 20, 40)
    checks.append(("graph reading: 20 teeth driving 40 at 120 rpm and 5 N m gives -60 rpm and -10 N m",
                   abs(w7 + 60) < 1e-9 and abs(t7 + 10) < 1e-9))
    checks.append(("[20, 30, 25, 60] has 3 meshes (two idlers): -40 rpm, -15 N m",
                   abs(w5 + 40) < 1e-9 and abs(t5 + 15) < 1e-9))
    checks.append(("a speed-up 40 to 20 at 100 rpm and 4 N m carries 41.9 W in and out",
                   abs(L.power_watts(4, 100) - 41.89) < 0.01 and abs(L.power_watts(2, 200) - L.power_watts(4, 100)) < 1e-9))
    w6, _ = L.mesh(120, 5, 40, 40)
    checks.append(("edge case: equal gears turn at the same speed, opposite way", abs(w6 + 120) < 1e-9))
    x, y = L.gear_outline(20, 1.0)
    r = np.hypot(x, y)
    checks.append(("gear outline: teeth reach pitch radius 10 + module 1 = 11 and roots 10 - 1.25 = 8.75",
                   abs(r.max() - 11.0) < 1e-9 and abs(r.min() - 8.75) < 1e-9))
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
