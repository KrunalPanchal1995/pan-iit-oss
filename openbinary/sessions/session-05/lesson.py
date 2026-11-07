"""Session 5 (Level 3): a 4-bit multiplier built from AND gates and adders.

Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: a multiplier from gates
# **A. Real-world problem.** The adder of Session 3 can add and subtract, but a processor also has
# to multiply: scaling a sound, mixing colours, computing an address. There is no multiply gate.
# Yet two 4-bit numbers can be multiplied with nothing more than AND gates and the half and full
# adders we already have. This session builds that multiplier in the gate simulator, tests it on
# all 256 input pairs against Python's own `*`, and then asks what it costs: how many gates,
# how long the slowest product bit takes, and why the answer needs twice as many bits as the
# inputs.
#
# **Plan.** (1) multiplying on paper in binary, (2) partial products from AND gates, (3) adding
# the rows with half and full adders, (4) the multiplier and its check, (5) size, delay and
# product width, (6) see it.
# This is a simplified educational model for unsigned numbers: ideal gates with a delay of 1 unit
# each, no wires, no clock, and no real chip timing.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the simulator and the adder cells (from Session 3)
# A circuit is a list of gates; each wire has a *depth*, the gate delays on its longest path. A half
# adder (XOR and AND) adds two bits, and a full adder (two half adders and an OR) adds two bits and
# a carry.

# %%
OPS = {
    "AND": lambda a, b: a & b,
    "OR": lambda a, b: a | b,
    "XOR": lambda a, b: a ^ b,
    "NAND": lambda a, b: 1 - (a & b),
    "NOT": lambda a: 1 - a,
}


class Circuit:
    def __init__(self):
        self.gates = []          # (output wire, op, input wires) in the order they were added
        self.depth = {}          # wire name -> gate delays from the inputs

    def input(self, name):
        self.depth[name] = 0
        return name

    def gate(self, op, *ins):
        out = f"w{len(self.gates)}"
        self.gates.append((out, op, ins))
        self.depth[out] = 1 + max(self.depth[i] for i in ins)
        return out

    def run(self, values):
        """values: dict input name -> array of 0/1. Returns every wire's array."""
        wires = {k: np.asarray(v, dtype=np.int64) for k, v in values.items()}
        for out, op, ins in self.gates:
            wires[out] = OPS[op](*[wires[i] for i in ins])
        return wires

    def size(self):
        return len(self.gates)

    def mix(self):
        """How many gates of each kind: {'AND': 36, ...}."""
        out = {}
        for _, op, _ in self.gates:
            out[op] = out.get(op, 0) + 1
        return out


def half_adder(c, a, b):
    return c.gate("XOR", a, b), c.gate("AND", a, b)          # sum, carry


def full_adder(c, a, b, cin):
    s1, c1 = half_adder(c, a, b)
    s, c2 = half_adder(c, s1, cin)
    return s, c.gate("OR", c1, c2)                           # sum, carry out


def bits_of(values, n):
    """Array of unsigned numbers -> list of n arrays (bit 0 first)."""
    values = np.asarray(values, dtype=np.int64)
    return [(values >> i) & 1 for i in range(n)]


def number_of(bit_arrays):
    """List of bit arrays (bit 0 first) -> array of unsigned numbers."""
    return sum(b.astype(np.int64) << i for i, b in enumerate(bit_arrays))


def ripple_adder_stats(n):
    """Gates and carry-out delay of the Session 3 ripple adder with n bits (for comparison)."""
    c = Circuit()
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    carry = c.input("cin")
    for i in range(n):
        _, carry = full_adder(c, a[i], b[i], carry)
    return c.size(), c.depth[carry]


# %% [markdown]
# ## Step 2: multiplying on paper, in binary
# Multiplying 13 x 11 on paper, you multiply 13 by each digit of 11 and add the rows, each shifted
# one place further left. In binary every digit is 0 or 1, so each row is either 0 or a copy of the
# first number, shifted. These rows are the **partial products**:
#
#       1101      13 x b0 (b0 = 1)
#      11010      13 x b1 (b1 = 1), shifted 1
#     000000      13 x b2 (b2 = 0), shifted 2
#    1101000      13 x b3 (b3 = 1), shifted 3
#    --------
#   10001111      = 143
#
# Column by column: add the ones in the column and the carry from the column before, write the
# total's last bit and carry the rest to the next column.

