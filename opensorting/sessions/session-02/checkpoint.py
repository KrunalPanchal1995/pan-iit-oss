"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # correctness of every algorithm on several inputs, including empty, one item and duplicates
    cases = [[], [1], [2, 1], [3, 3, 3], [5, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]]
    cases += [L.make_input(k, 50, 3) for k in ("sorted", "reversed", "random")]
    good = True
    for name, fn in L.ALGORITHMS.items():
        for data in cases:
            snapshot = list(data)
            out = fn(data)[0]
            good &= L.is_correct(out, data) and out == sorted(data) and data == snapshot
    checks.append(("all five sorts return a sorted list with the same items and leave the input unchanged", good))

    # worked example (Section E): n = 1,000,000
    n = 1_000_000
    checks.append(("worked example: n = 1,000,000 needs 499,999,500,000 comparisons for n(n-1)/2",
                   L.quad(n) == 499_999_500_000))
    checks.append(("worked example: n log2 n is about 19,931,569 for n = 1,000,000",
                   abs(L.nlogn(n) - 19_931_569) < 1))
    checks.append(("worked example: the ratio is about 25,086 times",
                   abs(L.cost_ratio(n) - 25_086) < 1))
    checks.append(("worked example: at 1e9 steps per second that is 500 s against 0.02 s",
                   abs(L.seconds(L.quad(n)) - 500.0) < 0.01 and abs(L.seconds(L.nlogn(n)) - 0.0199) < 0.0005))

    # hand calculation: insertion sort on a reversed list of 100
    _, c, m = L.insertion_sort(L.make_input("reversed", 100))
    checks.append(("insertion sort on a reversed list of 100: 4950 = 100*99/2 comparisons and shifts", c == 4950 == m == 100 * 99 // 2))
    checks.append(("insertion sort on [2, 1, 3] takes 2 comparisons and 1 shift", L.insertion_sort([2, 1, 3])[1:] == (2, 1)))
    ok = all(L.insertion_sort(L.make_input("reversed", k))[1] == k * (k - 1) // 2 for k in range(2, 40))
    checks.append(("the formula n(n-1)/2 holds exactly for n = 2 to 39", ok))

    checks.append(("snippet: n = 1000 gives n(n-1)/2 = 499,500 and n log2 n = 9,966 (rounded)",
                   L.quad(1000) == 499_500 and round(L.nlogn(1000)) == 9966))

    # best case, worst case at n = 1000
    n = 1000
    rev = {a: L.ALGORITHMS[a](L.make_input("reversed", n))[1:] for a in L.ALGORITHMS}
    srt = {a: L.ALGORITHMS[a](L.make_input("sorted", n))[1:] for a in L.ALGORITHMS}
    checks.append(("n = 1000 reversed: bubble, selection, insertion and quick all use 499,500 comparisons",
                   all(rev[a][0] == 499_500 for a in ("bubble", "selection", "insertion", "quick"))))
    checks.append(("n = 1000 sorted: bubble and insertion need only 999 comparisons and no moves",
                   srt["bubble"] == (999, 0) and srt["insertion"] == (999, 0)))
    checks.append(("selection sort does n(n-1)/2 comparisons even on sorted input", srt["selection"][0] == 499_500))
    checks.append(("selection sort moves at most n - 1 = 999 items", all(rev[a][1] <= 999 for a in ("selection",))))
    checks.append(("quick sort with the first item as pivot is quadratic on sorted input (499,500 comparisons)", srt["quick"][0] == 499_500))

    # merge sort bounds and exact values at n = 1024
    n = 1024
    lo, hi = n // 2 * math.log2(n), n * math.log2(n) - n + 1
    ms = L.merge_sort(L.make_input("sorted", n))
    mr = L.merge_sort(L.make_input("reversed", n))
    mx = L.merge_sort(L.make_input("random", n, 0))
    checks.append(("merge sort n = 1024: best 5120 = (n/2) log2 n, worst-case bound 9217 = n log2 n - n + 1",
                   ms[1] == 5120 == lo and hi == 9217))
    checks.append(("merge sort comparisons on sorted, reversed and random lists all lie between 5120 and 9217",
                   all(lo <= r[1] <= hi for r in (ms, mr, mx))))
    checks.append(("merge sort makes exactly n log2 n = 10240 item moves for n = 1024", ms[2] == mr[2] == mx[2] == 10_240))
    qa = L.measure("quick", "random", 1024)[0]
    checks.append(("quick sort random average at n = 1024 is below the 2 n ln n bound (14,196)", abs(2 * n * math.log(n) - 14196) < 1 and n * math.log2(n) * 0.9 < qa < 2 * n * math.log(n)))

    # n squared versus n log n grows apart
    r = [L.measure("bubble", "random", k)[0] / L.measure("merge", "random", k)[0] for k in (64, 128, 256)]
    checks.append(("bubble divided by merge comparisons grows with n", r[0] < r[1] < r[2]))

    # design problem: nearly sorted data
    data = L.nearly_sorted(1000, 10)
    inv = L.inversions(data)
    ins = L.insertion_sort(data)
    mg = L.merge_sort(data)
    checks.append(("design: nearly sorted list of 1000 has only 28 inversions", inv == 28))
    checks.append(("design: insertion sort needs 1027 = (n - 1) + inversions comparisons", ins[1] == 999 + inv == 1027))
    checks.append(("design: merge sort needs 4947 comparisons, more than 4 times insertion sort", mg[1] == 4947 and mg[1] > 4 * ins[1]))
    checks.append(("design: quick sort (first pivot) is the wrong choice here: over 400,000 comparisons",
                   L.quick_sort(data)[1] > 400_000))
    checks.append(("inversions: sorted 0, reversed n(n-1)/2, [2,1,3] has 1",
                   L.inversions(list(range(10))) == 0 and L.inversions(list(range(10, 0, -1))) == 45 and L.inversions([2, 1, 3]) == 1))

    # stability
    stable = {a: L.is_stable(a) for a in L.ALGORITHMS}
    checks.append(("stability: bubble, insertion and merge are stable", stable["bubble"] and stable["insertion"] and stable["merge"]))
    checks.append(("stability: selection and quick sort are not stable", not stable["selection"] and not stable["quick"]))
    recs = [(2, "a"), (2, "b"), (1, "c")]
    checks.append(("selection sort turns [(2,a),(2,b),(1,c)] into (1,c),(2,b),(2,a): equal keys swapped",
                   L.selection_sort(recs, key=lambda r: r[0])[0] == [(1, "c"), (2, "b"), (2, "a")]))
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
