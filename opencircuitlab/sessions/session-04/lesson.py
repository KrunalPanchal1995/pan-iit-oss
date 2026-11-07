"""Session 4 (Level 3): read a circuit from a text netlist, and catch the mistakes people make in one.

Run:  python start.py 4
Low-voltage educational circuits only (never mains). Ideal sources, linear resistors.
"""
# %% [markdown]
# # Session 4: read a netlist
# **A. Real-world problem.** So far every circuit was a Python list of tuples. Real circuit
# simulators (SPICE and its descendants) read a *netlist*: a text file with one line per part,
# such as `R1 2 1 1k` ("resistor named R1 between nodes 2 and 1, 1 kilo-ohm"). Text is easy to
# write, to share and to keep in a project, and also easy to get wrong: one letter changes
# `1k` to `1m` and the resistor is a thousand million times smaller. Today we write the reader,
# check it against the Session 3 solver, and then write a checker that finds the mistakes in a
# technician's file.
#
# **Plan.** (1) read a value with a scale suffix, (2) read a line, (3) read a whole file and
# solve it, (4) write a circuit back as text and check the round trip, (5) report every problem in
# a netlist, not only the first.

# %%
import math
import pathlib
import re

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 0: the solver from Session 3
# Unchanged: `solve_network(n_nodes, resistors, vsources, isources)` takes Python lists. Our job is
# to build those lists from text.

# %%
def solve_network(n_nodes, resistors, vsources=(), isources=()):
    """Solve a resistor network. Nodes are 0 (ground) to n_nodes.

    resistors: (a, b, ohm). vsources: (plus, minus, volts). isources: (a, b, amperes): the
    source pushes that current from node a, through itself, into node b.
    Returns (v, j): node voltages v[0..n_nodes] (v[0] = 0) and the current j[k] that each
    voltage source delivers (positive = the source is supplying power).
    Raises ValueError for a floating node or contradictory sources (singular matrix).
    """
    n, m = n_nodes, len(vsources)
    size = n + m
    a = np.zeros((size, size))
    rhs = np.zeros(size)
    for na, nb, r in resistors:
        if r <= 0:
            raise ValueError("resistance must be positive (a 0 ohm wire is a short circuit)")
        g = 1.0 / r
        for p, q, s in ((na, na, g), (nb, nb, g), (na, nb, -g), (nb, na, -g)):
            if p > 0 and q > 0:
                a[p - 1, q - 1] += s
    for na, nb, cur in isources:
        if na > 0:
            rhs[na - 1] -= cur
        if nb > 0:
            rhs[nb - 1] += cur
    for k, (p, q, volts) in enumerate(vsources):
        if p > 0:
            a[p - 1, n + k] -= 1.0
            a[n + k, p - 1] += 1.0
        if q > 0:
            a[q - 1, n + k] += 1.0
            a[n + k, q - 1] -= 1.0
        rhs[n + k] = volts
    if size == 0:
        return np.zeros(1), np.zeros(0)
    if np.linalg.cond(a) > 1e12:
        raise ValueError("singular matrix: a node is floating (no path to ground) or sources contradict each other")
    x = np.linalg.solve(a, rhs)
    return np.concatenate(([0.0], x[:n])), x[n:]


# the Session 2 two-loop circuit in list form, to compare against the text form
TWO_LOOP = dict(n_nodes=3,
                resistors=[(2, 1, 100.0), (3, 1, 200.0), (1, 0, 300.0)],
                vsources=[(2, 0, 10.0), (3, 0, 4.0)])

TWO_LOOP_TEXT = """\
* the Session 2 two-loop circuit: node A is the junction of the three resistors
V1 top1 0 10
V2 top2 0 4
R1 top1 A 100
R2 top2 A 200
R3 A 0 300
"""


# %% [markdown]
# ## Step 1: reading a value
# Netlists write `1k`, `4.7k`, `2.2meg`, `100m`. The rules (from SPICE) are:
#
#     t = 1e12   g = 1e9   meg = 1e6   k = 1e3   m = 1e-3   u = 1e-6   n = 1e-9   p = 1e-12   f = 1e-15
#
# * the letters are **not** case sensitive, so `1K` is 1000 and `1MEG` is a million;
# * **`m` means milli, also when written `M`**: `1M` is 0.001, not a million. For a million write `meg`;
# * letters after the scale are a unit and are ignored: `5V`, `2mA`, `1kohm`;
# * a plain number may use an exponent: `2.2e3`.
# One more trap: `1F` is one **femto**, because `f` is a scale letter.

