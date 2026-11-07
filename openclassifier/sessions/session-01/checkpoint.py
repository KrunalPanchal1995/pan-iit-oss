"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    X, y = L.toy_arrays()
    checks.append(("toy data: 12 fruit, 6 ripe", len(y) == 12 and int(y.sum()) == 6))

    # hand calculation: x*cos45 + y*sin45 > 7 means x + y > 9.899; only (6, 4.5) with sum 10.5 is wrongly ripe
    fa, ms = L.count_mistakes(y, L.line_rule(X, 45, 7.0))
    checks.append((f"worked example: line (45 degrees, c = 7) gives 1 false alarm and 0 misses (got {fa}, {ms})", (fa, ms) == (1, 0)))
    checks.append(("worked example: accuracy 11/12 = 0.917", abs(L.accuracy(y, L.line_rule(X, 45, 7.0)) - 11 / 12) < 1e-9))
    checks.append(("a perfect line exists for the toy fruit (45 degrees, c = 7.6)", L.count_mistakes(y, L.line_rule(X, 45, 7.6)) == (0, 0)))
    checks.append(("size-only rule at 5.25 makes 1 false alarm and 1 miss", L.count_mistakes(y, L.size_rule(X, 5.25)) == (1, 1)))

    checks.append(("size-only rule at 5 (size > 5): 1 false alarm, 1 miss, accuracy 10/12", L.count_mistakes(y, L.size_rule(X, 5.0)) == (1, 1) and abs(L.accuracy(y, L.size_rule(X, 5.0)) - 10 / 12) < 1e-9))
    # edge cases: a fruit exactly on the boundary is called unripe (strict inequality)
    checks.append(("a point exactly on the boundary is called 0", int(L.size_rule(np.array([[5.0, 1.0]]), 5.0)[0]) == 0))
    checks.append(("a boundary far right calls nothing ripe", int(L.line_rule(X, 0, 100).sum()) == 0))
    checks.append(("a boundary far left calls everything ripe", int(L.line_rule(X, 0, -100).sum()) == 12))

    Xb, yb = L.make_fruit()
    checks.append(("make_fruit is reproducible with its seed", np.allclose(Xb, L.make_fruit()[0])))
    fa1, ms1 = L.count_mistakes(yb, L.size_rule(Xb, 4.75))
    fa2, ms2 = L.count_mistakes(yb, L.line_rule(Xb, 45, 6.7))
    checks.append((f"size only: 14 false alarms and 8 misses of 200 (got {fa1}, {ms1})", (fa1, ms1) == (14, 8)))
    checks.append((f"size + colour line: 3 false alarms and 4 misses (got {fa2}, {ms2})", (fa2, ms2) == (3, 4)))
    checks.append(("using colour as well lowers the total mistakes", fa2 + ms2 < fa1 + ms1))
    checks.append(("accuracy of the line rule is 0.965", abs(L.accuracy(yb, L.line_rule(Xb, 45, 6.7)) - 0.965) < 1e-9))

    cs = np.linspace(2, 11, 91)
    fa_c, ms_c = L.sweep_offset(Xb, yb, 45, cs)
    checks.append(("sliding the line right: false alarms never rise, misses never fall", bool(np.all(np.diff(fa_c) <= 0) and np.all(np.diff(ms_c) >= 0))))
    checks.append((f"at c = 2: 96 false alarms and 0 misses (got {fa_c[0]}, {ms_c[0]})", (int(fa_c[0]), int(ms_c[0])) == (96, 0)))
    checks.append(("the two kinds of mistake are equal near c = 6.6", abs(cs[int(np.argmin(np.abs(fa_c - ms_c)))] - 6.6) < 0.2))
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
