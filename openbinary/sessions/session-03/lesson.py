"""Session 3 (Level 3): a gate-level simulator, adders, two's complement and a tiny ALU.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: building arithmetic out of gates
# **A. Real-world problem.** Inside a processor there is no "plus" button, only gates. Yet it adds
# very many numbers every second, subtracts, and knows when an answer does not fit. We build that
# from scratch: a tiny simulator where a circuit is a list of gates, then a half adder, a full
# adder, a 4-bit ripple-carry adder, subtraction by two's complement, and a 4-bit ALU slice. Every
# circuit is checked against Python's own integer arithmetic for every possible input.
#
# **Plan.** (1) the simulator, (2) adders, (3) negative numbers and overflow, (4) how long the
# carry takes to ripple (gate delays), (5) the ALU, (6) a seven-segment decoder as a stretch.
# This is a simplified educational model: ideal gates, each with the same delay of 1 unit, no
# wires, no clock and no real chip timing.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a gate-level simulator
# A *wire* is a name. A *gate* reads one or two wires and creates a new wire. Values are numpy
# arrays of 0/1, so one `run` tests thousands of input combinations at once. Each wire also has a
# *depth*: 0 for an input, and 1 + the largest depth of its inputs for a gate output. Depth counts
# gate delays on the longest path to that wire.

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


# %% [markdown]
# ## Step 2: half adder, full adder, ripple-carry adder
# Adding two bits: the *sum* bit is 1 when the inputs differ (XOR) and the *carry* is 1 when both
# are 1 (AND). That is a **half adder**. A **full adder** also takes a carry in: two half adders and
# an OR. Chain n full adders, carry out of one into the next, and you have an n-bit
# **ripple-carry adder**.

# %%
def half_adder(c, a, b):
    return c.gate("XOR", a, b), c.gate("AND", a, b)          # sum, carry


def full_adder(c, a, b, cin):
    s1, c1 = half_adder(c, a, b)
    s, c2 = half_adder(c, s1, cin)
    return s, c.gate("OR", c1, c2)                           # sum, carry out


def ripple_adder(c, a_bits, b_bits, cin):
    """a_bits, b_bits: wire names, least significant bit first. Returns (sum wires, carry-out wires)."""
    sums, carries, carry = [], [], cin
    for a, b in zip(a_bits, b_bits):
        s, carry = full_adder(c, a, b, carry)
        sums.append(s)
        carries.append(carry)
    return sums, carries


def build_adder(n):
    """An n-bit adder with inputs a0..a(n-1), b0..b(n-1), cin. Returns a dict describing it."""
    c = Circuit()
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    cin = c.input("cin")
    sums, carries = ripple_adder(c, a, b, cin)
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


# %% [markdown]
# ## Step 3: negative numbers, subtraction and overflow
# With n bits, *two's complement* reads the pattern u as u if u < 2^(n-1), else u - 2^n. So 4 bits
# cover -8 to 7, and 1111 means -1. To negate: flip every bit and add 1. Then a - b is just
# a + (NOT b) + 1, so one adder does both jobs: XOR every b bit with a `sub` control and feed `sub`
# in as the carry in. *Overflow* (the true answer does not fit) happens exactly when the carry into the
# top bit differs from the carry out of it.

# %%
def to_twos(v, n):
    """Signed integer -> n-bit pattern (an unsigned number)."""
    return v % (2 ** n)


def from_twos(u, n):
    """n-bit pattern -> signed integer."""
    u = np.asarray(u)
    return np.where(u >= 2 ** (n - 1), u - 2 ** n, u)


def build_add_sub(n):
    """n-bit adder-subtractor: sub = 0 gives a + b, sub = 1 gives a - b. Has an overflow flag (n >= 2)."""
    c = Circuit()
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    sub = c.input("sub")
    bx = [c.gate("XOR", bi, sub) for bi in b]
    sums, carries = ripple_adder(c, a, bx, sub)
    overflow = c.gate("XOR", carries[n - 2], carries[n - 1])
    return {"c": c, "n": n, "a": a, "b": b, "sub": sub, "sum": sums, "carry": carries, "overflow": overflow}


def add_sub(circ, a, b, sub):
    """a, b: arrays of signed integers; sub: 0 or 1. Returns (signed result, overflow flag)."""
    n = circ["n"]
    ua, ub = to_twos(np.asarray(a), n), to_twos(np.asarray(b), n)
    ua, ub = np.broadcast_arrays(ua, ub)
    vals = {circ["sub"]: np.full(ua.shape, sub)}
    for i, (x, y) in enumerate(zip(bits_of(ua, n), bits_of(ub, n))):
        vals[circ["a"][i]], vals[circ["b"][i]] = x, y
    w = circ["c"].run(vals)
    return from_twos(number_of([w[s] for s in circ["sum"]]), n), w[circ["overflow"]]


def python_reference(a, b, sub, n):
    """What Python says: (result wrapped into n bits as a signed number, true result did not fit)."""
    true = a - b if sub else a + b
    wrapped = int(from_twos(to_twos(true, n), n))
    return wrapped, int(true != wrapped)


# %% [markdown]
# ## Step 4: how long does the carry take?
# Each gate takes one unit of delay. In a ripple adder the carry out of stage i is needed by stage
# i+1, so the delay of the last carry grows with the number of bits. We read it off the
# simulator's `depth`. This is why real processors use faster carry circuits (carry-lookahead,
# a stretch topic) instead of rippling.

# %%
def carry_delay(adder):
    """Gate delays until the last carry out is valid (longest path)."""
    return adder["c"].depth[adder["carry"][-1]]


def sum_delay(adder):
    return max(adder["c"].depth[s] for s in adder["sum"])


def longest_carry_run(a, b, n):
    """Longest run of stages in a row that pass a carry on (a data-dependent chain), for unsigned a + b."""
    carry, run, best = 0, 0, 0
    for i in range(n):
        x, y = (a >> i) & 1, (b >> i) & 1
        carry = (x & y) | ((x ^ y) & carry)
        run = run + 1 if carry else 0
        best = max(best, run)
    return best


# %% [markdown]
# ## Step 5: a 4-bit ALU slice
# An ALU (arithmetic logic unit) does several operations on the same inputs and a 2-bit control
# code picks which one comes out: 00 add, 01 subtract, 10 AND, 11 OR. We select with AND gates
# and an OR, all inside the simulator.

# %%
OP_ADD, OP_SUB, OP_AND, OP_OR = 0, 1, 2, 3


def build_alu(n=4):
    c = Circuit()
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    op1, op0 = c.input("op1"), c.input("op0")
    not1, not0 = c.gate("NOT", op1), c.gate("NOT", op0)
    sub = c.gate("AND", not1, op0)                  # 01
    sel_and = c.gate("AND", op1, not0)              # 10
    sel_or = c.gate("AND", op1, op0)                # 11
    bx = [c.gate("XOR", bi, sub) for bi in b]
    sums, carries = ripple_adder(c, a, bx, sub)
    ovf = c.gate("AND", c.gate("XOR", carries[n - 2], carries[n - 1]), not1)
    out = []
    for i in range(n):
        arith = c.gate("AND", not1, sums[i])
        land = c.gate("AND", sel_and, c.gate("AND", a[i], b[i]))
        lor = c.gate("AND", sel_or, c.gate("OR", a[i], b[i]))
        out.append(c.gate("OR", c.gate("OR", arith, land), lor))
    return {"c": c, "n": n, "a": a, "b": b, "op1": op1, "op0": op0, "out": out, "overflow": ovf}


def run_alu(alu, a, b, op):
    """a, b: unsigned patterns (0 to 2^n - 1), op: 0..3. Returns (result pattern, overflow flag)."""
    n = alu["n"]
    a, b = np.broadcast_arrays(np.asarray(a), np.asarray(b))
    vals = {alu["op1"]: np.full(a.shape, op >> 1), alu["op0"]: np.full(a.shape, op & 1)}
    for i, (x, y) in enumerate(zip(bits_of(a, n), bits_of(b, n))):
        vals[alu["a"][i]], vals[alu["b"][i]] = x, y
    w = alu["c"].run(vals)
    return number_of([w[o] for o in alu["out"]]), w[alu["overflow"]]


def alu_reference(a, b, op, n):
    """Python's answer for unsigned patterns a, b: (result pattern, signed overflow flag)."""
    mask = 2 ** n - 1
    if op in (OP_ADD, OP_SUB):
        sa, sb = int(from_twos(a, n)), int(from_twos(b, n))
        true = sa + sb if op == OP_ADD else sa - sb
        return (a + b) & mask if op == OP_ADD else (a - b) & mask, int(not -(2 ** (n - 1)) <= true < 2 ** (n - 1))
    return (a & b if op == OP_AND else a | b), 0