# %%
SCALE_EXP = {"t": 12, "g": 9, "meg": 6, "k": 3, "m": -3, "u": -6, "n": -9, "p": -12, "f": -15}
_VALUE = re.compile(r"^([+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)([a-z]*)$", re.IGNORECASE)


class NetlistError(ValueError):
    """A problem in a netlist; the message starts with the line number when there is one."""


def parse_value(text):
    """Value of a netlist number such as '1k', '4.7K', '2.2meg', '100m', '12', '5V' or '1e3'."""
    m = _VALUE.match(text.strip())
    if not m:
        raise NetlistError(f"cannot read the value '{text}'")
    number, letters = m.group(1), m.group(2).lower()
    exp = 0
    if letters.startswith("meg"):
        exp = SCALE_EXP["meg"]
    elif letters and letters[0] in SCALE_EXP:
        exp = SCALE_EXP[letters[0]]
    return float(number) * 10.0 ** exp if "e" in number.lower() else float(f"{number}e{exp}")


_FORMAT = [(1e12, "t"), (1e9, "g"), (1e6, "meg"), (1e3, "k"), (1.0, ""), (1e-3, "m"), (1e-6, "u"), (1e-9, "n"), (1e-12, "p"), (1e-15, "f")]


def format_value(x):
    """The shortest netlist text for x: 4700 -> '4.7k', 0.001 -> '1m', 1e6 -> 'meg'-form '1meg'."""
    if x == 0:
        return "0"
    sign = "-" if x < 0 else ""
    ax = abs(x)
    for scale, letters in _FORMAT:
        if ax >= scale * (1 - 1e-12):
            return f"{sign}{ax / scale:.12g}{letters}"
    return f"{sign}{ax / 1e-15:.12g}f"


# %% [markdown]
# ## Step 2: reading a file
# One line per part: `name node node value`. The first letter of the name says what it is: `R`
# resistor, `V` voltage source (the first node is the plus side), `I` current source (it pushes its
# current from the first node, through itself, into the second). Sources may have `DC` before the
# value. A line that starts with `*` is a comment, `;` starts a comment at the end of a line, blank
# lines are skipped, and `.end` stops the reading. Node `0` (or `gnd`) is the ground; other node
# names can be words, and get the numbers 1, 2, 3... in the order they first appear. Names are not
# case sensitive. The reader refuses what it cannot understand, with the line number.

# %%
GROUND = {"0", "gnd"}


def _strip(line):
    return line.split(";", 1)[0].strip()


def parse_netlist(text):
    """Read a netlist. Returns a dict with n_nodes, resistors, vsources, isources (as the solver wants them),
    nodes (name -> number) and names (element names in the order of each list)."""
    nodes = {"0": 0}
    seen, names = set(), {"R": [], "V": [], "I": []}
    out = {"resistors": [], "vsources": [], "isources": []}
    lists = {"R": out["resistors"], "V": out["vsources"], "I": out["isources"]}

    def node(name):
        name = name.lower()
        if name in GROUND:
            return 0
        if name not in nodes:
            nodes[name] = len(nodes)
        return nodes[name]

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = _strip(raw)
        if not line or line.startswith("*"):
            continue
        if line.lower() == ".end":
            break
        if line.startswith("."):
            raise NetlistError(f"line {lineno}: the command '{line.split()[0]}' is not supported")
        tok = line.split()
        name, kind = tok[0], tok[0][0].upper()
        if kind not in lists:
            raise NetlistError(f"line {lineno}: unknown part '{name}' (this reader knows R, V and I)")
        if kind != "R" and len(tok) == 5 and tok[3].lower() == "dc":
            tok = tok[:3] + tok[4:]
        if len(tok) != 4:
            raise NetlistError(f"line {lineno}: '{name}' needs a name, two nodes and a value (found {len(tok) - 1} fields after the name)")
        if name.lower() in seen:
            raise NetlistError(f"line {lineno}: the name '{name}' is already used")
        try:
            value = parse_value(tok[3])
        except NetlistError as e:
            raise NetlistError(f"line {lineno}: {e}") from None
        a, b = node(tok[1]), node(tok[2])
        if a == b:
            raise NetlistError(f"line {lineno}: both ends of '{name}' are on the same node")
        if kind == "R" and value <= 0:
            raise NetlistError(f"line {lineno}: the resistance of '{name}' must be positive")
        seen.add(name.lower())
        lists[kind].append((a, b, value))
        names[kind].append(name.lower())
    if len(nodes) == 1 and not any(lists.values()):
        raise NetlistError("the netlist is empty")
    if not any(0 in (a, b) for a, b, _ in out["resistors"] + out["vsources"] + out["isources"]):
        raise NetlistError("no part touches the ground node: use node 0 (or gnd) as the reference")
    out.update(n_nodes=len(nodes) - 1, nodes=nodes, names=names)
    return out


