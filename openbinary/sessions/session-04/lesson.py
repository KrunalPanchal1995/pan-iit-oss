"""Session 4 (Level 3): a carry-lookahead adder. Carries computed in parallel instead of rippling.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: a carry-lookahead adder
# **A. Real-world problem.** Session 3 built an adder that works for every input, but its carry
# ripples: the last carry waits for every carry before it, so the delay is 2n + 1 gate delays. A
# 16-bit ripple adder needs 33 gate delays and a 32-bit one needs 65, which is far too slow for the
# adder inside a processor that must finish in one clock tick. This session removes the wait. We
# work out what each stage will *generate* and *propagate*, write every carry directly in terms of
# those signals, and build two faster adders in the same simulator: a flat carry-lookahead adder
# and a parallel-prefix adder. Each one is checked against Python's own addition, and we count
# honestly what the speed costs in gates.
#
# **Plan.** (1) the simulator again, with the ripple adder as the baseline, (2) generate and
# propagate, (3) the carry equations and where a carry comes from, (4) the flat lookahead adder,
# (5) the parallel-prefix adder, (6) the cost of speed and how to choose, (7) see it.
# This is a simplified educational model: ideal gates with two inputs and a delay of 1 unit each,
# no wires, no fan-out limit, no clock and no real chip timing.

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the simulator and the ripple adder (from Session 3)
# A circuit is a list of gates. Each wire has a *depth*: 0 for an input, and 1 + the largest depth
# of its inputs for a gate output. Depth counts the gate delays on the longest path to that wire.
# Every gate here has two inputs (one for NOT), so a signal that depends on 17 inputs needs at
# least 5 levels of gates (2^5 = 32 >= 17). That limit is what keeps lookahead from being instant.

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


def half_adder(c, a, b):
    return c.gate("XOR", a, b), c.gate("AND", a, b)          # sum, carry


def full_adder(c, a, b, cin):
    s1, c1 = half_adder(c, a, b)
    s, c2 = half_adder(c, s1, cin)
    return s, c.gate("OR", c1, c2)                           # sum, carry out


def new_inputs(n):
    """A fresh circuit with inputs a0..a(n-1), b0..b(n-1) and cin."""
    c = Circuit()
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    return c, a, b, c.input("cin")


def build_ripple(n):
    """The Session 3 adder: n full adders in a chain. Returns a dict describing the adder."""
    c, a, b, cin = new_inputs(n)
    sums, carries, carry = [], [], cin
    for i in range(n):
        s, carry = full_adder(c, a[i], b[i], carry)
        sums.append(s)
        carries.append(carry)
    return {"c": c, "n": n, "a": a, "b": b, "cin": cin, "sum": sums, "carry": carries}


def bits_of(values, n):
    """Array of unsigned numbers -> list of n arrays (bit 0 first)."""
    values = np.asarray(values, dtype=np.int64)
    return [(values >> i) & 1 for i in range(n)]


def number_of(bit_arrays):
    """List of bit arrays (bit 0 first) -> array of unsigned numbers."""
    return sum(b.astype(np.int64) << i for i, b in enumerate(bit_arrays))


def add_bits(adder, a, b, cin=0):
    """Run a built adder on arrays of unsigned numbers a, b; returns (sum numbers, carry-out bits)."""
    n = adder["n"]
    a, b = np.broadcast_arrays(np.asarray(a), np.asarray(b))
    vals = {adder["cin"]: np.full(a.shape, cin)}
    for i, (x, y) in enumerate(zip(bits_of(a, n), bits_of(b, n))):
        vals[adder["a"][i]], vals[adder["b"][i]] = x, y
    w = adder["c"].run(vals)
    return number_of([w[s] for s in adder["sum"]]), w[adder["carry"][-1]]


def carry_delay(adder):
    """Gate delays until the last carry out is valid (longest path)."""
    return adder["c"].depth[adder["carry"][-1]]


def sum_delay(adder):
    return max(adder["c"].depth[s] for s in adder["sum"])


# %% [markdown]
# ## Step 2: generate and propagate
# Look at one stage with inputs a and b and ask what it does to a carry that arrives. Three cases:
# - a = b = 1: the stage **generates** a carry whatever arrives (g = a AND b = 1).
# - a and b differ: the stage **propagates**: a carry that arrives goes straight through, and
#   if none arrives none leaves (p = a XOR b = 1).
# - a = b = 0: the stage **kills** any carry that arrives. Both g and p are 0.
#
# Then the carry out of the stage is `c_next = g OR (p AND c)`, and the sum bit is `p XOR c`.
# The important fact: g and p depend only on the stage's own inputs, so they are ready after ONE
# gate delay in every stage at the same time. Nothing has to wait for a carry yet.

# %%
def generate_propagate(c, a_bits, b_bits):
    """Gates for p_i = a_i XOR b_i and g_i = a_i AND b_i. Returns (p wires, g wires)."""
    p = [c.gate("XOR", a, b) for a, b in zip(a_bits, b_bits)]
    g = [c.gate("AND", a, b) for a, b in zip(a_bits, b_bits)]
    return p, g


def stage_kind(a, b):
    """'generate', 'propagate' or 'kill' for one stage with input bits a and b."""
    return "generate" if a & b else ("propagate" if a ^ b else "kill")


# %% [markdown]
# ## Step 3: write the carries directly
# Substitute `c_next = g OR (p AND c)` into itself again and again. For the first four carries:
#
#     c1 = g0 + p0 cin
#     c2 = g1 + p1 g0 + p1 p0 cin
#     c3 = g2 + p2 g1 + p2 p1 g0 + p2 p1 p0 cin
#     c4 = g3 + p3 g2 + p3 p2 g1 + p3 p2 p1 g0 + p3 p2 p1 p0 cin
#
# (+ is OR, juxtaposition is AND.) Read the last line in words: a carry leaves stage 3 if stage 3
# generated one, or stage 2 generated one and stage 3 passes it on, or ... or the carry in made it
# all the way through. Every term uses only p, g and cin, so *all* carries can be computed at the
# same time. And **at most one term can be 1**: a stage that generates has p = 0, so it blocks any
# term that starts further down. So every carry has a single *source*, which `carry_sources` finds.

# %%
def carry_equation(i):
    """The text of the carry out of stage i (c1 is the carry out of stage 0)."""
    terms = []
    for j in range(i, -1, -1):
        terms.append(" ".join([f"p{k}" for k in range(i, j, -1)] + [f"g{j}"]))
    terms.append(" ".join([f"p{k}" for k in range(i, -1, -1)] + ["cin"]))
    return f"c{i + 1} = " + " + ".join(terms)


def carry_sources(a, b, n, cin=0):
    """For each stage i (0 to n-1): where the carry out of that stage came from.

    None: no carry. -1: the carry in travelled all the way. j >= 0: stage j generated it and
    every stage above j up to i propagated it.
    """
    p = [((a >> i) ^ (b >> i)) & 1 for i in range(n)]
    g = [((a >> i) & (b >> i)) & 1 for i in range(n)]
    out = []
    for i in range(n):
        src = None
        for j in range(i, -2, -1):
            if all(p[k] for k in range(j + 1, i + 1)):
                if (j >= 0 and g[j]) or (j == -1 and cin and all(p[k] for k in range(i + 1))):
                    src = j
                    break
            else:
                break
        out.append(src)
    return out


def longest_carry_run(a, b, n, cin=0):
    """Longest run of stages in a row that hold a carry (a data-dependent chain), for unsigned a + b + cin."""
    carry, run, best = cin, 0, 0
    for i in range(n):
        x, y = (a >> i) & 1, (b >> i) & 1
        carry = (x & y) | ((x ^ y) & carry)
        run = run + 1 if carry else 0
        best = max(best, run)
    return best


def mean_longest_run(n, trials=20000, seed=4):
    """Average longest carry run over random n-bit pairs (exact over all pairs when n <= 8)."""
    if n <= 8:
        runs = [longest_carry_run(x, y, n) for x in range(2 ** n) for y in range(2 ** n)]
    else:
        rng = np.random.default_rng(seed)
        A, B = rng.integers(0, 2 ** n, trials), rng.integers(0, 2 ** n, trials)
        runs = [longest_carry_run(int(x), int(y), n) for x, y in zip(A, B)]
    return float(np.mean(runs))


# %% [markdown]
# ## Step 4: the flat carry-lookahead adder
# To build `c_i` we need an AND of up to i + 1 signals for each term and an OR of up to i + 2
# terms. With two-input gates, `tree` joins signals in a balanced way, always combining the two
# *shallowest* wires first so the result is as shallow as possible. The sum bits are then
# `p XOR c`. This is the textbook idea written out in full, with no sharing between terms, so
# it is simple but wasteful in gates.

# %%
def tree(c, op, wires):
    """Combine wires with a two-input op, always joining the two shallowest first."""
    ws = list(wires)
    while len(ws) > 1:
        ws.sort(key=lambda w: c.depth[w])
        x, y = ws.pop(0), ws.pop(0)
        ws.append(c.gate(op, x, y))
    return ws[0]


def build_flat(n):
    """Flat carry-lookahead adder: every carry is a sum of products of p, g and cin."""
    c, a, b, cin = new_inputs(n)
    p, g = generate_propagate(c, a, b)
    carries, cs = [], [cin]
    for i in range(n):
        terms = [tree(c, "AND", [g[j]] + p[j + 1:i + 1]) for j in range(i + 1)]
        terms.append(tree(c, "AND", [cin] + p[:i + 1]))
        carries.append(tree(c, "OR", terms))
        cs.append(carries[-1])
    sums = [c.gate("XOR", p[i], cs[i]) for i in range(n)]
    return {"c": c, "n": n, "a": a, "b": b, "cin": cin, "sum": sums, "carry": carries}


# %% [markdown]
# ## Step 5: the parallel-prefix adder
# Flat lookahead repeats the same ANDs over and over. A smarter way joins stages in pairs. A *group*
# of stages has its own generate G (it makes a carry by itself) and propagate P (it passes a carry
# through). Two neighbouring groups, low and high, combine as
#
#     G = G_high OR (P_high AND G_low)        P = P_high AND P_low
#
# Doing this with distances 1, 2, 4, 8, ... (the Kogge-Stone pattern) gives every stage a group
# that reaches back to stage 0 after only log2(n) rounds. The carry in is folded into stage 0
# first. Each round costs 2 gate delays, so doubling the width adds just 2 gate delays.

# %%
def build_prefix(n):
    """Parallel-prefix (Kogge-Stone) adder: carries from log2(n) rounds of group combining."""
    c, a, b, cin = new_inputs(n)
    p, g = generate_propagate(c, a, b)
    G = [c.gate("OR", g[0], c.gate("AND", p[0], cin))] + g[1:]   # stage 0 absorbs the carry in
    P = list(p)
    d = 1
    while d < n:
        G2, P2 = list(G), list(P)
        for i in range(d, n):
            G2[i] = c.gate("OR", G[i], c.gate("AND", P[i], G[i - d]))
            P2[i] = c.gate("AND", P[i], P[i - d])
        G, P = G2, P2
        d *= 2
    cs = [cin] + G
    sums = [c.gate("XOR", p[i], cs[i]) for i in range(n)]
    return {"c": c, "n": n, "a": a, "b": b, "cin": cin, "sum": sums, "carry": G}


def prefix_gate_count(n):
    """Gates in build_prefix(n): 2n for p and g, 2 for the carry in, 3 per combine, n for the sums."""
    combines = sum(n - d for d in (2 ** k for k in range(n.bit_length())) if d < n)
    return 2 * n + 2 + 3 * combines + n


DESIGNS = {"ripple": build_ripple, "flat": build_flat, "prefix": build_prefix}


def build_design(name, n):
    return DESIGNS[name](n)


# %% [markdown]
# ## Step 6: checking and the cost of speed
# Correctness first: for widths up to 8 we try every pair and both carry-ins; for wider adders we
# try random pairs plus the nasty corners (all ones plus one, a long carry chain). Then we put
# numbers on the trade: gates against gate delays. `choose` lists the designs that meet a delay
# budget and a gate budget, cheapest first.

# %%
def corner_pairs(n):
    """Pairs that make long carry chains or sit at the ends of the range."""
    top = 2 ** n - 1
    half = 2 ** (n - 1)
    pairs = [(0, 0), (top, 0), (0, top), (top, 1), (1, top), (top, top), (half, half),
             (half - 1, 1), (half, half - 1), (top ^ 1, 1), (0x5555 & top, 0xAAAA & top)]
    return pairs


def mismatches(adder, trials=20000, seed=7):
    """Number of (a, b, cin) cases where the adder disagrees with Python. Exhaustive for n <= 8."""
    n = adder["n"]
    if n <= 8:
        A, B = np.meshgrid(np.arange(2 ** n), np.arange(2 ** n))
        A, B = A.ravel(), B.ravel()
    else:
        rng = np.random.default_rng(seed)
        cp = np.array(corner_pairs(n), dtype=np.int64)
        A = np.concatenate([rng.integers(0, 2 ** n, trials), cp[:, 0]])
        B = np.concatenate([rng.integers(0, 2 ** n, trials), cp[:, 1]])
    bad = 0
    for cin in (0, 1):
        s, co = add_bits(adder, A, B, cin)
        total = A + B + cin
        bad += int(np.sum((s != total % 2 ** n) | (co != total // 2 ** n)))
    return bad


def design_row(name, n):
    ad = build_design(name, n)
    return {"design": name, "n": n, "gates": ad["c"].size(),
            "carry_depth": carry_delay(ad), "sum_depth": sum_delay(ad)}


def design_table(widths=(4, 8, 16, 32)):
    return [design_row(name, n) for n in widths for name in DESIGNS]


def choose(n, max_delay, max_gates):
    """Designs at width n that meet both budgets, cheapest in gates first: list of rows."""
    rows = [design_row(name, n) for name in DESIGNS]
    ok = [r for r in rows if r["carry_depth"] <= max_delay and r["gates"] <= max_gates]
    return sorted(ok, key=lambda r: r["gates"])


def widest_within(name, max_delay, limit=32):
    """Widest n (up to limit) whose carry out is ready within max_delay gate delays."""
    return max((n for n in range(1, limit + 1) if design_row(name, n)["carry_depth"] <= max_delay), default=0)


def time_ns(depth, gate_ns=0.5):
    return depth * gate_ns


# %% [markdown]
# ## Step 7: see it
# Left: the carry-out delay against the width for the three designs, read from the simulator. The
# ripple line climbs steeply; the two lookahead lines grow by at most 2 gate delays per doubling. Right:
# the number of gates on a logarithmic axis, which is the price. Widths are powers of two, the
# natural sizes for the prefix adder.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    widths = [2, 4, 8, 16, 32]
    style = {"ripple": ("#c0561b", "o", "-", "ripple"), "flat": ("#0072b2", "s", "--", "flat lookahead"),
             "prefix": ("#8a1a5b", "^", ":", "parallel prefix")}
    rows = {name: [design_row(name, n) for n in widths] for name in DESIGNS}
    for n in (4, 8, 16, 32):
        for name in DESIGNS:
            r = design_row(name, n)
            print(f"{n:2d}-bit {name:6s}: {r['gates']:5d} gates, carry-out depth {r['carry_depth']:2d}, last sum depth {r['sum_depth']:2d}")
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.9))
    for name, (col, mk, ls, lab) in style.items():
        axs[0].plot(widths, [r["carry_depth"] for r in rows[name]], marker=mk, ls=ls, color=col, label=lab)
        axs[1].plot(widths, [r["gates"] for r in rows[name]], marker=mk, ls=ls, color=col, label=lab)
    axs[0].set_xlabel("adder width (bits)")
    axs[0].set_ylabel("carry-out delay (gate delays)")
    axs[0].set_title("Delay: ripple climbs, lookahead barely moves")
    axs[1].set_xlabel("adder width (bits)")
    axs[1].set_ylabel("gates (log scale)")
    axs[1].set_yscale("log")
    axs[1].set_title("Cost: the price of speed")
    for ax in axs:
        ax.set_xscale("log", base=2)
        ax.set_xticks(widths)
        ax.set_xticklabels([str(w) for w in widths])
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "lookahead_delay_cost.png", dpi=120)

    # the carry chain in a real sum: usually short, but the worst case sets the clock
    fig2, ax2 = plt.subplots(figsize=(5.6, 3.8))
    rng = np.random.default_rng(3)
    A, B = rng.integers(0, 2 ** 16, 20000), rng.integers(0, 2 ** 16, 20000)
    runs = np.array([longest_carry_run(int(x), int(y), 16) for x, y in zip(A, B)])
    ax2.hist(runs, bins=np.arange(0, 18) - 0.5, color="#0072b2")
    ax2.axvline(runs.mean(), color="#c0561b", ls="--", label=f"mean {runs.mean():.1f}")
    ax2.set_xticks(range(0, 17, 2))
    ax2.set_xlabel("longest carry run in one 16-bit sum (stages)")
    ax2.set_ylabel("number of random pairs")
    ax2.set_title("Usually short, but the worst case is 16")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "carry_runs.png", dpi=120)

    a, b = 0b1011, 0b0101
    print("example 11 + 5:", carry_sources(a, b, 4), "(carry out of stage 3 came from stage 0)")
    print(carry_equation(3))
    print("mean longest carry run, random 16-bit pairs:", round(float(runs.mean()), 2))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
