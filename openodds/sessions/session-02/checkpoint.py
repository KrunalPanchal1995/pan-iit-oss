"""Checkpoint for Session 2. Prints PASS or FAIL."""
import itertools


def _raises(f):
    try:
        f()
    except ValueError:
        return True
    return False


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c = L.poker_counts()
    checks.append(("worked example: C(52,5) = 2598960 hands, 1098240 one-pair hands, 5148 flushes",
                   c["total"] == 2598960 and c["one pair"] == 1098240 and c["flush"] == 5148))
    checks.append(("P(one pair) = 0.4226 and P(flush) = 0.00198", abs(c["one pair"] / c["total"] - 0.42257) < 1e-4 and abs(c["flush"] / c["total"] - 0.001981) < 1e-5))
    checks.append(("hand calculation: C(5,2) = 10 and 5! = 120", L.combinations(5, 2) == 10 and L.permutations(5, 5) == 120))
    checks.append(("brute force: C(6,3) = 20 subsets", L.combinations(6, 3) == len(list(itertools.combinations(range(6), 3)))))
    checks.append(("brute force: 6P2 = 30 ordered pairs", L.permutations(6, 2) == len(list(itertools.permutations(range(6), 2)))))
    checks.append(("birthday: 23 people give 0.507", abs(L.birthday_shared(23) - 0.5073) < 1e-3))
    checks.append(("birthday edge cases: 1 person 0, 366 people 1", L.birthday_shared(1) == 0.0 and L.birthday_shared(366) == 1.0))
    checks.append(("independent events multiply: two sixes = 1/36", abs(L.probability(1, 6) * L.probability(1, 6) - 1 / 36) < 1e-12))
    checks.append(("one fair die has expected value 3.5", abs(L.expected_value(range(1, 7), [1 / 6] * 6) - 3.5) < 1e-12))
    checks.append(("worked example: break-even prize for 500 tickets at Rs 20 is Rs 10000",
                   L.break_even_prize(500, 20) == 10000 and abs(L.raffle_net_gain(500, 20, 10000)) < 1e-9))
    checks.append(("a smaller prize loses money for the player", L.raffle_net_gain(500, 20, 5000) < 0))
    checks.append(("edge case: C(5,7) = 0 and zero total is rejected", L.combinations(5, 7) == 0 and _raises(lambda: L.probability(1, 0))))
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
