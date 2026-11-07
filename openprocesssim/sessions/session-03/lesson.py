"""Session 3 (Level 3): a sequential-modular flowsheet engine with a recycle loop.

Run:  python start.py 3
Educational model only: ideal liquids, constant heat capacities, rounded textbook constants.
A learning-scale flowsheet solver in the spirit of commercial flowsheet tools; it is not
compatible with them and is not for design or safety decisions.
"""
# %% [markdown]
# # Session 3: join the boxes, close the loop
# **A. Real-world problem.** A plant feeds mostly toluene. A reactor turns part of it into benzene,
# a flash separates a benzene-rich vapour, and the unreacted toluene-rich liquid is sent back to the
# start. A loop like that cannot be solved box by box in one pass: the input of the first box
# depends on the output of the last. We solve it by guessing the returning stream (the **tear
# stream**), running the boxes in order, comparing, and repeating.
#
# Everything here repeats the Session 2 physics in a few lines so that this file runs alone.
# The reaction is a toy: toluene -> benzene, one mole for one mole, with no heat of reaction.

# %%
import itertools
import pathlib
from dataclasses import dataclass

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

ANTOINE = np.array([[6.90565, 1211.033, 220.790],     # benzene
                    [6.95464, 1344.800, 219.482],     # toluene
                    [8.20417, 1642.890, 230.300]])    # ethanol
CP = np.array([136.0, 157.0, 112.0])                  # J/(mol K), approximate
DHVAP = np.array([30800.0, 33200.0, 38600.0])         # J/mol, approximate
T_REF, P_ATM, MMHG_TO_KPA = 298.15, 101.325, 0.1333224


@dataclass
class Stream:
    n: np.ndarray
    T: float
    P: float
    phase: str = "L"

    def total(self):
        return float(np.sum(self.n))

    def enthalpy(self):
        h = CP * (self.T - T_REF) + (DHVAP if self.phase == "V" else 0.0)
        return float(np.sum(self.n * h))


def psat(T):
    return MMHG_TO_KPA * 10.0 ** (ANTOINE[:, 0] - ANTOINE[:, 1] / (ANTOINE[:, 2] + T - 273.15))


def rr_V(z, K):
    """Rachford-Rice vapour fraction by bisection (0 or 1 outside the two-phase region)."""
    f = lambda V: float(np.sum(z * (K - 1.0) / (1.0 + V * (K - 1.0))))
    if f(0.0) <= 0:
        return 0.0
    if f(1.0) >= 0:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def flash_block(feed, T, P):
    """Isothermal flash. Returns (vapour, liquid, duty W)."""
    F = feed.total()
    z = feed.n / F
    K = psat(T) / P
    V = rr_V(z, K)
    x = z / (1.0 + V * (K - 1.0))
    y = K * x
    x, y = x / x.sum(), y / y.sum()
    vap = Stream(V * F * y, T, P, "V")
    liq = Stream((1.0 - V) * F * x, T, P, "L")
    return vap, liq, vap.enthalpy() + liq.enthalpy() - feed.enthalpy()


# %% [markdown]
# ## Step 1: a flowsheet is a graph, and we count what we know
# A flowsheet is a dictionary of feed streams plus a list of blocks. Each block names its input
# and output streams and carries its settings. Before solving anything we count: every stream
# must be made by exactly one block (or be a feed with values), and every block needs all its
# settings, and no setting twice. Degrees of freedom (DOF) = settings given minus settings
# needed. DOF < 0: under-specified. DOF > 0: over-specified. The solver refuses both.

# %%
class SpecError(Exception):
    """Raised when a flowsheet is under- or over-specified, with a message saying where."""


NEEDS = {"mixer": [], "splitter": ["fraction"], "reactor": ["conversion"],
         "hx": [], "flash": ["T", "P"]}
SHAPE = {"mixer": (None, 1), "splitter": (1, 2), "reactor": (1, 1), "hx": (1, 1), "flash": (1, 2)}


