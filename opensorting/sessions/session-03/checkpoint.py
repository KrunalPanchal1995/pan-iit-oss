"""Checkpoint for Session 3. Prints PASS or FAIL.

Operation counts carry the main claims. Wall-clock checks use generous margins (factors of 3 or more).
"""
import math
import random
import struct


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # validation against sorted(): every method, every pattern, plus tiny and degenerate inputs
    ok = True
    for pat in L.PATTERNS:
        for name in L.METHODS:
            data = L.make_data(pat, 300, 4)
            snap = list(data)
            L.run_method(name, data)          # run_method asserts the output equals sorted(data)
            ok &= data == snap
    for name in L.METHODS:
        for data in ([], [5], [2, 1], [7] * 50):
            L.run_method(name, data)
    checks.append(("all 8 methods match sorted() on 5 patterns, on empty, single, pair and all-equal inputs", ok))

    # slopes on log-log axes (counts, so independent of the computer)
    s = {}
    for name in ("bubble", "selection", "insertion"):
        s[name] = L.loglog_slope(L.QUAD_SIZES, L.count_curve(name, L.QUAD_SIZES))
    for name in ("merge", "hybrid", "quick_random", "quick_median3"):
        s[name] = L.loglog_slope(L.FAST_SIZES, L.count_curve(name, L.FAST_SIZES))
    checks.append(("slopes of bubble, selection and insertion comparisons are between 1.9 and 2.1 (about 2)",
                   all(1.9 < s[k] < 2.1 for k in ("bubble", "selection", "insertion"))))
    checks.append(("slopes of merge, hybrid and quick (random or median-of-3 pivot) are between 1.05 and 1.25 (1 plus a little)",
                   all(1.05 < s[k] < 1.25 for k in ("merge", "hybrid", "quick_random", "quick_median3"))))
    pure = 1 + 1 / math.log(1600)
    checks.append(("hand check: n log n has local slope 1 + 1/ln n, about 1.14 near n = 1600, close to the fitted merge slope",
                   abs(pure - 1.1355) < 0.001 and abs(s["merge"] - pure) < 0.08))

    # quicksort worst case and its cures: worked example (Section E)
    first = L.quick_sort(L.make_data("sorted", 200), "first")
    med = L.quick_sort(L.make_data("sorted", 200), "median3")
    rnd = L.quick_sort(L.make_data("sorted", 200), "random")
    checks.append(("worked example: sorted input of 200, first pivot: 19,900 = 200*199/2 comparisons, 199 moves, depth 199",
                   first[1:] == (19900, 199, 199) and first[1] == 200 * 199 // 2))
    checks.append(("worked example: sorted input of 200, median-of-3 pivot: 1,534 comparisons, depth 7",
                   med[1] == 1534 and med[3] == 7 and med[2] == 734))
    checks.append(("worked example: sorted input of 200, random pivot (seed 0): 1,625 comparisons, depth 16",
                   rnd[1] == 1625 and rnd[3] == 16))
    checks.append(("on sorted input the first-pivot depth is n - 1 for every size tested",
                   all(L.quick_sort(L.make_data("sorted", n), "first")[3] == n - 1 for n in L.QUAD_SIZES)))
    s_first = L.loglog_slope(L.QUAD_SIZES, [L.quick_sort(L.make_data("sorted", n), "first")[1] for n in L.QUAD_SIZES])
    s_med = L.loglog_slope(L.QUAD_SIZES, [L.quick_sort(L.make_data("sorted", n), "median3")[1] for n in L.QUAD_SIZES])
    checks.append(("quicksort on sorted input: slope about 2 with a first pivot, below 1.3 with median-of-3",
                   1.9 < s_first < 2.1 and s_med < 1.3))
    allsame = L.quick_sort([7] * 200, "first")
    checks.append(("all-equal input is also a worst case for this quicksort: 19,900 comparisons for 200 items", allsame[1] == 19900))
    rev_med = L.cost("quick_median3", L.make_data("reversed", 1000))
    rev_rnd = L.cost("quick_random", L.make_data("reversed", 1000))
    checks.append(("median-of-3 is not a guarantee: on reversed input of 1000 it costs 190,506, over 5 times the random pivot",
                   rev_med == 190_506 and rev_med > 5 * rev_rnd))

    # input patterns at n = 1000
    tab = {pat: {m: L.cost(m, L.make_data(pat, 1000)) for m in L.METHODS} for pat in L.PATTERNS}
    checks.append(("random input n = 1000: merge costs 18,679 and bubble sort over 20 times more",
                   tab["random"]["merge"] == 18_679 and tab["random"]["bubble"] > 20 * tab["random"]["merge"]))
    checks.append(("sorted input n = 1000: bubble and insertion cost only 999; selection still costs 499,500",
                   tab["sorted"]["bubble"] == 999 and tab["sorted"]["insertion"] == 999 and tab["sorted"]["selection"] == 499_500))
    checks.append(("many duplicates (10 values): quick sort with a first pivot costs 57,190, over 3 times merge sort (18,516)",
                   tab["duplicates"]["quick_first"] == 57_190 and tab["duplicates"]["merge"] == 18_516
                   and tab["duplicates"]["quick_first"] > 3 * tab["duplicates"]["merge"]))
    checks.append(("nearly sorted (10 far swaps in 1000): insertion costs 16,159 and quick (first pivot) is about 9 times worse",
                   tab["nearly"]["insertion"] == 16_159 and tab["nearly"]["quick_first"] > 8 * tab["nearly"]["insertion"]))

    checks.append(("worked example: first-pivot comparisons are about 13 times the median-of-3 comparisons (19,900 / 1,534)",
                   round(19900 / 1534) == 13))
    checks.append(("duplicates: insertion sort costs over 100,000 at n = 1000", tab["duplicates"]["insertion"] > 100_000))

    # hybrid merge sort and cross-over sizes
    cut, table = L.best_cutoff()
    checks.append(("hybrid: the cheapest cutoff for n = 4096 is 4 (88,172) against 93,154 for pure merge sort",
                   cut == 4 and table[4] == 88_172 and table[1] == 93_154))
    checks.append(("hybrid: a cutoff of 64 is worse than pure merge sort (182,555 against 93,154)", table[64] == 182_555 > table[1]))
    checks.append(("cross-over size: for lists of 11 items or more merge sort needs fewer steps than insertion sort", L.small_n_crossover() == 11))

    # memory
    word = struct.calcsize("P")
    n = 20000
    data = L.make_data("random", n)
    m_merge = L.extra_bytes(L.merge_sort, data)
    m_ins = L.extra_bytes(L.insertion_sort, L.make_data("random", 2000))
    checks.append(("memory: merge sort allocates more than n extra slots; insertion sort allocates under 0.1 n",
                   m_merge > word * n and m_ins < 0.1 * word * 2000))
    sel = L.selection_sort(L.make_data("random", 1024))
    mer = L.merge_sort(L.make_data("random", 1024))
    ins = L.insertion_sort(L.make_data("random", 1024))
    checks.append(("moves: selection sort moves at most n - 1 = 1023 items; merge sort 10,240; insertion sort far more",
                   sel[2] <= 1023 and mer[2] == 10_240 and ins[2] > 200_000))

    # Python's built-in sorted (Timsort)
    srt = list(range(20000))
    rand = L.make_data("random", 20000)
    checks.append(("timsort: sorted and reversed input of 20,000 need exactly 19,999 comparisons",
                   L.timsort_comparisons(srt) == 19_999 and L.timsort_comparisons(srt[::-1]) == 19_999))
    c = L.timsort_comparisons(rand)
    checks.append(("timsort: random input of 20,000 needs between 0.5 and 1.0 times n log2 n comparisons",
                   0.5 * 20000 * math.log2(20000) < c < 20000 * math.log2(20000)))
    checks.append(("timsort: an empty list needs 0 comparisons", L.timsort_comparisons([]) == 0))
    big = list(range(200000))
    shuf = big[:]
    random.Random(1).shuffle(shuf)
    t_sorted, t_random = L.best_time(sorted, big), L.best_time(sorted, shuf)
    checks.append(("timing (illustrative): sorted() on shuffled data takes over 3 times longer than on presorted data", t_random > 3 * t_sorted))

    # timing: slopes in time are only illustrative
    tb = [L.best_time(L.bubble_sort, L.make_data("random", k)) for k in (400, 1600)]
    tm = [L.best_time(L.merge_sort, L.make_data("random", k)) for k in (400, 1600)]
    checks.append(("timing (illustrative): 4 times more items makes bubble sort over 6 times slower, merge sort under 10 times",
                   tb[1] / tb[0] > 6 and tm[1] / tm[0] < 10))
    checks.append(("timing (illustrative): bubble sort of 1600 items is slower than merge sort", tb[1] > tm[1]))

    # failure cases
    checks.append(("failure: recursive quicksort (first pivot) on sorted input of 1000 exceeds the recursion limit", L.recursion_fails(1000, "first")))
    checks.append(("failure: median-of-3 pivot survives the same input, and 100 sorted items are fine even with a first pivot",
                   not L.recursion_fails(1000, "median3") and not L.recursion_fails(100, "first")))
    good = L.name_then_grade(L.insertion_sort)
    bad = L.name_then_grade(L.selection_sort)
    checks.append(("failure: insertion sort is stable (grade 3 stays Asha, Chitra, Esha); selection sort gives Esha, Asha, Chitra",
                   [r[1] for r in good if r[0] == 3] == ["Asha", "Chitra", "Esha"] and [r[1] for r in bad if r[0] == 3] == ["Esha", "Asha", "Chitra"]))

    # numbers quoted in the roadmap (what the shipped code does)
    d10 = L.far_nearly_sorted(2000, 10)
    dup = L.make_data("duplicates", 1000)
    worst = max(L.run_method("quick_first", L.make_data(p, 1000))[0] for p in L.PATTERNS)
    checks.append(("roadmap baselines: best shipped comparisons 13,565 on 2000 items with 10 far swaps; first-pivot quick sort 54,365 on duplicates and 499,500 worst",
                   L.merge_sort(d10, 4)[1] == 13_565 and L.insertion_sort(d10)[1] == 17_189 and L.merge_sort(d10)[1] == 14_019
                   and L.run_method("quick_first", dup)[0] == 54_365 and worst == 499_500))
    checks.append(("hand check: doubling n from 100 to 200 multiplies n(n-1)/2 from 4950 to 19,900, a slope of log2(4.02) = 2.007",
                   abs(math.log2(19900 / 4950) - 2.007) < 0.001))

    # mini-project helper
    checks.append(("mini-project: with n = 2000, merge sort beats insertion sort from 11 far swaps; a hybrid with cutoff 4 from 10",
                   L.crossover_swaps() == 11 and L.crossover_swaps(cutoff=4) == 10))
    few = L.far_nearly_sorted(2000, 2)
    c_ins = L.cost("insertion", few)
    c_hyb = sum(L.merge_sort(few, 4)[1:])
    checks.append(("mini-project: with 2 far swaps insertion sort costs 5,923, more than 4 times cheaper than the hybrid (29,384)",
                   c_ins == 5923 and c_hyb == 29_384 and c_hyb > 4 * c_ins))
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