def solve_netlist(text):
    """Parse and solve. Returns (node voltages by node name, voltage source currents by source name)."""
    net = parse_netlist(text)
    v, j = solve_network(net["n_nodes"], net["resistors"], net["vsources"], net["isources"])
    volts = {name: float(v[k]) for name, k in net["nodes"].items()}
    amps = {name: float(j[k]) for k, name in enumerate(net["names"]["V"])}
    return volts, amps


# %% [markdown]
# ## Step 3: writing a circuit as text, and the round trip
# The opposite function turns lists into a netlist. A good reader and writer pair satisfies
# `parse(write(circuit)) = circuit`; we test that on random networks in the checkpoint.

# %%
def to_netlist(n_nodes, resistors, vsources=(), isources=()):
    """Netlist text for a network given as lists (nodes are called 1, 2, 3... and 0)."""
    lines = []
    for k, (a, b, r) in enumerate(resistors, 1):
        lines.append(f"R{k} {a} {b} {format_value(r)}")
    for k, (p, q, v) in enumerate(vsources, 1):
        lines.append(f"V{k} {p} {q} {format_value(v)}")
    for k, (a, b, i) in enumerate(isources, 1):
        lines.append(f"I{k} {a} {b} {format_value(i)}")
    return "\n".join(lines) + "\n"


# %% [markdown]
# ## Step 4: report every problem, not only the first
# `parse_netlist` stops at the first error, which is right for a program but tiring for a person
# with ten mistakes. `check_netlist` reads the whole file and lists everything it finds:
# * **errors** (the file cannot be solved): unreadable lines, repeated names, a part with both ends
#   on one node, no ground, and **floating nodes** (a group of nodes with no path to ground);
# * **warnings** (the file can be solved but is probably not what you meant): a resistor below
#   0.1 ohm (`1M` is a milliohm: did you mean `1meg`?) or above 100 megohm.

# %%
def check_netlist(text):
    """List of (line number, 'error' or 'warning', message) for everything suspicious; never raises."""
    problems, seen, edges, first_line, has_ground = [], set(), [], {}, False
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = _strip(raw)
        if not line or line.startswith("*"):
            continue
        if line.lower() == ".end":
            break
        tok = line.split()
        name, kind = tok[0], tok[0][0].upper()
        if line.startswith("."):
            problems.append((lineno, "error", f"the command '{tok[0]}' is not supported"))
            continue
        if kind not in "RVI":
            problems.append((lineno, "error", f"unknown part '{name}'"))
            continue
        if kind != "R" and len(tok) == 5 and tok[3].lower() == "dc":
            tok = tok[:3] + tok[4:]
        if len(tok) != 4:
            problems.append((lineno, "error", f"'{name}' needs a name, two nodes and a value"))
            continue
        bad = False
        if name.lower() in seen:
            problems.append((lineno, "error", f"the name '{name}' is already used"))
            bad = True
        seen.add(name.lower())
        try:
            value = parse_value(tok[3])
        except NetlistError as e:
            problems.append((lineno, "error", str(e)))
            continue
        a, b = ("0" if t.lower() in GROUND else t.lower() for t in tok[1:3])
        if a == b:
            problems.append((lineno, "error", f"both ends of '{name}' are on the same node"))
            bad = True
        if kind == "R":
            if value <= 0:
                problems.append((lineno, "error", f"the resistance of '{name}' must be positive"))
                bad = True
            elif value < 0.1:
                problems.append((lineno, "warning", f"'{name}' is only {format_value(value)} ohm (note: M means milli; for mega write meg)"))
            elif value > 1e8:
                problems.append((lineno, "warning", f"'{name}' is {format_value(value)} ohm, practically an open circuit"))
        if not bad:
            edges.append((a, b))
            first_line.setdefault(a, lineno)
            first_line.setdefault(b, lineno)
        has_ground = has_ground or a == "0" or b == "0"
    if edges and not has_ground:
        problems.append((1, "error", "no part touches the ground node: use node 0 (or gnd)"))
    # floating groups: nodes that cannot reach ground through any part
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        parent[find(a)] = find(b)
    ground = find("0") if "0" in parent else None
    groups = {}
    for n in parent:
        if find(n) != ground:
            groups.setdefault(find(n), []).append(n)
    for g in groups.values():
        problems.append((min(first_line[n] for n in g), "error", "nodes " + ", ".join(sorted(g)) + " have no path to ground (floating)"))
    return sorted(problems, key=lambda p: (p[0], p[1]))


