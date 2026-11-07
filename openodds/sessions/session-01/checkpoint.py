"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("two dice have 36 equally likely outcomes", len(L.sample_space(2)) == 36))
    c = L.sum_counts()
    checks.append(("worked example: 6 of the 36 outcomes give a sum of 7, so P(7) = 1/6",
                   c[7] == 6 and abs(L.sum_probabilities()[7] - 1 / 6) < 1e-12))
    checks.append(("hand count: sums 2..12 have 1,2,3,4,5,6,5,4,3,2,1 outcomes",
                   [c[s] for s in range(2, 13)] == [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]))
    checks.append(("probabilities add up to exactly 1", abs(sum(L.sum_probabilities().values()) - 1.0) < 1e-12))
    checks.append(("one die: each face has probability 1/6", set(L.sum_counts(1).values()) == {1} and len(L.sum_counts(1)) == 6))
    s = L.roll_sums(100000, seed=3)
    f = L.relative_frequencies(s)
    exact = np.array([L.sum_probabilities()[k] for k in range(2, 13)])
    checks.append(("100000 simulated rolls match the exact table within 0.01", np.max(np.abs(f - exact)) < 0.01))
    checks.append(("same seed gives the same rolls", np.array_equal(L.roll_sums(50, 7), L.roll_sums(50, 7))))
    checks.append(("every simulated sum lies between 2 and 12", s.min() >= 2 and s.max() <= 12))
    checks.append(("edge case: three dice give 216 outcomes and sums 3..18", len(L.sample_space(3)) == 216 and min(L.sum_counts(3)) == 3 and max(L.sum_counts(3)) == 18))
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
