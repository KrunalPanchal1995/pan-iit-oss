"""Session 3 (Level 3): measure how sorting cost grows, find the failure cases, and choose a method.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: empirical complexity and choosing a sorting method
# **A. Real-world problem.** You are told "merge sort is O(n log n)". How do you know that is true for
# *your* code and *your* data? You measure. In this session we count operations over a range of sizes,
# fit straight lines on log-log axes, find the inputs that break a method, and then pick and justify a
# method for a given data pattern. Operation counts carry the main claims because they do not depend on
# the computer; wall-clock times are shown only as an illustration.
#
# **Plan.** (1) the sorts with counters, (2) log-log slopes, (3) input patterns, (4) quicksort's worst
# case and its cures, (5) a hybrid merge/insertion sort, (6) memory, (7) Python's built-in `sorted`,
# (8) two failure cases, (9) the mini-project helper.

# %%
import math
import pathlib
import random
import sys
import time
import tracemalloc

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the sorts, with counters
# Each function returns `(sorted_list, comparisons, moves)`; `quick_sort` also returns the recursion depth.
# *Moves* are writes of an item (swaps, shifts, or items copied into a merged list).

# %%
def bubble_sort(values):
    a = list(values)
    comps = moves = 0
    for end in range(len(a) - 1, 0, -1):
        swapped = False
        for j in range(end):
            comps += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                moves += 1
                swapped = True
        if not swapped:
            break
    return a, comps, moves


def insertion_sort(values, key=None):
    k = key or (lambda x: x)
    a = list(values)
    comps = moves = 0
    for i in range(1, len(a)):
        item, j = a[i], i - 1
        while j >= 0:
            comps += 1
            if k(a[j]) > k(item):
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break
        a[j + 1] = item
    return a, comps, moves


def selection_sort(values, key=None):
    k = key or (lambda x: x)
    a = list(values)
    comps = moves = 0
    for i in range(len(a) - 1):
        m = i
        for j in range(i + 1, len(a)):
            comps += 1
            if k(a[j]) < k(a[m]):
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            moves += 1
    return a, comps, moves


def merge_sort(values, cutoff=1):
    """Top-down merge sort. Pieces of at most `cutoff` items are sorted by insertion sort (a hybrid)."""
    cnt = [0, 0]

    def sort(xs):
        if len(xs) <= max(cutoff, 1):
            if len(xs) > 1:
                out, c, m = insertion_sort(xs)
                cnt[0] += c
                cnt[1] += m
                return out
            return xs
        mid = len(xs) // 2
        left, right = sort(xs[:mid]), sort(xs[mid:])
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            cnt[0] += 1
            cnt[1] += 1
            if right[j] < left[i]:
                out.append(right[j])
                j += 1
            else:
                out.append(left[i])
                i += 1
        tail = left[i:] + right[j:]
        out.extend(tail)
        cnt[1] += len(tail)
        return out

    return sort(list(values)), cnt[0], cnt[1]


# %% [markdown]
# ## Step 2: quicksort with three pivot rules
# Quicksort picks a *pivot* item, moves smaller items before it, and sorts the two sides.
# `first` always takes the first item. `random` takes a random item. `median3` takes the median of the first,
# middle and last item (3 comparisons). The recursion depth is the number of nested pieces.

# %%
def _choose(a, lo, hi, pivot, rng, cnt):
    if pivot == "first":
        return lo
    if pivot == "random":
        return rng.randint(lo, hi)
    mid = (lo + hi) // 2
    c1, c2, c3 = a[lo] < a[mid], a[mid] < a[hi], a[lo] < a[hi]
    cnt[0] += 3
    if c1 == c2:
        return mid
    return hi if c1 == c3 else lo


def _partition(a, lo, hi, pivot, rng, cnt):
    """Lomuto partition of a[lo..hi]; returns the final index of the pivot."""
    p = _choose(a, lo, hi, pivot, rng, cnt)
    if p != lo:
        a[lo], a[p] = a[p], a[lo]
        cnt[1] += 1
    v, i = a[lo], lo
    for j in range(lo + 1, hi + 1):
        cnt[0] += 1
        if a[j] < v:
            i += 1
            a[i], a[j] = a[j], a[i]
            cnt[1] += 1
    a[lo], a[i] = a[i], a[lo]
    cnt[1] += 1
    return i


def quick_sort(values, pivot="first", seed=0):
    """Return (sorted list, comparisons, moves, depth). Uses an explicit stack, so it never overflows."""
    a = list(values)
    rng = random.Random(seed)
    cnt = [0, 0]
    stack, depth = [(0, len(a) - 1, 1)], 0
    while stack:
        lo, hi, d = stack.pop()
        if lo >= hi:
            continue
        depth = max(depth, d)
        i = _partition(a, lo, hi, pivot, rng, cnt)
        stack.append((lo, i - 1, d + 1))
        stack.append((i + 1, hi, d + 1))
    return a, cnt[0], cnt[1], depth


def quick_recursive(a, lo, hi, pivot="first"):
    """The textbook recursive form, used only to demonstrate the failure case."""
    if lo >= hi:
        return
    i = _partition(a, lo, hi, pivot, random.Random(0), [0, 0])
    quick_recursive(a, lo, i - 1, pivot)
    quick_recursive(a, i + 1, hi, pivot)


# %% [markdown]
# ## Step 3: input patterns
# The same algorithm behaves differently on different data. Five patterns:
# `random` (a shuffle of 0..n-1), `sorted`, `reversed`, `duplicates` (only 10 different values),
# and `nearly` (sorted, then a few random swaps).

# %%
def far_nearly_sorted(n, swaps, seed=1):
    """0..n-1 in order, then `swaps` random exchanges between any two places."""
    rng = random.Random(seed)
    a = list(range(n))
    for _ in range(swaps):
        i, j = rng.randrange(n), rng.randrange(n)
        a[i], a[j] = a[j], a[i]
    return a


def make_data(pattern, n, seed=0):
    rng = random.Random(seed)
    if pattern == "sorted":
        return list(range(n))
    if pattern == "reversed":
        return list(range(n - 1, -1, -1))
    if pattern == "duplicates":
        return [rng.randint(0, 9) for _ in range(n)]
    if pattern == "nearly":
        return far_nearly_sorted(n, max(1, n // 100), seed + 1)
    xs = list(range(n))
    rng.shuffle(xs)
    return xs


PATTERNS = ["random", "sorted", "reversed", "duplicates", "nearly"]


def run_method(name, data):
    """Return (comparisons, moves) for a method name on a list."""
    if name == "bubble":
        r = bubble_sort(data)
    elif name == "insertion":
        r = insertion_sort(data)
    elif name == "selection":
        r = selection_sort(data)
    elif name == "merge":
        r = merge_sort(data)
    elif name == "hybrid":
        r = merge_sort(data, 16)
    else:                                  # quick_first, quick_random, quick_median3
        r = quick_sort(data, name.split("_")[1])
    assert r[0] == sorted(data)
    return r[1], r[2]


METHODS = ["bubble", "selection", "insertion", "merge", "hybrid", "quick_first", "quick_random", "quick_median3"]


def cost(name, data):
    c, m = run_method(name, data)
    return c + m


# %% [markdown]
# ## Step 4: slopes on log-log axes
# If cost = a * n^p then log(cost) = log(a) + p log(n): a straight line of slope p.
# `np.polyfit` finds the slope. For n log n the slope is not exactly 1 but 1 + 1/ln(n), a little above 1.

# %%
def loglog_slope(ns, ys):
    return float(np.polyfit(np.log(ns), np.log(ys), 1)[0])


def count_curve(name, ns, pattern="random", seed=0):
    """Total comparisons for each n."""
    return [run_method(name, make_data(pattern, n, seed))[0] for n in ns]


QUAD_SIZES = [100, 200, 400, 800, 1600]
FAST_SIZES = [200, 400, 800, 1600, 3200, 6400, 12800]


# %% [markdown]
# ## Step 5: Python's built-in `sorted` (Timsort) and timing
# Timsort looks for runs that are already ascending or descending, so presorted input costs only n - 1
# comparisons. We count comparisons with a small wrapper class and time it (timing is only illustrative).

# %%
class Counted:
    count = 0

    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        Counted.count += 1
        return self.v < other.v


def timsort_comparisons(data):
    Counted.count = 0
    sorted(Counted(x) for x in data)
    return Counted.count


def best_time(fn, data, repeats=3):
    """Smallest wall-clock time (seconds) over a few repeats; the smallest is the least disturbed."""
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn(list(data))
        best = min(best, time.perf_counter() - t0)
    return best


# %% [markdown]
# ## Step 6: memory
# Merge sort builds new lists, so it needs extra space of order n. Insertion, selection and bubble sort work in
# place. `tracemalloc` reports the peak memory a call allocates; we subtract the cost of the copy every method makes.

# %%
def extra_bytes(fn, data):
    """Peak extra bytes allocated by fn(data) beyond the plain copy of the list."""
    def peak(f):
        tracemalloc.start()
        f()
        p = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        return p
    base = peak(lambda: list(data))
    return peak(lambda: fn(data)) - base


# %% [markdown]
# ## Step 7: two failure cases
# 1. Naive recursive quicksort with a first-item pivot on sorted input recurses n deep and hits Python's limit.
# 2. A sort that is not stable scrambles records with equal keys (sorting by grade after sorting by name).

# %%
def recursion_fails(n, pivot="first", margin=150):
    """True if recursive quicksort of the sorted list 0..n-1 exceeds a recursion limit `margin` frames above now."""
    frames, f = 0, sys._getframe()
    while f is not None:
        frames += 1
        f = f.f_back
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(frames + margin)
    try:
        quick_recursive(list(range(n)), 0, n - 1, pivot)
        return False
    except RecursionError:
        return True
    finally:
        sys.setrecursionlimit(old)


def name_then_grade(sorter):
    """Sort by name, then by grade with `sorter` (key-aware). Return the final list of (grade, name)."""
    people = [(3, "Asha"), (1, "Bala"), (3, "Chitra"), (1, "Devi"), (3, "Esha"), (2, "Farid"), (1, "Gita")]
    by_name = sorted(people, key=lambda r: r[1])
    return sorter(by_name, key=lambda r: r[0])[0]


# %% [markdown]
# ## Step 8: helpers for the mini-project
# Which method is cheapest for a given pattern? `crossover_swaps` finds how many far swaps in a sorted list
# make merge sort cheaper than insertion sort.

# %%
def crossover_swaps(n=2000, limit=200, seed=1, cutoff=1):
    """Smallest number k of random far swaps for which merge sort (with the given cutoff) costs less
    than insertion sort, counting comparisons + moves."""
    for k in range(limit + 1):
        data = far_nearly_sorted(n, k, seed)
        if sum(merge_sort(data, cutoff)[1:]) < cost("insertion", data):
            return k
    return None


def best_cutoff(n=4096, cutoffs=(1, 2, 4, 8, 16, 32, 64, 128, 256), seed=0):
    """(cutoff with the lowest total cost, dict cutoff -> cost) for hybrid merge sort on random data."""
    data = make_data("random", n, seed)
    table = {c: sum(merge_sort(data, c)[1:]) for c in cutoffs}
    return min(table, key=table.get), table


def small_n_crossover(seeds=10, nmax=64):
    """Smallest n (2..nmax) at which pure merge sort costs less than insertion sort on average random data."""
    for n in range(2, nmax + 1):
        mi = sum(sum(insertion_sort(make_data("random", n, s))[1:]) for s in range(seeds))
        mm = sum(sum(merge_sort(make_data("random", n, s))[1:]) for s in range(seeds))
        if mm < mi:
            return n
    return None


# %% [markdown]
# ## Step 9: see it
# Figure 1: comparisons against n on log-log axes with fitted slopes. Figure 2: quicksort on sorted input
# with three pivot rules. Figure 3: total cost of hybrid merge sort against the cutoff.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for name, sizes in (("bubble", QUAD_SIZES), ("selection", QUAD_SIZES), ("insertion", QUAD_SIZES),
                        ("merge", FAST_SIZES), ("quick_random", FAST_SIZES)):
        ys = count_curve(name, sizes)
        s = loglog_slope(sizes, ys)
        ax.loglog(sizes, ys, "o-", ms=4, label="%s (slope %.2f)" % (name, s))
        print("%-13s slope %.3f" % (name, s))
    ax.set_xlabel("n (items, log scale)")
    ax.set_ylabel("comparisons (log scale)")
    ax.set_title("Straight lines on log-log axes: the slope is the exponent")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "loglog_slopes.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4.5))
    for piv in ("first", "random", "median3"):
        ys = [quick_sort(make_data("sorted", n), piv)[1] for n in QUAD_SIZES]
        ax2.loglog(QUAD_SIZES, ys, "o-", ms=4, label="pivot %s (slope %.2f)" % (piv, loglog_slope(QUAD_SIZES, ys)))
        print("quicksort on sorted input, pivot", piv, ys)
    ax2.set_xlabel("n (items, log scale)")
    ax2.set_ylabel("comparisons (log scale)")
    ax2.set_title("Quicksort on sorted input: the pivot rule decides")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "quicksort_pivots.png", dpi=120)

    c_best, table = best_cutoff()
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.semilogx(list(table), list(table.values()), "o-")
    ax3.set_xlabel("cutoff: pieces up to this size use insertion sort")
    ax3.set_ylabel("comparisons + moves (n = 4096)")
    ax3.set_title("Hybrid merge sort: best cutoff %d" % c_best)
    ax3.grid(alpha=0.3, which="both")
    fig3.tight_layout()
    fig3.savefig(OUT / "hybrid_cutoff.png", dpi=120)
    print("hybrid table", table)
    print("small-n crossover", small_n_crossover(), "| far-swap crossover", crossover_swaps())
    print("n = 1000 total cost by pattern")
    for pat in PATTERNS:
        print(" ", pat, {m: cost(m, make_data(pat, 1000)) for m in METHODS})
    data = list(range(20000))
    print("timsort comparisons, sorted 20000:", timsort_comparisons(data))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