# %% [markdown]
# ## Step 5: mini-project tools (a technician's bridge file)
# A technician sends the netlist of the Pt1000 bridge of Session 3 at 100 degrees (1.385 kohm)
# with a meter resistor, and says "it does not work". It has three mistakes.

# %%
TECH_NETLIST = """\
* Pt1000 bridge at 100 C, 5 V supply (technician's file)
V1 top 0 5
R1 top a 1k
R2 top b 1k
R3 a 0 1.385k
R4 b 0 1M
R2 a b 10k
R5 c d 2.2k
"""


def bridge_formula(vs, r1, r2, r3, r4):
    return vs * (r3 / (r1 + r3) - r4 / (r2 + r4))


def corrected_bridge(meter=None):
    """The technician's bridge with the three mistakes repaired; optionally with a meter resistor between a and b."""
    text = TECH_NETLIST.replace("R4 b 0 1M", "R4 b 0 1k").replace("R2 a b 10k\n", "").replace("R5 c d 2.2k\n", "")
    if meter is not None:
        text += f"Rm a b {format_value(meter)}\n"
    return text


def bridge_output(meter=None):
    """V(a) - V(b) of the corrected technician bridge, read from text and solved; meter in ohm (None = no meter)."""
    v, _ = solve_netlist(corrected_bridge(meter))
    return v["a"] - v["b"]


def loading_error(meter):
    """Fraction of the unloaded bridge output that a meter of this resistance takes away."""
    return 1.0 - bridge_output(meter) / bridge_output(None)


METERS = [m * 10 ** k for k in range(3, 8) for m in (1, 2, 5)] + [1e8]   # 1k, 2k, 5k, 10k ... 100meg


def smallest_meter(max_error, candidates=METERS):
    """First meter resistance in the list whose loading error is at most max_error, or None."""
    for m in candidates:
        if loading_error(m) <= max_error:
            return m
    return None