def degrees_of_freedom(fs):
    """Return (dof, messages). dof = settings given - settings needed; messages list each problem."""
    msgs, dof = [], 0
    produced = {}
    for b in fs["blocks"]:
        for s in b["out"]:
            produced.setdefault(s, []).append(b["name"])
    for name, makers in produced.items():
        if len(makers) > 1:
            msgs.append(f"stream {name} is made by two blocks ({', '.join(makers)}): over-specified")
            dof += len(makers) - 1
    for name, feed in fs["feeds"].items():
        if name in produced:
            msgs.append(f"stream {name} is a fixed feed AND the output of block {produced[name][0]}: over-specified")
            dof += 1
        if feed is None:
            msgs.append(f"feed stream {name} has no values (flows, T, P): under-specified")
            dof -= 1
    consumed = {}
    for b in fs["blocks"]:
        n_in, n_out = SHAPE[b["type"]]
        if (n_in is not None and len(b["in"]) != n_in) or (n_in is None and len(b["in"]) < 2) or len(b["out"]) != n_out:
            msgs.append(f"block {b['name']} ({b['type']}) has the wrong number of streams")
            dof -= 1
        for s in b["in"]:
            consumed.setdefault(s, []).append(b["name"])
            if s not in produced and s not in fs["feeds"]:
                msgs.append(f"stream {s} enters block {b['name']} but nothing makes it: under-specified")
                dof -= 1
        for key in NEEDS[b["type"]]:
            if key not in b:
                msgs.append(f"block {b['name']} ({b['type']}) is missing its setting '{key}': under-specified")
                dof -= 1
        if b["type"] == "hx":
            modes = ("T_out" in b) + ("UA" in b)
            if modes == 0:
                msgs.append(f"block {b['name']} (hx) needs either T_out or UA with T_utility: under-specified")
                dof -= 1
            elif modes == 2:
                msgs.append(f"block {b['name']} (hx) has both T_out and UA: over-specified")
                dof += 1
            elif "UA" in b and "T_utility" not in b:
                msgs.append(f"block {b['name']} (hx) has UA but no T_utility: under-specified")
                dof -= 1
    for s, users in consumed.items():
        if len(users) > 1:
            msgs.append(f"stream {s} goes into two blocks ({', '.join(users)}); add a splitter: over-specified")
            dof += len(users) - 1
    return dof, msgs


def check_flowsheet(fs):
    dof, msgs = degrees_of_freedom(fs)
    if msgs:
        word = "UNDER" if dof < 0 else "OVER" if dof > 0 else "MIS"
        raise SpecError(f"{word}-SPECIFIED flowsheet (DOF = {dof:+d}):\n  " + "\n  ".join(msgs))


# %% [markdown]
# ## Step 2: find the order, and where to cut the loop
# If no stream loops back, sort the blocks so every block runs after the blocks that feed it
# (a topological order). If there is a loop, cut it by choosing a **tear stream** whose removal
# leaves no loop; then the rest can be sorted.

# %%
def _edges(fs, cut=()):
    made = {s: b["name"] for b in fs["blocks"] for s in b["out"]}
    return [(made[s], b["name"], s) for b in fs["blocks"] for s in b["in"] if s in made and s not in cut]


def topological_order(fs, cut=()):
    """Block names in a valid run order, or None if loops remain after removing the cut streams."""
    names = [b["name"] for b in fs["blocks"]]
    edges = _edges(fs, cut)
    indeg = {n: 0 for n in names}
    for _, v, _ in edges:
        indeg[v] += 1
    ready, order = [n for n in names if indeg[n] == 0], []
    while ready:
        u = ready.pop(0)
        order.append(u)
        for a, v, _ in edges:
            if a == u:
                indeg[v] -= 1
                if indeg[v] == 0:
                    ready.append(v)
    return order if len(order) == len(names) else None