# %% [markdown]
# ## Stretch: a seven-segment decoder
# A digit display lights segments a to g. The table below is a *truth table with 4 inputs* (the bits
# of the digit) and 7 outputs; each output could be built with the sum-of-products method.

# %%
SEGMENTS = {
    0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg",
    5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg", 9: "abcdfg",
}


def seven_segment(d):
    """Seven 0/1 outputs (a, b, c, d, e, f, g) for digit 0 to 9."""
    return [1 if s in SEGMENTS[d] else 0 for s in "abcdefg"]


# %% [markdown]
# ## Step 6: see it
# Left: the carry delay against the number of bits, read from the simulator. Right: the failure
# case, 7 + 1 in 4 bits, with the overflow flag.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    widths = np.arange(2, 17)
    delays = [carry_delay(build_adder(int(n))) for n in widths]
    for n in (4, 8, 16):
        ad = build_adder(n)
        print(f"{n:2d}-bit adder: {ad['c'].size()} gates, carry-out depth {carry_delay(ad)}, last sum depth {sum_delay(ad)}")
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.plot(widths, delays, "o-", color="#c0561b")
    ax.set_xlabel("adder width (bits)")
    ax.set_ylabel("carry-out delay (gate delays)")
    ax.set_title("Ripple-carry delay grows in step with the width")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "carry_delay.png", dpi=120)

    circ = build_add_sub(4)
    A, B = np.meshgrid(np.arange(-8, 8), np.arange(-8, 8))
    res, ovf = add_sub(circ, A.ravel(), B.ravel(), 0)
    fig2, ax2 = plt.subplots(figsize=(5.2, 4.4))
    ax2.imshow(ovf.reshape(16, 16), cmap="YlOrBr", origin="lower", extent=(-8.5, 7.5, -8.5, 7.5), vmin=0, vmax=1.4)
    ax2.set_xlabel("a (signed, 4 bits)")
    ax2.set_ylabel("b (signed, 4 bits)")
    ax2.set_title("Overflow flag for a + b (dark = overflow)")
    fig2.tight_layout()
    fig2.savefig(OUT / "overflow_map.png", dpi=120)
    r, o = add_sub(circ, 7, 1, 0)
    print(f"failure case: 7 + 1 in 4 bits gives {int(r)} with overflow flag {int(o)}")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
