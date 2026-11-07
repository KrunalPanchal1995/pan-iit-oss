"""Session 1 (Level 1): data as black and white squares, and a check digit that catches mistakes.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: squares of data, and the check digit
# **A. Real-world problem.** A shop scanner reads a barcode in a fraction of a second. A smudge,
# a bad print or a typed mistake could turn one number into another. How does the scanner know
# the number it read is probably right?
#
# **Plan.** (1) turn text into black and white squares, (2) compute the EAN-13 check digit,
# (3) test a few real-format numbers, (4) measure what a check digit catches and what it misses.

# %%
import itertools
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: data is just black and white
# A computer stores a letter as a number, and a number as 0s and 1s. Call 1 a black square and
# 0 a white square. The letter `A` is number 65, which is 01000001 in binary (64 + 1).
# Eight squares make one letter. This is the idea behind every barcode and QR code.

# %%
def text_to_bits(text):
    """Each character -> 8 bits (ASCII code, most significant bit first)."""
    return np.array([(ord(ch) >> k) & 1 for ch in text for k in range(7, -1, -1)], dtype=int)


def bits_to_grid(bits, width):
    """Lay the bits in rows of `width` squares (pad with white at the end)."""
    n = -(-len(bits) // width) * width
    padded = np.zeros(n, dtype=int)
    padded[: len(bits)] = bits
    return padded.reshape(-1, width)


def grid_art(grid):
    """Text picture: '#' is black (1), '.' is white (0)."""
    return "\n".join("".join("#" if v else "." for v in row) for row in grid)


# %% [markdown]
# ## Step 2: the EAN-13 check digit
# Shop barcodes (EAN-13) hold 13 digits. The last one is a *check digit* computed from the
# first 12. Rule: multiply the 12 digits by weights 1, 3, 1, 3, ... (from the left), add them up,
# and choose the check digit so that the total ends in 0.
#
# Section E of the README does one example fully by hand; the code below does it for any number.

# %%
WEIGHTS = [1, 3] * 6          # weights for the first 12 digits


def weighted_sum(digits):
    """Sum of digit * weight, weights 1, 3, 1, 3, ... from the left (any length)."""
    return sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))


def ean13_check_digit(first12):
    """The 13th digit for a string of 12 digits."""
    return (10 - weighted_sum(first12) % 10) % 10


def ean13_is_valid(code):
    """True if a 13-digit string passes the check (weighted sum of all 13 ends in 0)."""
    return len(code) == 13 and code.isdigit() and weighted_sum(code) % 10 == 0


# real-format example numbers (each has a correct check digit)
EXAMPLES = ["4006381333931", "5901234123457", "9780306406157"]


# %% [markdown]
# ## Step 3: what does a check digit catch?
# Two kinds of human mistake: (a) one digit wrong, (b) two neighbouring digits swapped.
# We test every possible case by brute force. (Because 3 and 10 share no factor, a wrong digit
# in any place changes the sum by a non-multiple of 10, so (a) is always caught. A swap of
# neighbours a, b changes the sum by 2(a - b), which is a multiple of 10 only when a - b = +-5.)

# %%
def single_error_detection(code):
    """Fraction of all one-digit substitutions (13 places x 9 wrong digits) that are caught."""
    caught = total = 0
    for pos in range(13):
        for new in "0123456789":
            if new == code[pos]:
                continue
            bad = code[:pos] + new + code[pos + 1:]
            total += 1
            caught += not ean13_is_valid(bad)
    return caught / total


def swap_detection(code):
    """Fraction of neighbour swaps of unequal digits that are caught."""
    caught = total = 0
    for pos in range(12):
        if code[pos] == code[pos + 1]:
            continue
        bad = code[:pos] + code[pos + 1] + code[pos] + code[pos + 2:]
        total += 1
        caught += not ean13_is_valid(bad)
    return caught / total


def double_error_detection(code):
    """Fraction of all ways to change TWO different digits (to any other digits) that are caught."""
    caught = total = 0
    for i, j in itertools.combinations(range(13), 2):
        for a in "0123456789":
            for b in "0123456789":
                if a == code[i] or b == code[j]:
                    continue
                bad = list(code)
                bad[i], bad[j] = a, b
                total += 1
                caught += not ean13_is_valid("".join(bad))
    return caught / total


def swap_detection_all_pairs():
    """Exact answer over every ordered pair of different digits (a, b) side by side."""
    pairs = [(a, b) for a, b in itertools.product(range(10), repeat=2) if a != b]
    missed = [(a, b) for a, b in pairs if (2 * (a - b)) % 10 == 0]
    return 1 - len(missed) / len(pairs), missed


def mod11_swap_detection():
    """A stronger idea: weights 7, 6, 5, 4, 3, 2 modulo 11. Fraction of neighbour swaps caught (exact)."""
    w = [7, 6, 5, 4, 3, 2]
    caught = total = 0
    for k in range(5):
        for a, b in itertools.product(range(10), repeat=2):
            if a != b:
                total += 1
                caught += ((w[k] * a + w[k + 1] * b) - (w[k] * b + w[k + 1] * a)) % 11 != 0
    return caught / total


# %% [markdown]
# ## Step 4: see it
# Left: the word `QR` as squares. Right: for the first example number, the weighted sum
# when ONE digit is replaced; the code is valid only when the sum ends in 0.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    bits = text_to_bits("QR")
    print("QR as bits:", "".join(map(str, bits)))
    print(grid_art(bits_to_grid(bits, 8)))
    for code in EXAMPLES:
        print(f"{code}: check digit of first 12 = {ean13_check_digit(code[:12])}, valid = {ean13_is_valid(code)}")
    rates = [(single_error_detection(c), swap_detection(c)) for c in EXAMPLES]
    print("single-digit errors caught:", [f"{a:.0%}" for a, _ in rates])
    frac, missed = swap_detection_all_pairs()
    dbl = double_error_detection(EXAMPLES[0])
    print("mod-11 weights catch neighbour swaps:", mod11_swap_detection())
    print(f"two wrong digits caught: {dbl:.1%}")
    print(f"neighbour swaps caught (all digit pairs): {frac:.1%}; missed pairs {missed}")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.6))
    g = bits_to_grid(bits, 8)
    axs[0].imshow(1 - g, cmap="gray", vmin=0, vmax=1)
    axs[0].set_xticks(range(8)); axs[0].set_yticks(range(2))
    axs[0].set_xlabel("bit position in the letter (0 = leftmost)")
    axs[0].set_ylabel("letter (0 = Q, 1 = R)")
    axs[0].set_title("'QR' as 16 squares (black = 1)")

    code = EXAMPLES[0]
    pos = 4                                       # replace the 5th digit
    sums = []
    for d in range(10):
        bad = code[:pos] + str(d) + code[pos + 1:]
        sums.append(weighted_sum(bad) % 10)
    colors = ["tab:green" if s == 0 else "tab:red" for s in sums]
    axs[1].bar(range(10), sums, color=colors)
    axs[1].set_xticks(range(10))
    axs[1].set_xlabel("digit written in place 5")
    axs[1].set_ylabel("weighted sum mod 10 (0 = valid)")
    axs[1].set_title("Only the true digit (3) gives a valid number")
    fig.tight_layout()
    fig.savefig(OUT / "squares_and_check.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 3.6))
    ax2.bar(["one wrong digit", "neighbours swapped", "two digits wrong\n(random)"],
            [100 * rates[0][0], 100 * frac, 100 * dbl], color=["tab:green", "tab:orange", "tab:blue"])
    ax2.set_ylabel("mistakes caught (percent)")
    ax2.set_ylim(0, 105)
    ax2.set_title("What the EAN-13 check digit catches")
    fig2.tight_layout()
    fig2.savefig(OUT / "what_is_caught.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
