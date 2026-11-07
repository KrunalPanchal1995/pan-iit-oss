"""Session 2 (Level 2): five sorting algorithms with a step counter, and why n log n beats n squared.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: count the steps of five sorting algorithms
# **A. Real-world problem.** A shop has 1,000,000 orders to put in date order. Two programs give
# the same sorted answer; one finishes in a blink and the other keeps the machine busy for minutes.
# The difference is the *number of steps*, so we count steps instead of guessing.
#
# **Plan.** (1) write bubble, selection, insertion, merge and quick sort with counters,
# (2) test that each one is correct, (3) measure best, average and worst inputs,
# (4) compare the counts with the formulas n(n-1)/2 and n log2 n, (5) check stability.

# %%
import math
import pathlib
import random

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the five algorithms
# Every function returns `(sorted_list, comparisons, moves)` and never changes its input.
# A *comparison* looks at two items. A *move* is one write of an item: a swap in bubble, selection
# and quick sort, a one-place shift in insertion sort, an item copied into the merged list in merge sort.
# `key` says what to sort by (default: the item itself); it is used for the stability test.

# %%
def _key(key):
    return key if key is not None else (lambda x: x)


def bubble_sort(values, key=None):
    k = _key(key)
    a = list(values)
    comps = moves = 0
    for end in range(len(a) - 1, 0, -1):
        swapped = False
        for j in range(end):
            comps += 1
            if k(a[j]) > k(a[j + 1]):
                a[j], a[j + 1] = a[j + 1], a[j]
                moves += 1
                swapped = True
        if not swapped:
            break
    return a, comps, moves


def selection_sort(values, key=None):
    k = _key(key)
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


def insertion_sort(values, key=None):
    k = _key(key)
    a = list(values)
    comps = moves = 0
    for i in range(1, len(a)):
        card = a[i]
        j = i - 1
        while j >= 0:
            comps += 1
            if k(a[j]) > k(card):
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break
        a[j + 1] = card
    return a, comps, moves


def merge_sort(values, key=None):
    k = _key(key)
    counts = [0, 0]

    def sort(xs):
        if len(xs) <= 1:
            return xs
        mid = len(xs) // 2
        left, right = sort(xs[:mid]), sort(xs[mid:])
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            counts[0] += 1
            if k(right[j]) < k(left[i]):      # strict: on a tie the left item goes first (stable)
                out.append(right[j])
                j += 1
            else:
                out.append(left[i])
                i += 1
            counts[1] += 1
        for rest in (left[i:], right[j:]):
            for x in rest:
                out.append(x)
                counts[1] += 1
        return out

    return sort(list(values)), counts[0], counts[1]


def quick_sort(values, key=None):
    """First item as pivot, Lomuto partition, explicit stack (no deep recursion)."""
    k = _key(key)
    a = list(values)
    comps = moves = 0
    stack = [(0, len(a) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        pivot = k(a[lo])
        i = lo
        for j in range(lo + 1, hi + 1):
            comps += 1
            if k(a[j]) < pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
                moves += 1
        a[lo], a[i] = a[i], a[lo]
        moves += 1
        stack.append((lo, i - 1))
        stack.append((i + 1, hi))
    return a, comps, moves


ALGORITHMS = {"bubble": bubble_sort, "selection": selection_sort, "insertion": insertion_sort,
              "merge": merge_sort, "quick": quick_sort}


# %% [markdown]
# ## Step 2: correctness comes first
# A fast wrong sort is useless. A result is correct when (1) it is in order and (2) it contains
# exactly the same items as the input (same multiset). We compare against Python's `sorted`.

# %%
def is_sorted(values):
    return all(values[i] <= values[i + 1] for i in range(len(values) - 1))


def is_correct(result, original):
    return is_sorted(result) and sorted(result) == sorted(original)


def make_input(kind, n, seed=0):
    """kind: 'sorted', 'reversed' or 'random' (a shuffle of 0..n-1)."""
    if kind == "sorted":
        return list(range(n))
    if kind == "reversed":
        return list(range(n - 1, -1, -1))
    rng = random.Random(seed)
    xs = list(range(n))
    rng.shuffle(xs)
    return xs


# %% [markdown]
# ## Step 3: best, average and worst inputs
# The step count depends on the input. 'Average' here is the mean over 20 random shuffles.

# %%
def measure(algo, kind, n, trials=20):
    """(comparisons, moves) for one input kind; random is averaged over `trials` shuffles."""
    fn = ALGORITHMS[algo]
    if kind != "random":
        _, c, m = fn(make_input(kind, n))
        return float(c), float(m)
    cs, ms = [], []
    for seed in range(trials):
        _, c, m = fn(make_input("random", n, seed))
        cs.append(c)
        ms.append(m)
    return sum(cs) / trials, sum(ms) / trials


# %% [markdown]
# ## Step 4: the formulas
# * bubble, selection, insertion (worst case): about n(n-1)/2 = n^2/2 comparisons.
# * merge sort: between (n/2) log2 n and n log2 n - n + 1 comparisons.
# * Insertion sort on a reversed list does exactly n(n-1)/2 comparisons and n(n-1)/2 shifts.

# %%
def quad(n):
    return n * (n - 1) / 2


def nlogn(n):
    return n * math.log2(n)


def cost_ratio(n):
    """How many times more comparisons n(n-1)/2 needs than n log2 n."""
    return quad(n) / nlogn(n)


def seconds(steps, steps_per_second=1e9):
    return steps / steps_per_second


# %% [markdown]
# ## Step 5: nearly sorted data and stability
# A *stable* sort keeps equal items in their original order. We test it with (key, position) records.

# %%
def nearly_sorted(n, swaps, seed=1):
    """0..n-1 in order, then `swaps` random exchanges of items at most 3 places apart."""
    rng = random.Random(seed)
    a = list(range(n))
    for _ in range(swaps):
        i = rng.randrange(n - 3)
        j = i + rng.randint(1, 3)
        a[i], a[j] = a[j], a[i]
    return a


def inversions(values):
    """Number of pairs in the wrong order (merge-sort style count, n log n steps)."""
    def rec(xs):
        if len(xs) <= 1:
            return xs, 0
        mid = len(xs) // 2
        left, a = rec(xs[:mid])
        right, b = rec(xs[mid:])
        out, i, j, c = [], 0, 0, a + b
        while i < len(left) and j < len(right):
            if right[j] < left[i]:
                out.append(right[j])
                j += 1
                c += len(left) - i
            else:
                out.append(left[i])
                i += 1
        return out + left[i:] + right[j:], c
    return rec(list(values))[1]


def is_stable(algo, trials=200, n=12, seed=5):
    """True if the algorithm keeps equal-key records in input order on every random test."""
    rng = random.Random(seed)
    fn = ALGORITHMS[algo]
    for _ in range(trials):
        recs = [(rng.randrange(4), i) for i in range(n)]      # (key, original position)
        out = fn(recs, key=lambda r: r[0])[0]
        if out != sorted(recs, key=lambda r: r[0]):           # Python's sorted is stable
            return False
    return True


# %% [markdown]
# ## Step 6: see it
# Left: comparisons of the five methods on sorted, random and reversed lists of 128 items (log scale).
# Right: insertion sort on reversed lists matches n(n-1)/2 exactly.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    n = 128
    kinds = ["sorted", "random", "reversed"]
    print("n = %d, comparisons / moves" % n)
    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.25
    for i, kind in enumerate(kinds):
        vals = []
        for name in ALGORITHMS:
            c, m = measure(name, kind, n)
            vals.append(max(c, 1))
            print("  %-9s %-9s comps %8.1f moves %8.1f" % (name, kind, c, m))
        ax.bar([x + (i - 1) * width for x in range(5)], vals, width, label=kind)
    ax.set_xticks(range(5))
    ax.set_xticklabels(list(ALGORITHMS))
    ax.set_yscale("log")
    ax.set_ylabel("comparisons (log scale)")
    ax.set_xlabel("algorithm (128 items)")
    ax.set_title("Comparisons depend on the algorithm and on the input")
    ax.legend(title="input")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "comparisons_by_input.png", dpi=120)

    ns = list(range(2, 61, 2))
    meas = [insertion_sort(make_input("reversed", m))[1] for m in ns]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(ns, [quad(m) for m in ns], label="n(n-1)/2")
    ax2.plot(ns, meas, "o", ms=4, label="insertion sort, reversed input")
    ax2.set_xlabel("n (items)")
    ax2.set_ylabel("comparisons")
    ax2.set_title("Measured counts sit on the formula")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "insertion_vs_formula.png", dpi=120)

    big = 1_000_000
    print("n = 1,000,000: n(n-1)/2 = %.4g, n log2 n = %.4g, ratio %.0f" % (quad(big), nlogn(big), cost_ratio(big)))
    print("at 1e9 steps per second: %.1f s versus %.3f s" % (seconds(quad(big)), seconds(nlogn(big))))
    for name in ALGORITHMS:
        print("stable?", name, is_stable(name))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
