"""Session 2 (Level 2): number systems, logic gates and Boolean algebra.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: converting numbers, and gates that decide
# **A. Real-world problem.** A stairwell light has a switch at the top and one at the bottom.
# Either switch must toggle the light. A lift must refuse to move unless the door is closed AND
# the load is allowed. Such rules are built from *logic gates*, tiny circuits whose output is 0 or
# 1 and depends only on their inputs. Before that, we need to move numbers between the three
# writing systems engineers use: binary (base 2), decimal (base 10) and hexadecimal (base 16).
#
# **Plan.** (1) write converters and test them on thousands of numbers, (2) define the gates and
# print their truth tables, (3) verify De Morgan's laws by trying every input, (4) build NOT, AND,
# OR and XOR from NAND alone, (5) design a majority gate and a comparator from a truth table.
# This is a simplified educational model of digital logic (ideal gates, no electrical detail).

# %%
import itertools
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

DIGITS = "0123456789ABCDEF"


# %% [markdown]
# ## Step 1: place value in any base
# In base b the digit string d_k ... d_1 d_0 means d_k * b^k + ... + d_1 * b + d_0.
# To go the other way, divide by b again and again and collect the remainders (last one first).
# Hexadecimal uses the digits 0-9 and A-F (A = 10 ... F = 15); one hex digit is exactly 4 bits.

# %%
def to_base(n, base):
    """Whole number n >= 0 as a digit string in the given base (2 to 16)."""
    if n < 0:
        raise ValueError("only whole numbers from 0 up")
    if n == 0:
        return "0"
    out = []
    while n:
        n, r = divmod(n, base)
        out.append(DIGITS[r])
    return "".join(reversed(out))


def from_base(text, base):
    """Digit string in the given base back to a whole number (place values added up)."""
    value = 0
    for ch in text.upper():
        d = DIGITS.index(ch)
        if d >= base:
            raise ValueError(f"digit {ch} is not allowed in base {base}")
        value = value * base + d
    return value


def bin_to_hex(bits):
    """Group the bits in fours from the right; each group is one hex digit."""
    bits = bits.zfill(-(-len(bits) // 4) * 4)
    return "".join(to_base(from_base(bits[i:i + 4], 2), 16) for i in range(0, len(bits), 4))


# %% [markdown]
# ## Step 2: the gates
# A gate takes bits and returns a bit. We write them with numpy so one call handles many
# inputs at once (arrays of 0s and 1s).
#
#     AND  : 1 only if both inputs are 1       OR   : 1 if at least one input is 1
#     NOT  : flips the bit                      XOR  : 1 if the inputs are different
#     NAND : NOT of AND (0 only if both are 1)

# %%
def AND(a, b):
    return np.asarray(a) & np.asarray(b)


def OR(a, b):
    return np.asarray(a) | np.asarray(b)


def NOT(a):
    return 1 - np.asarray(a)


def XOR(a, b):
    return np.asarray(a) ^ np.asarray(b)


def NAND(a, b):
    return 1 - (np.asarray(a) & np.asarray(b))


def all_inputs(n):
    """Every combination of n input bits: shape (2**n, n), first column is the biggest place."""
    return np.array(list(itertools.product((0, 1), repeat=n)), dtype=int)


def truth_table(gate, n=2):
    """Rows of inputs followed by the output of the gate on that row."""
    X = all_inputs(n)
    return np.column_stack([X, gate(*X.T)])


# %% [markdown]
# ## Step 3: De Morgan's laws, proved by trying everything
# With two inputs there are only 4 combinations, with three only 8. A claim that holds for every
# row of the truth table is *proved*, not just tested. De Morgan:
# NOT(a AND b) = (NOT a) OR (NOT b)  and  NOT(a OR b) = (NOT a) AND (NOT b).

# %%
def de_morgan_holds(n_inputs=2):
    """True if both De Morgan laws hold on every row of the truth table (any number of inputs)."""
    X = all_inputs(n_inputs).T
    all_and, all_or = X[0], X[0]
    or_of_nots, and_of_nots = NOT(X[0]), NOT(X[0])
    for row in X[1:]:
        all_and, all_or = AND(all_and, row), OR(all_or, row)
        or_of_nots, and_of_nots = OR(or_of_nots, NOT(row)), AND(and_of_nots, NOT(row))
    law1 = np.array_equal(NOT(all_and), or_of_nots)    # NOT(a AND b ...) = NOT a OR NOT b ...
    law2 = np.array_equal(NOT(all_or), and_of_nots)    # NOT(a OR b ...) = NOT a AND NOT b ...
    return bool(law1 and law2)


# %% [markdown]
# ## Step 4: NAND alone is enough
# NOT a = NAND(a, a). AND = NOT(NAND). OR(a, b) = NAND(NOT a, NOT b) (De Morgan again).
# XOR needs four NAND gates. `nand` is a parameter so that a checkpoint can count the gates used.

# %%
def not_n(a, nand=NAND):
    return nand(a, a)


def and_n(a, b, nand=NAND):
    return not_n(nand(a, b), nand)


def or_n(a, b, nand=NAND):
    return nand(not_n(a, nand), not_n(b, nand))


def xor_n(a, b, nand=NAND):
    m = nand(a, b)
    return nand(nand(a, m), nand(b, m))


def counting_nand():
    """A NAND gate that counts how many times it is used: returns (gate, counter_list)."""
    counter = [0]

    def gate(a, b):
        counter[0] += 1
        return NAND(a, b)

    return gate, counter


# %% [markdown]
# ## Step 5: designing a gate from a truth table (sum of products)
# Write the wanted output for every input row. Each row with output 1 becomes one AND term
# (a *minterm*) that is true for exactly that row; OR the terms together. This always works.
# Example 1: a 3-input *majority* gate (1 when at least two inputs are 1).
# Example 2: a 2-bit comparator, output 1 when the number A = (a1 a0) is greater than B = (b1 b0).

# %%
def minterms(outputs):
    """Row numbers (0 = all inputs 0) where the wanted output is 1."""
    return [i for i, o in enumerate(outputs) if o == 1]


def sop_eval(terms, n, X):
    """Evaluate the sum of products on rows X (shape (rows, n)): OR over minterms of an AND of literals."""
    X = np.asarray(X)
    out = np.zeros(len(X), dtype=int)
    for t in terms:
        bits = [(t >> (n - 1 - k)) & 1 for k in range(n)]
        term = np.ones(len(X), dtype=int)
        for k, want in enumerate(bits):
            term = AND(term, X[:, k] if want else NOT(X[:, k]))
        out = OR(out, term)
    return out


def majority_outputs():
    return [1 if sum(row) >= 2 else 0 for row in all_inputs(3)]


def greater_outputs():
    """Rows are (a1, a0, b1, b0); output 1 when 2*a1 + a0 > 2*b1 + b0."""
    return [1 if 2 * r[0] + r[1] > 2 * r[2] + r[3] else 0 for r in all_inputs(4)]


def majority_short(a, b, c):
    """The simplified form a.b + a.c + b.c."""
    return OR(OR(AND(a, b), AND(a, c)), AND(b, c))


def greater_short(a1, a0, b1, b0):
    """Simplified: a1.(NOT b1) + (a1 XNOR b1).a0.(NOT b0)."""
    same = NOT(XOR(a1, b1))
    return OR(AND(a1, NOT(b1)), AND(AND(same, a0), NOT(b0)))


# %% [markdown]
# ## Step 6: see it
# Left: the truth tables of four gates as a grid. Right: the comparator, with A down the side and
# B along the top, 1 where A > B.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for n in (5, 10, 183, 255, 4095):
        print(f"{n:5d} = {to_base(n, 2)} (binary) = {to_base(n, 16)} (hex)")
    gates = [("AND", AND), ("OR", OR), ("XOR", XOR), ("NAND", NAND)]
    fig, ax = plt.subplots(figsize=(6, 3.4))
    grid = np.array([[g(a, b) for g_name, g in gates] for a, b in all_inputs(2)])
    ax.imshow(grid, cmap="YlOrBr", vmin=0, vmax=1.4, aspect="auto")
    for (r, c), v in np.ndenumerate(grid):
        ax.text(c, r, str(v), ha="center", va="center")
    ax.set_xticks(range(4), [g[0] for g in gates])
    ax.set_yticks(range(4), [f"a={a} b={b}" for a, b in all_inputs(2)])
    ax.set_xlabel("gate")
    ax.set_ylabel("inputs")
    ax.set_title("Truth tables: output of each gate (1 = lamp on)")
    fig.tight_layout()
    fig.savefig(OUT / "gate_truth_tables.png", dpi=120)

    cmp = np.zeros((4, 4), dtype=int)
    for A in range(4):
        for B in range(4):
            cmp[A, B] = greater_short(A >> 1, A & 1, B >> 1, B & 1)
    fig2, ax2 = plt.subplots(figsize=(4.4, 4))
    ax2.imshow(cmp, cmap="YlOrBr", vmin=0, vmax=1.4)
    for (r, c), v in np.ndenumerate(cmp):
        ax2.text(c, r, str(v), ha="center", va="center")
    ax2.set_xticks(range(4))
    ax2.set_yticks(range(4))
    ax2.set_xlabel("B (decimal value of b1 b0)")
    ax2.set_ylabel("A (decimal value of a1 a0)")
    ax2.set_title("Comparator output: 1 where A > B")
    fig2.tight_layout()
    fig2.savefig(OUT / "comparator.png", dpi=120)
    print("majority minterm rows:", minterms(majority_outputs()))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