def find_tear_streams(fs):
    """Smallest set of streams whose removal makes the flowsheet loop-free ([] if there is none)."""
    kind = {b["name"]: b["type"] for b in fs["blocks"]}
    # prefer to cut a stream that enters a mixer (the natural place where a recycle comes back)
    inner = sorted({(kind[v] != "mixer", s) for _, v, s in _edges(fs)})
    inner = [s for _, s in inner]
    for k in range(0, len(inner) + 1):
        for combo in itertools.combinations(inner, k):
            if topological_order(fs, combo) is not None:
                return list(combo)
    return inner


# %% [markdown]
# ## Step 3: the blocks
# Each block turns input streams into output streams. A block also returns its duty in W (heat
# added; negative means heat removed).

# %%
def run_block(b, ins):
    """Run one block. Returns (list of output streams, duty W, extent mol/s of reaction)."""
    t = b["type"]
    if t == "mixer":
        n = sum(s.n for s in ins)
        T = T_REF + sum(float(np.sum(s.n * CP)) * (s.T - T_REF) for s in ins) / float(np.sum(n * CP))
        return [Stream(n, T, min(s.P for s in ins))], 0.0, 0.0
    s = ins[0]
    if t == "splitter":
        f = b["fraction"]
        return [Stream(f * s.n, s.T, s.P), Stream((1.0 - f) * s.n, s.T, s.P)], 0.0, 0.0
    if t == "reactor":
        ext = b["conversion"] * s.n[b.get("key", 1)]
        n = s.n.copy()
        n[b.get("key", 1)] -= ext
        n[b.get("product", 0)] += ext
        out = Stream(n, s.T, s.P)
        return [out], out.enthalpy() - s.enthalpy(), ext
    if t == "hx":
        if "T_out" in b:
            T_out = b["T_out"]
        else:
            ntu = b["UA"] / float(np.sum(s.n * CP))
            T_out = b["T_utility"] - (b["T_utility"] - s.T) * np.exp(-ntu)
        out = Stream(s.n.copy(), T_out, s.P)
        return [out], out.enthalpy() - s.enthalpy(), 0.0
    if t == "flash":
        v, l, q = flash_block(s, b["T"], b["P"])
        return [v, l], q, 0.0
    raise SpecError(f"unknown block type {t}")


# %% [markdown]
# ## Step 4: solve with a tear stream
# Guess the tear stream, run the blocks in order, read what comes back, and compare.
# * **Successive substitution**: the new guess is simply what came back.
# * **Wegstein**: look at the last two guesses, estimate the slope s of (what came back) against
#   (what we guessed), and push the guess further: x_next = q x + (1 - q) g(x), q = s / (s - 1),
#   with q limited to between -5 and 0.

# %%
def _pack(s):
    return np.append(s.n, s.T)


def _unpack(v, P):
    return Stream(np.array(v[:3], dtype=float), float(v[3]), P)


