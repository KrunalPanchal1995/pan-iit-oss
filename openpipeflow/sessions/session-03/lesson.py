"""Session 3 (Level 3): a small looped water network solved with Hardy Cross, and checked.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a small town network, solved and validated
# **A. Real-world problem.** A town is fed from a hill tank. Pipes branch and close into a
# loop, and every street takes some water. Nobody can read the flow in each pipe off a
# formula. We solve it numerically, then *prove to ourselves* the answer is right: a network
# with one pipe must agree with Session 2, water must be conserved at every node, and the
# head losses around the loop must cancel.
#
# **Plan.** (1) one-pipe head loss (from Session 2), (2) the network, (3) Hardy Cross loop
# correction, (4) pressures, (5) validation, (6) sensitivity to roughness and viscosity,
# (7) a failure case. Educational model, not a hydraulic design tool.

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

RHO, G, NU = 998.0, 9.81, 1.0e-6    # water at 20 C


# %% [markdown]
# ## Step 1: head loss of one pipe (Session 2, in the form the solver needs)
# `loss(q, ...)` is the *signed* head loss: the sign follows the flow direction, so a
# negative flow in a pipe gives a negative loss.

# %%
def friction_factor(re, rel_rough):
    def turbulent(r):
        return 0.25 / math.log10(rel_rough / 3.7 + 5.74 / r ** 0.9) ** 2
    if re < 2000.0:
        return 64.0 / re
    if re > 4000.0:
        return turbulent(re)
    w = (re - 2000.0) / 2000.0
    return (1 - w) * 0.032 + w * turbulent(4000.0)


def head_loss(q, d, length, rough, nu=NU):
    """Head loss (m) for a non-negative flow q (m^3/s)."""
    if q <= 0.0:
        return 0.0
    v = 4.0 * q / (math.pi * d ** 2)
    f = friction_factor(v * d / nu, rough / d)
    return f * length / d * v ** 2 / (2 * G)


def loss(q, pipe, rough, nu=NU):
    """Signed head loss of a pipe dict {'L', 'D'} for a flow q that may be negative."""
    return math.copysign(head_loss(abs(q), pipe["D"], pipe["L"], rough, nu), q)


# %% [markdown]
# ## Step 2: the network
# ```
#   tank T ---1---> A ---2---> B
#                   |          |
#                   3          4
#                   v          v
#                   C <--------+      (pipe 4 joins B and C: a loop A-B-C)
# ```
# Node heights z, tank water level H_T, demands taken out at B and C. Flows are in m^3/s.
# We call the unknown flow in pipe 4 (B to C) `x`. Continuity at every node then fixes
# the other three flows: Q1 = Qb + Qc, Q2 = Qb + x, Q3 = Qc - x.

# %%
Z = {"T": 70.0, "A": 20.0, "B": 15.0, "C": 25.0}   # T: tank water level; others: street levels, m
LENGTHS = {1: 1200.0, 2: 600.0, 3: 800.0, 4: 500.0}  # m


def make_network(d_main=0.20, d_branch=0.125):
    """Pipe data for the 4-pipe network (diameters in m)."""
    return {1: {"L": LENGTHS[1], "D": d_main}, 2: {"L": LENGTHS[2], "D": d_branch},
            3: {"L": LENGTHS[3], "D": d_branch}, 4: {"L": LENGTHS[4], "D": d_branch}}


def flows_from_x(x, qb, qc):
    return {1: qb + qc, 2: qb + x, 3: qc - x, 4: x}


# %% [markdown]
# ## Step 3: Hardy Cross
# Going round the loop A -> B -> C -> A the head losses must add to zero (you cannot gain
# energy by walking in a circle):  F(x) = h2 + h4 - h3 = 0. Guess x, see how wrong F is, and
# correct x by  dx = -F / F'  where F' = dh2/dQ + dh4/dQ + dh3/dQ  (found numerically).
# This is Newton's method on one unknown, and it converges in a few steps.

# %%
def hardy_cross(pipes, qb, qc, rough, nu=NU, tol=1e-12, max_iter=50):
    """Return (x, iterations): the flow in pipe 4 (B to C) that balances the loop."""
    x = 0.0
    for it in range(1, max_iter + 1):
        q = flows_from_x(x, qb, qc)
        f_val = loss(q[2], pipes[2], rough, nu) + loss(q[4], pipes[4], rough, nu) - loss(q[3], pipes[3], rough, nu)
        dq = 1e-7
        slope = 0.0
        for pid in (2, 3, 4):
            slope += (loss(q[pid] + dq, pipes[pid], rough, nu) - loss(q[pid] - dq, pipes[pid], rough, nu)) / (2 * dq)
        step = -f_val / slope
        x += step
        if abs(step) < tol:
            return x, it
    return x, max_iter


def solve(d_main=0.20, d_branch=0.125, total_lps=30.0, share_b=0.6, rough=0.00015, nu=NU):
    """Solve the network. Returns a dict with flows (m^3/s), heads (m), pressure heads (m)."""
    pipes = make_network(d_main, d_branch)
    qtot = total_lps / 1000.0
    qb, qc = share_b * qtot, (1 - share_b) * qtot
    x, iters = hardy_cross(pipes, qb, qc, rough, nu)
    q = flows_from_x(x, qb, qc)
    h = {i: loss(q[i], pipes[i], rough, nu) for i in q}
    head = {"T": Z["T"]}
    head["A"] = head["T"] - h[1]
    head["B"] = head["A"] - h[2]
    head["C"] = head["A"] - h[3]
    pres = {n: head[n] - Z[n] for n in ("A", "B", "C")}
    return {"Q": q, "h": h, "head": head, "pressure_head": pres, "iterations": iters,
            "demand": {"B": qb, "C": qc}, "pipes": pipes}


# %% [markdown]
# ## Step 4: pressure
# Pressure head (m of water) at a node = hydraulic head minus street level. Pressure in
# kilopascals is rho g times that, so 1 m of head is 9.79 kPa. In this simplified picture we
# ask for at least 20 m (about 196 kPa) at every node.

# %%
def min_pressure_head(**kw):
    return min(solve(**kw)["pressure_head"].values())


def node_balance(sol):
    """Net flow (m^3/s) into each node minus its demand; should be zero everywhere."""
    q, d = sol["Q"], sol["demand"]
    return {"A": q[1] - q[2] - q[3], "B": q[2] - q[4] - d["B"], "C": q[3] + q[4] - d["C"]}


def loop_closure(sol):
    """Sum of head losses around the loop A-B-C-A (m); should be zero."""
    h = sol["h"]
    return h[2] + h[4] - h[3]


# %% [markdown]
# ## Step 5: validation and Step 6: sensitivity
# * Single pipe: one pipe through the network way must give the Session 2 head loss.
# * Conservation: node balance and loop closure are zero to rounding.
# * Symmetry: if B and C are treated identically, pipe 4 carries nothing.
# * Sensitivity: change one input at a time and see how the worst pressure moves.

# %%
def single_pipe_check(q=0.030, d=0.20, length=1200.0, rough=0.00015):
    """Head drop for one tank-to-node pipe: the network way versus the Session 2 formula."""
    network_way = loss(q, {"L": length, "D": d}, rough)
    v = 4 * q / (math.pi * d ** 2)
    re = v * d / NU
    direct = friction_factor(re, rough / d) * length / d * v ** 2 / (2 * G)
    return network_way, direct


def sensitivity(base=None):
    """Worst pressure head (m) for roughness x2, and for colder and warmer water."""
    base = base or {}
    out = {"base": min_pressure_head(**base)}
    out["rough x2"] = min_pressure_head(**{**base, "rough": 2 * base.get("rough", 0.00015)})
    out["cold water (nu 1.31e-6)"] = min_pressure_head(**{**base, "nu": 1.31e-6})
    out["warm water (nu 0.66e-6)"] = min_pressure_head(**{**base, "nu": 0.66e-6})
    return out


# %% [markdown]
# ## Step 7: a failure case and the mini-project tool
# Pull too much water and the worst node loses pressure (below zero it would suck air in;
# the model does not warn about that, you must). `pipe_run_power` is the single-pipe pump
# power from Session 2, used by the mini-project.

# %%
def pipe_run_power(q, d, length, rough, lift, k_minor=0.0, eta=0.65, nu=NU):
    """Electric power (W) to pump q (m^3/s) through one pipe run with a static lift (m)."""
    v = 4 * q / (math.pi * d ** 2)
    f = friction_factor(v * d / nu, rough / d)
    h = lift + (f * length / d + k_minor) * v ** 2 / (2 * G)
    return RHO * G * q * h / eta


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    s = solve()
    print("iterations:", s["iterations"])
    print("flows (L/s):", {k: round(1000 * v, 2) for k, v in s["Q"].items()})
    print("head loss (m):", {k: round(v, 2) for k, v in s["h"].items()})
    print("pressure head (m):", {k: round(v, 2) for k, v in s["pressure_head"].items()})
    print("node balance:", node_balance(s), " loop closure:", loop_closure(s))
    print("single pipe:", single_pipe_check())
    print("sensitivity (worst pressure head, m):", {k: round(v, 2) for k, v in sensitivity().items()})

    tot = np.linspace(5, 90, 60)
    worst = [min_pressure_head(total_lps=t) for t in tot]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(tot, worst)
    ax.axhline(20, color="tab:red", ls="--", label="20 m target")
    ax.axhline(0, color="gray", ls=":")
    ax.set_xlabel("total town demand (L/s)")
    ax.set_ylabel("worst node pressure head (m)")
    ax.set_title("Pressure sags as the town draws more water")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "pressure_vs_demand.png", dpi=120)

    rr = np.linspace(0.01, 1.0, 50)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(rr, [min_pressure_head(rough=r / 1000) for r in rr])
    ax2.set_xlabel("pipe wall roughness (mm)")
    ax2.set_ylabel("worst node pressure head (m)")
    ax2.set_title("Old, rough pipes cost pressure (30 L/s)")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "pressure_vs_roughness.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
