"""Session 1 (Level 1): sorting cards by hand is an algorithm.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: the way you sort cards is an algorithm
# **A. Real-world problem.** You hold a hand of playing cards and put them in order. You do
# not think about it, yet you follow rules. Write the rules down exactly and a computer can
# follow them on a million cards. Two simple rule sets are *bubble sort* and *insertion sort*.
#
# **Plan.** (1) write the two rule sets as Python, (2) count the steps they take
# (comparisons and swaps), (3) see that the steps depend on how mixed up the cards start,
# (4) draw the cards as bars before and after.

# %%
import pathlib

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: bubble sort
# Look at two neighbouring cards. If the left one is bigger, swap them. Walk along the row
# doing this; the biggest card "bubbles" to the right end. Repeat on the shorter row that is left.
# Stop early if a whole walk needed no swap, because then the row is already in order.
#
# We count every *comparison* (looking at two cards) and every *swap* (exchanging two neighbours).

# %%
def bubble_sort(values):
    """Return (sorted list, comparisons, swaps). The input list is not changed."""
    a = list(values)
    comparisons = swaps = 0
    for end in range(len(a) - 1, 0, -1):
        swapped = False
        for j in range(end):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return a, comparisons, swaps


# %% [markdown]
# ## Step 2: insertion sort
# This is how most people sort a hand of cards. Take the next card and slide it left past every
# bigger card until it fits. The cards on the left are always in order.
# Each one-place slide is counted as a swap (a one-place move).

# %%
def insertion_sort(values):
    """Return (sorted list, comparisons, swaps). The input list is not changed."""
    a = list(values)
    comparisons = swaps = 0
    for i in range(1, len(a)):
        j = i
        while j > 0:
            comparisons += 1
            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                swaps += 1
                j -= 1
            else:
                break
    return a, comparisons, swaps


# %% [markdown]
# ## Step 3: how mixed up is the row?
# An *inversion* is a pair of cards that is in the wrong order (the bigger one is to the left).
# Each swap of two neighbours removes exactly one inversion, so the number of swaps both methods
# need equals the number of inversions. A sorted row has 0 inversions; a reversed row of n cards
# has the most, n(n-1)/2.

# %%
def inversions(values):
    a = list(values)
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])


def prefix_reversed(n, k):
    """Cards 1..n in order, except that the first k cards are reversed (k = 0 or 1 changes nothing)."""
    k = max(0, min(k, n))
    return list(range(k, 0, -1)) + list(range(k + 1, n + 1))


def is_sorted(values):
    return all(values[i] <= values[i + 1] for i in range(len(values) - 1))


# %% [markdown]
# ## Step 4: see it
# Left: a row of 12 cards drawn as bars, before and after. Right: the steps each method takes as
# the first k cards of a 30-card row are reversed (k = 0 is already sorted, k = 30 is fully reversed).

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    hand = [7, 3, 11, 1, 9, 5, 12, 2, 10, 4, 8, 6]
    result, c, s = bubble_sort(hand)
    print("12 cards:", hand, "->", result, "| comparisons", c, "swaps", s, "inversions", inversions(hand))
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2), sharey=True)
    axs[0].bar(range(len(hand)), hand, color="#d9534f")
    axs[0].set_title("before: %d inversions" % inversions(hand))
    axs[1].bar(range(len(result)), result, color="#2a9d8f")
    axs[1].set_title("after: 0 inversions")
    for ax in axs:
        ax.set_xlabel("position in the row")
    axs[0].set_ylabel("card value")
    fig.tight_layout()
    fig.savefig(OUT / "bars_before_after.png", dpi=120)

    n = 30
    ks = list(range(0, n + 1))
    bc, bs, ic, is_ = [], [], [], []
    for k in ks:
        row = prefix_reversed(n, k)
        bc.append(bubble_sort(row)[1]); bs.append(bubble_sort(row)[2])
        ic.append(insertion_sort(row)[1]); is_.append(insertion_sort(row)[2])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(ks, bc, label="bubble comparisons")
    ax2.plot(ks, ic, label="insertion comparisons")
    ax2.plot(ks, bs, "--", label="swaps (both methods)")
    ax2.set_xlabel("k = how many leading cards are reversed (30 cards)")
    ax2.set_ylabel("steps counted")
    ax2.set_title("Steps grow with the disorder")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "steps_vs_disorder.png", dpi=120)
    print("fully reversed 30 cards: bubble", bubble_sort(prefix_reversed(30, 30))[1:], "insertion", insertion_sort(prefix_reversed(30, 30))[1:])
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