def solve(fs, method="wegstein", tol=1e-10, maxit=200, guess=None):
    """Solve the flowsheet. Returns a result dict with 'streams', 'duties', 'extents', 'iterations',
    'history' (tear-stream change per iteration), 'converged', 'order', 'tear'."""
    check_flowsheet(fs)
    tears = find_tear_streams(fs)
    order = topological_order(fs, tears)
    blocks = {b["name"]: b for b in fs["blocks"]}
    if len(tears) > 1:
        raise SpecError("this teaching solver handles one tear stream only")

    def sweep(tear_value):
        st = dict(fs["feeds"])
        if tears:
            st[tears[0]] = tear_value
        duties, ext = {}, {}
        for name in order:
            b = blocks[name]
            outs, q, e = run_block(b, [st[s] for s in b["in"]])
            for s, o in zip(b["out"], outs):
                st[s] = o
            duties[name], ext[name] = q, e
        return st, duties, ext

    history, it, converged = [], 0, True
    if not tears:
        st, duties, ext = sweep(None)
    else:
        t = tears[0]
        P = next(s.P for s in fs["feeds"].values())
        x = _pack(guess) if guess is not None else np.append(np.zeros(3), 300.0)
        x_prev = g_prev = None
        converged = False
        for it in range(1, maxit + 1):
            st, duties, ext = sweep(_unpack(x, P))
            g = _pack(st[t])
            err = float(np.max(np.abs(g - x)))
            history.append(err)
            if err < tol:
                converged = True
                break
            if method == "wegstein" and x_prev is not None:
                dx = x - x_prev
                with np.errstate(divide="ignore", invalid="ignore"):
                    s_ = np.where(np.abs(dx) > 1e-14, (g - g_prev) / dx, 0.0)
                    q = np.where(np.abs(s_ - 1.0) > 1e-12, s_ / (s_ - 1.0), -5.0)
                q = np.clip(q, -5.0, 0.0)
                x_new = q * x + (1.0 - q) * g
            else:
                x_new = g
            x_prev, g_prev, x = x, g, x_new
    return {"streams": st, "duties": duties, "extents": ext, "iterations": it, "history": history,
            "converged": converged, "order": order, "tear": tears}


# %% [markdown]
# ## Step 5: closure reports
# A solved flowsheet must close its books. Mass: for each component, feeds in + generated by
# reaction - products out = 0. Energy: enthalpy of products - enthalpy of feeds = sum of all block duties.

# %%
def closure(fs, res):
    """Return dict: component imbalance (mol/s), total relative mass error, absolute energy error (W)."""
    st = res["streams"]
    used = {s for b in fs["blocks"] for s in b["in"]}
    made = {s for b in fs["blocks"] for s in b["out"]}
    products = [s for s in made if s not in used]
    feed_n = sum(f.n for f in fs["feeds"].values())
    gen = np.zeros(3)
    for b in fs["blocks"]:
        if b["type"] == "reactor":
            gen[b.get("key", 1)] -= res["extents"][b["name"]]
            gen[b.get("product", 0)] += res["extents"][b["name"]]
    out_n = sum(st[s].n for s in products)
    comp_err = feed_n + gen - out_n
    h_in = sum(f.enthalpy() for f in fs["feeds"].values())
    h_out = sum(st[s].enthalpy() for s in products)
    e_err = h_out - h_in - sum(res["duties"].values())
    return {"component_error": comp_err, "mass_error": float(np.max(np.abs(comp_err)) / feed_n.sum()),
            "energy_error": float(e_err), "products": products}


# %% [markdown]
# ## Step 6: the mini-project flowsheet
# Feed F (mostly toluene) + recycle R -> mixer M -> reactor RX -> heat exchanger HX -> flash FL.
# Vapour V is the benzene-rich product; the liquid goes to a splitter SP: a fraction goes back
# as the recycle R, the rest leaves as bottoms B.

# %%
def loop_flowsheet(r=0.9, T_flash=368.0, conversion=0.30, feed=(5.0, 95.0, 0.0), T_hx=355.0):
    return {
        "feeds": {"F": Stream(np.array(feed, dtype=float), 320.0, P_ATM)},
        "blocks": [
            {"name": "M", "type": "mixer", "in": ["F", "R"], "out": ["S1"]},
            {"name": "RX", "type": "reactor", "in": ["S1"], "out": ["S2"], "conversion": conversion},
            {"name": "HX", "type": "hx", "in": ["S2"], "out": ["S3"], "T_out": T_hx},
            {"name": "FL", "type": "flash", "in": ["S3"], "out": ["V", "L"], "T": T_flash, "P": P_ATM},
            {"name": "SP", "type": "splitter", "in": ["L"], "out": ["R", "B"], "fraction": r},
        ],
    }


