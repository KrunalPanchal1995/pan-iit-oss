"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    fr = L.blob_frames(0.6)
    K = L.kymograph(fr, fr.shape[1] // 2)
    checks.append(("kymograph has one row per frame and one column per pixel", K.shape == (40, 64)))
    x = L.stripe_position(K)
    checks.append(("worked example: blob at column 14 in frame 10 and 26 in frame 30",
                   int(x[10]) == 14 and int(x[30]) == 26))
    checks.append(("worked example: slope (26 - 14) / (30 - 10) = 0.6 px/frame",
                   abs(L.slope_two_points(K, 10, 30) - 0.6) < 1e-9))
    checks.append(("a line fit through the stripe also gives 0.6 px/frame within 0.02",
                   abs(L.slope_fit(K) - 0.6) < 0.02))
    K0 = L.kymograph(L.blob_frames(0.0), 7)
    checks.append(("a blob that does not move gives a vertical stripe (slope 0)", L.slope_two_points(K0, 0, 39) == 0.0))
    Kn = L.kymograph(L.blob_frames(-0.5, x0=40.0), 7)
    checks.append(("a blob moving left has a negative slope", L.slope_two_points(Kn, 10, 30) < 0))
    f1 = L.blob_frames(1.0)
    checks.append(("kymograph row t is exactly the chosen line of frame t",
                   all(np.array_equal(L.kymograph(f1, 7)[t], f1[t, 7, :]) for t in (0, 13, 39))))
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
