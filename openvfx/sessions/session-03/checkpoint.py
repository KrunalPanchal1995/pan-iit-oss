"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    top0, bottom0 = L.rest_mesh()
    t, b = L.lbs_pose(0.0)
    checks.append(("zero bend leaves the skin unchanged", np.allclose(t, top0) and np.allclose(b, bottom0)))
    w = L.smooth_weights(top0[:, 0])
    checks.append(("weights lie in [0, 1]", bool(w.min() >= 0 and w.max() <= 1)))
    checks.append(("weights rise from 0 to 1", w[0] == 0 and w[-1] == 1 and bool(np.all(np.diff(w) >= -1e-12))))

    bend = np.radians(90)
    gap = {}
    for name, fn in (("rigid", L.rigid_weights), ("smooth", L.smooth_weights)):
        t, b = L.pose(fn, bend)
        gap[name] = max(L.max_gap(t), L.max_gap(b))
    checks.append(("rigid skin cracks: largest gap above 0.2 at 90 degrees", gap["rigid"] > 0.2))
    checks.append(("blended skin: largest gap below 0.1 at 90 degrees", gap["smooth"] < 0.1))

    # hand calculation: elbow width ratio = cos(bend / 2)
    r90 = L.elbow_width_ratio(*L.lbs_pose(bend))
    checks.append((f"worked example: width ratio at 90 degrees is cos(45 deg) = 0.707 (got {r90:.3f})",
                   abs(r90 - np.cos(np.pi / 4)) < 1e-3))
    r120 = L.elbow_width_ratio(*L.lbs_pose(np.radians(120)))
    checks.append(("width ratio at 120 degrees is 0.5", abs(r120 - 0.5) < 1e-3))
    rrigid = L.elbow_width_ratio(*L.pose(L.rigid_weights, bend))
    checks.append(("rigid skin keeps full width (the trade-off)", abs(rrigid - 1.0) < 1e-9))

    # the blend zone can be changed through lbs_pose
    narrow = max(L.max_gap(x) for x in L.lbs_pose(bend, 0.1))
    wide = max(L.max_gap(x) for x in L.lbs_pose(bend, 0.4))
    checks.append(("a wider blend zone gives a smaller gap", wide < narrow))
    t, b = L.lbs_pose(bend, 0.2)
    checks.append(("blend zone 0.2 keeps the gap below 0.08 at 90 degrees", max(L.max_gap(t), L.max_gap(b)) < 0.08))
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