def convergence_message(res, tol=1e-10):
    """One honest sentence about how a solve ended."""
    if res["converged"]:
        return f"converged in {res['iterations']} iterations (change {res['history'][-1]:.1e} < {tol:.0e})"
    return (f"NOT converged after {res['iterations']} iterations: the tear stream still changes by "
            f"{res['history'][-1]:.3g} per iteration. Check that the specification is feasible.")


def purity(res, stream="V"):
    n = res["streams"][stream].n
    return float(n[0] / n.sum()) if n.sum() > 0 else float("nan")


# %% [markdown]
# ## Step 7: where Raoult's law fails
# Ethanol and benzene form a minimum-boiling azeotrope: the real mixture of about 45 mole percent
# ethanol boils near 341 K at 1 atm (approximate literature value), lower than either pure liquid.
# Raoult's law can only give a boiling point between the pure ones, so it cannot show this.

# %%
REAL_AZEOTROPE_T = 341.0          # K, approximate, ethanol-benzene at 1 atm
REAL_AZEOTROPE_X_ETHANOL = 0.45   # approximate


def raoult_bubble_T(x_ethanol, P=P_ATM):
    """Ideal bubble temperature (K) of an ethanol-benzene liquid, bisection on sum x P_sat = P."""
    x = np.array([1.0 - x_ethanol, 0.0, x_ethanol])
    lo, hi = 300.0, 420.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if float(np.sum(x * psat(mid))) < P:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fs = loop_flowsheet()
    ss = solve(fs, "substitution")
    wg = solve(fs, "wegstein")
    cl = closure(fs, wg)
    print("order:", wg["order"], "tear:", wg["tear"])
    print(f"substitution: {ss['iterations']} iterations, Wegstein: {wg['iterations']} iterations")
    print(f"product purity (benzene in V): {purity(wg):.4f}, V = {wg['streams']['V'].total():.2f} mol/s")
    print(f"recycle flow: {wg['streams']['R'].total():.2f} mol/s, closure {cl['mass_error']:.1e}")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.semilogy(range(1, len(ss["history"]) + 1), ss["history"], "o-", ms=3, label="successive substitution")
    ax.semilogy(range(1, len(wg["history"]) + 1), wg["history"], "s-", ms=3, label="Wegstein")
    ax.set_xlabel("iteration")
    ax.set_ylabel("change in tear stream (largest entry)")
    ax.set_title("Recycle loop convergence")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "convergence.png", dpi=120)

    Ts = np.linspace(364.0, 378.0, 29)
    pur = [purity(solve(loop_flowsheet(T_flash=T), "wegstein")) for T in Ts]
    vap = [solve(loop_flowsheet(T_flash=T), "wegstein")["streams"]["V"].total() for T in Ts]
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(Ts, pur, "b", label="benzene purity of the vapour product")
    ax2.set_xlabel("flash temperature T (K)")
    ax2.set_ylabel("purity (mole fraction)")
    ax3 = ax2.twinx()
    ax3.plot(Ts, vap, "r--", label="product flow (mol/s)")
    ax3.set_ylabel("vapour product flow (mol/s)")
    ax2.set_title("Sensitivity to the flash temperature (r = 0.9)")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "sensitivity.png", dpi=120)

    xs = np.linspace(0, 1, 101)
    fig3, ax4 = plt.subplots(figsize=(6.4, 4.2))
    ax4.plot(xs, [raoult_bubble_T(x) for x in xs], label="Raoult's law (ideal)")
    ax4.plot([REAL_AZEOTROPE_X_ETHANOL], [REAL_AZEOTROPE_T], "r*", ms=12, label="real azeotrope (approx.)")
    ax4.set_xlabel("ethanol mole fraction in the liquid")
    ax4.set_ylabel("bubble temperature (K)")
    ax4.set_title("Ethanol-benzene at 1 atm: the honest limit")
    ax4.legend(fontsize=8)
    ax4.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "azeotrope.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Ideal thermodynamics, one tear stream, no heat of reaction, no pressure drops, no column.
# The roadmap lists what comes next.