# %% [markdown]
# ## See it
# Figure 1: how the same digits are read with different suffixes. Figure 2: what a one-letter typo
# does to the node voltage of the two-loop circuit. Figure 3: the bridge read from text against the
# closed formula over the whole temperature range.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA, GREY = "#0072b2", "#c86a00", "#d81b60", "#555555"
    v, j = solve_network(**TWO_LOOP)
    volts, amps = solve_netlist(TWO_LOOP_TEXT)
    print("two-loop from lists: V_A =", round(v[1], 4), "  from text: V(A) =", round(volts["a"], 4), " source currents (mA):", {k: round(1000 * x, 3) for k, x in amps.items()})
    for s in ("1k", "4.7K", "2.2meg", "2.2MEG", "1M", "100m", "5V", "2mA", "1kohm", "2.2e3", "1F"):
        print(f"  parse_value({s!r:9}) = {parse_value(s):g}")
    print("technician's file:")
    for p in check_netlist(TECH_NETLIST):
        print("   line %d %s: %s" % p)
    for meter in (None, 10000.0):
        vv, _ = solve_netlist(corrected_bridge(meter))
        print(f"   repaired bridge{'' if meter is None else ' with a 10 kohm meter'}: V(a) - V(b) = {1000 * (vv['a'] - vv['b']):.2f} mV (formula without meter: {1000 * bridge_formula(5, 1000, 1000, 1385, 1000):.2f} mV)")
    for m in (1e3, 1e4, 1e5, 1e6):
        print(f"   meter {format_value(m):>5} ohm: reads {1000 * bridge_output(m):7.2f} mV, loading error {100 * loading_error(m):5.2f} %")
    print("   smallest meter from the 1-2-5 list for a loading error of at most 1 %:", format_value(smallest_meter(0.01)), "ohm")
    print("   as typed (R4 = 1M = 1 milliohm, no repairs except the name and the floating part):")
    typed = TECH_NETLIST.replace("R2 a b 10k\n", "").replace("R5 c d 2.2k\n", "")
    vt, _ = solve_netlist(typed)
    print(f"      V(b) = {vt['b']:.4f} V (should be 2.5 V), V(a) - V(b) = {1000 * (vt['a'] - vt['b']):.1f} mV")

    # Figure 1: the same digits with different suffixes
    labels = ["1m", "1M", "1k", "1K", "1meg", "1MEG", "1u"]
    vals = [parse_value(s) for s in labels]
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    cols = [MAGENTA if s in ("1m", "1M") else BLUE if s.lower() in ("1k", "1meg") else GREY for s in labels]
    ax1.bar(range(len(labels)), vals, color=cols)
    ax1.set_yscale("log")
    ax1.set_xticks(range(len(labels)))
    ax1.set_xticklabels(labels)
    ax1.set_xlabel("how the value is typed")
    ax1.set_ylabel("value read (ohm)")
    ax1.set_title("1M is a milliohm, 1meg a megohm; upper and lower case agree")
    ax1.grid(alpha=0.3, which="major", axis="y")
    fig1.tight_layout()
    fig1.savefig(OUT / "value_suffixes.png", dpi=120)

    # Figure 2: V_A against the typed value of R3
    r3 = np.logspace(-1, 6.5, 200)
    va = [solve_network(3, [(2, 1, 100.0), (3, 1, 200.0), (1, 0, x)], [(2, 0, 10.0), (3, 0, 4.0)])[0][1] for x in r3]
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.semilogx(r3, va, color=BLUE, lw=2)
    typed_pts = [("300m", 0.3), ("300", 300.0), ("300k", 3e5), ("300meg", 3e8)]
    for s, rv in typed_pts:
        vt_ = solve_netlist(TWO_LOOP_TEXT.replace("R3 A 0 300", f"R3 A 0 {s}"))[0]["a"]
        ax2.plot([rv], [vt_], "o", color=MAGENTA if s != "300" else ORANGE, ms=8)
        ax2.annotate(f"R3 {s}: {vt_:.3f} V", (rv, vt_), textcoords="offset points", xytext=(6, 8 if s != "300meg" else -16), fontsize=8)
        print(f"  R3 typed {s:7}: V(A) = {vt_:.4f} V")
    ax2.set_xlabel("value of R3 (ohm)")
    ax2.set_ylabel("node voltage V(A) (V)")
    ax2.set_title("One letter in the file moves V(A) from 6.55 V to almost 0 V")
    ax2.grid(alpha=0.3, which="major")
    fig2.tight_layout()
    fig2.savefig(OUT / "typo_effect.png", dpi=120)

    # Figure 3: bridge from text against formula
    temps = np.linspace(0, 100, 101)
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.plot(temps, [1000 * bridge_formula(5, 1000, 1000, 1000 * (1 + 0.00385 * t), 1000) for t in temps], color=BLUE, lw=2, label="closed formula")
    pts = temps[::10]
    from_text = []
    for t in pts:
        net = f"V1 top 0 5\nR1 top a 1k\nR2 top b 1k\nR3 a 0 {format_value(1000 * (1 + 0.00385 * t))}\nR4 b 0 1k\n"
        vv, _ = solve_netlist(net)
        from_text.append(1000 * (vv["a"] - vv["b"]))
    ax3.plot(pts, from_text, "o", color=ORANGE, label="read from text and solved")
    ax3.set_xlabel("temperature (degrees C)")
    ax3.set_ylabel("bridge output V(a) - V(b) (mV)")
    ax3.set_title("The netlist route agrees with the formula")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "bridge_from_text.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
