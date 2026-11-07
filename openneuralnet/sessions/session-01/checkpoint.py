"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    z, out = L.neuron([2.0, 2.5], [1.0, 1.0], 0.0)
    checks.append(("hand calculation: w = (1, 1), b = 0 on (2, 2.5) gives z = 4.5 and fires",
                   abs(z - 4.5) < 1e-12 and int(out) == 1))
    z0, out0 = L.neuron([2.0, 2.5], [1.0, -2.0], 0.0)
    checks.append(("worked example: start w = (1, -2), b = 0 gives z = -3 on (2, 2.5), so it stays silent (wrong)",
                   abs(z0 + 3.0) < 1e-12 and int(out0) == 0))
    w, b, hist = L.perceptron_train(L.X, L.Y)
    checks.append(("worked example: first nudge gives w = (3, 0.5), b = 1",
                   np.allclose(hist[1][0], [3.0, 0.5]) and abs(hist[1][1] - 1.0) < 1e-12))
    checks.append(("worked example: second nudge gives w = (2.5, 1), b = 0",
                   np.allclose(hist[2][0], [2.5, 1.0]) and abs(hist[2][1]) < 1e-12))
    checks.append(("learning ends with w = (2, 1.5), b = -1 after exactly 3 nudges",
                   len(hist) - 1 == 3 and np.allclose(w, [2.0, 1.5]) and abs(b + 1.0) < 1e-12))
    checks.append(("the start classifies 2 of 10 points right, the end 10 of 10",
                   L.n_correct(L.X, L.Y, hist[0][0], hist[0][1]) == 2 and L.n_correct(L.X, L.Y, w, b) == 10))
    checks.append(("w = (1, -1), b = 0 gets 5 of 10 right (the app default)", L.n_correct(L.X, L.Y, [1.0, -1.0], 0.0) == 5))
    checks.append(("w = (1, 1), b = 0 gets all 10 right (the app challenge)", L.n_correct(L.X, L.Y, [1.0, 1.0], 0.0) == 10))
    sc = [L.n_correct(L.X, L.Y, wk, bk) for wk, bk in hist]
    checks.append(("points right after each nudge: 2, 9, 9, 10", sc == [2, 9, 9, 10]))
    # the line: z = 0 on it
    x1 = 1.0
    x2 = L.line_x2(x1, w, b)
    checks.append(("a point on the drawn line has z = 0", abs(L.neuron([x1, x2], w, b)[0]) < 1e-12))
    checks.append(("hand calculation: the learned neuron on (-0.5, -1.5) gives z = -4.25 and stays silent (label 0, right)",
                   abs(float(L.neuron([-0.5, -1.5], w, b)[0]) + 4.25) < 1e-12 and int(L.neuron([-0.5, -1.5], w, b)[1]) == 0))
    checks.append(("design: with w = (1, 1) any bias in (-4.5, 0] gets all 10 right; -2 works, -4.5 and 0.5 do not",
                   L.n_correct(L.X, L.Y, [1.0, 1.0], -2.0) == 10 and L.n_correct(L.X, L.Y, [1.0, 1.0], 0.0) == 10
                   and L.n_correct(L.X, L.Y, [1.0, 1.0], -4.5) < 10 and L.n_correct(L.X, L.Y, [1.0, 1.0], 0.5) < 10))
    checks.append(("worked example: point 8 = (0.5, -0.5) has z = 2.25 with the first nudge's line and z = 0.75 with the second's (both wrongly fire)",
                   abs(float(L.neuron(L.X[7], [3.0, 0.5], 1.0)[0]) - 2.25) < 1e-12 and abs(float(L.neuron(L.X[7], [2.5, 1.0], 0.0)[0]) - 0.75) < 1e-12))
    # edge: a point exactly on the line does not fire (z > 0 is strict)
    checks.append(("edge: a point exactly on the line (z = 0) does not fire", int(L.neuron([0.0, 0.0], [1.0, 1.0], 0.0)[1]) == 0))
    # edge: already-correct weights need zero nudges
    w2, b2, h2 = L.perceptron_train(L.X, L.Y, w0=(1.0, 1.0), b0=0.0)
    checks.append(("edge: starting from a perfect line needs 0 nudges", len(h2) == 1))
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