# %%
def partial_products(a, b, n):
    """The n partial products of a x b: row j is a shifted left j places if bit j of b is 1, else 0."""
    return [(a << j) if (b >> j) & 1 else 0 for j in range(n)]


def shift_and_add(a, b, n):
    """Multiply by adding the partial products."""
    return sum(partial_products(a, b, n))


def column_addition(a, b, n):
    """Add the partial products column by column, as on paper.

    Returns a list for columns 0 to 2n - 1 of dicts with: ones (partial-product bits that are 1 in
    this column), carry_in, total, bit (the product bit) and carry_out.
    """
    cols, carry = [], 0
    for k in range(2 * n):
        ones = sum(((a >> i) & 1) & ((b >> (k - i)) & 1) for i in range(n) if 0 <= k - i < n)
        total = ones + carry
        cols.append({"ones": ones, "carry_in": carry, "total": total, "bit": total % 2, "carry_out": total // 2})
        carry = total // 2
    return cols


# %% [markdown]
# ## Step 3: the partial products are AND gates
# Bit i of row j is `a_i AND b_j`: it is 1 only when both bits are 1. A 4 x 4 multiplier needs
# 16 AND gates, one for every cell of the paper layout, all working at once (depth 1).
#
# ## Step 4: add the rows with half and full adders
# We add the rows one at a time. In a column where two bits meet we use a half adder; where two
# bits and a carry meet we use a full adder; a lone bit passes straight through. The carry out of
# one cell goes to the next column of the same row. This regular grid of cells is called an
# **array multiplier**.

# %%
def partial_product_wires(c, a, b):
    """AND gates: pp[j][i] = a_i AND b_j."""
    return [[c.gate("AND", ai, bj) for ai in a] for bj in b]


def add_column(c, signals):
    """Add up to three bits in one column: returns (sum wire, carry wire or None). None means 'no wire'."""
    sigs = [s for s in signals if s is not None]
    if len(sigs) == 1:
        return sigs[0], None
    if len(sigs) == 2:
        return half_adder(c, *sigs)
    return full_adder(c, *sigs)


def build_multiplier(n):
    """An n x n unsigned array multiplier (n >= 2). Returns a dict describing it; 'product' has 2n wires."""
    c = Circuit()
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{j}") for j in range(n)]
    pp = partial_product_wires(c, a, b)
    acc = [None] * (2 * n)
    for i in range(n):
        acc[i] = pp[0][i]
    for j in range(1, n):
        carry = None
        for i in range(n):
            acc[j + i], carry = add_column(c, [acc[j + i], pp[j][i], carry])
        acc[j + n] = carry
    return {"c": c, "n": n, "a": a, "b": b, "product": acc}


def multiply(mult, a, b):
    """Run a built multiplier on arrays of unsigned numbers; returns the products."""
    n = mult["n"]
    a, b = np.broadcast_arrays(np.asarray(a), np.asarray(b))
    vals = {}
    for i, (x, y) in enumerate(zip(bits_of(a, n), bits_of(b, n))):
        vals[mult["a"][i]], vals[mult["b"][i]] = x, y
    w = mult["c"].run(vals)
    return number_of([w[p] for p in mult["product"]])


def mismatches(mult, trials=20000, seed=5):
    """Number of input pairs where the multiplier disagrees with Python's a * b.

    Every pair is tried for n <= 8; wider multipliers get random pairs plus the extremes.
    """
    n = mult["n"]
    if n <= 8:
        A, B = np.meshgrid(np.arange(2 ** n), np.arange(2 ** n))
        A, B = A.ravel(), B.ravel()
    else:
        rng = np.random.default_rng(seed)
        top = 2 ** n - 1
        A = np.concatenate([rng.integers(0, 2 ** n, trials), [0, top, top, 1, top]])
        B = np.concatenate([rng.integers(0, 2 ** n, trials), [top, 0, top, top, 1]])
    return int(np.sum(multiply(mult, A, B) != A * B))


# %% [markdown]
# ## Step 5: size, delay and the width of the answer
# We can count the gates and read the delay of every product bit from the simulator. Each
# of the n rows after the first needs n adder cells, so the gate count grows with n squared, while
# the longest path runs down through the rows, so the delay grows in step with n. An n-bit number
# is at most 2^n - 1, so the product is at most (2^n - 1)^2 < 2^(2n): it needs 2n bits and can
# never overflow if you keep them all. Keep only the low n bits, as a narrow chip might, and
# most answers are wrong.

# %%
def gate_count_formula(n):
    """6n^2 - 8n: n^2 AND gates, n half adders (2 gates) and n(n - 2) full adders (5 gates)."""
    return 6 * n * n - 8 * n


def product_delays(mult):
    """Gate delays until each product bit is valid, bit 0 first."""
    return [mult["c"].depth[p] for p in mult["product"]]


def design_row(n):
    m = build_multiplier(n)
    return {"n": n, "gates": m["c"].size(), "depth": max(product_delays(m)), "bits": len(m["product"])}


def design_table(widths=range(2, 11)):
    return [design_row(n) for n in widths]


def widest_within(max_delay, limit=16):
    """Widest n (2 to limit) whose slowest product bit is ready within max_delay gate delays."""
    return max((n for n in range(2, limit + 1) if design_row(n)["depth"] <= max_delay), default=0)


def low_half(product, n):
    """What a multiplier that keeps only n bits would return."""
    return product % (2 ** n)


def time_ns(depth, gate_ns=0.5):
    return depth * gate_ns


# %% [markdown]
# ## Step 6: see it
# Left: all 256 products of two 4-bit numbers (a down the side, b along the bottom): symmetric,
# zero along the first row and column, and up to 225 at the corner. Right: the gates and the
# delay of the array multiplier against n, read from the simulator.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m4 = build_multiplier(4)
    A, B = np.meshgrid(np.arange(16), np.arange(16))
    P = multiply(m4, A.ravel(), B.ravel()).reshape(16, 16)
    print(f"4 x 4 multiplier: {m4['c'].size()} gates {m4['c'].mix()}, product-bit delays {product_delays(m4)}")
    print("all 256 pairs match Python:", mismatches(m4) == 0)
    fig, ax = plt.subplots(figsize=(5.8, 4.8))
    im = ax.imshow(P, cmap="YlOrBr", origin="lower", extent=(-0.5, 15.5, -0.5, 15.5))
    ax.set_xlabel("b (4 bits)")
    ax.set_ylabel("a (4 bits)")
    ax.set_title("Product from the gate-level multiplier")
    fig.colorbar(im, ax=ax, label="a x b (8-bit product)")
    fig.tight_layout()
    fig.savefig(OUT / "product_table.png", dpi=120)

    rows = design_table()
    ns = [r["n"] for r in rows]
    fig2, axs = plt.subplots(1, 2, figsize=(9.6, 3.8))
    axs[0].plot(ns, [r["gates"] for r in rows], "o-", color="#0072b2")
    axs[0].set_xlabel("multiplier width n (bits)")
    axs[0].set_ylabel("gates")
    axs[0].set_title("Size grows as n squared (6n^2 - 8n)")
    axs[1].plot(ns, [r["depth"] for r in rows], "s--", color="#c0561b")
    axs[1].axhline(20, color="#8a1a5b", ls=":", label="10 ns budget (20 gate delays)")
    axs[1].set_xlabel("multiplier width n (bits)")
    axs[1].set_ylabel("slowest product bit (gate delays)")
    axs[1].set_title("Delay grows in step with n (6n - 8)")
    axs[1].legend()
    for a_ in axs:
        a_.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "size_delay.png", dpi=120)
    for r in rows:
        print(f"n = {r['n']:2d}: {r['gates']:4d} gates, slowest product bit after {r['depth']:2d} gate delays")
    print("7 x 3 columns:", [(c["ones"], c["carry_in"], c["bit"]) for c in column_addition(7, 3, 4)][:5])
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
