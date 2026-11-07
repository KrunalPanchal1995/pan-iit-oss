"""Session 1 (Level 1): a plant is boxes joined by pipes; solve all the box rules together.

Run:  python start.py 1
Educational model only: one number per pipe (a total molar flow), no chemistry yet.
"""
# %% [markdown]
# # Session 1: boxes, pipes and a loop
# **A. Real-world problem.** In a chemical plant a stream of liquid goes into a separator, and
# the part that is not good enough is sent back to the start to try again. Every box obeys a
# simple rule ("what goes in comes out"), but because of the loop the flow into the first box
# depends on the flow out of the last. How much liquid really flows through the separator?
# Commercial flowsheet programs answer this for plants with hundreds of boxes; today you
# do it for two, in the spirit of those tools but at learning scale.
#
# Words: a **stream** is a pipe with a flow (mol/s). A **box** has inlets, outlets and a **rule**.
# The **recycle** is the stream that goes back to the start.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: write each box as one equation
# Streams: F = fresh feed (known), S = flow into the separator, P = product, R = recycle.
# * Mixer box (joins F and R):          S = F + R           ->  S - R = F
# * Separator box, rule 1 (recycle):    R = r * S           ->  R - r S = 0
# * Separator box, rule 2 (product):    P = (1 - r) * S     ->  P - (1 - r) S = 0
# r is the **recycle fraction** (0 to 1). Three unknowns (S, P, R), three equations: solvable.

# %%
def plant_equations(F, r):
    """Matrix A and right-hand side b of A @ [S, P, R] = b for the mixer and separator rules."""
    A = np.array([[1.0, 0.0, -1.0],
                  [-r, 0.0, 1.0],
                  [-(1.0 - r), 1.0, 0.0]])
    b = np.array([F, 0.0, 0.0])
    return A, b


def solve_plant(F, r):
    """Solve all box rules together. Returns dict with S, P, R in mol/s."""
    if not 0.0 <= r < 1.0:
        raise ValueError("recycle fraction must be at least 0 and below 1: with r = 1 nothing can leave the plant")
    A, b = plant_equations(F, r)
    S, P, R = np.linalg.solve(A, b)
    return {"S": float(S), "P": float(P), "R": float(R)}


# %% [markdown]
# ## Step 2: the "guess and go round" method
# Another way: guess the recycle, run the mixer and separator in order, and see what recycle
# comes back. If it differs from the guess, use the new value and go round again. This is
# **successive substitution**, and it is how flowsheet programs treat a loop (Session 3).

# %%
def go_round(F, r, tol=1e-6, max_rounds=10000):
    """Successive substitution on the recycle. Returns (R, rounds, list of R after each round)."""
    R, hist = 0.0, []
    for k in range(1, max_rounds + 1):
        S = F + R               # mixer
        R_new = r * S           # separator sends r*S back
        hist.append(R_new)
        if abs(R_new - R) < tol:
            return R_new, k, hist
        R = R_new
    return R, max_rounds, hist


def amplification(r):
    """S / F = 1 / (1 - r): how many times the fresh feed flows through the separator."""
    return 1.0 / (1.0 - r)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    out = solve_plant(100.0, 0.6)
    print("F = 100, r = 0.6 ->", {k: round(v, 1) for k, v in out.items()})
    R, rounds, hist = go_round(100.0, 0.6)
    print("rounds needed:", rounds, " first guesses:", [round(h, 1) for h in hist[:3]])
    print("r = 0.9: S =", round(solve_plant(100.0, 0.9)["S"], 1), " rounds:", go_round(100.0, 0.9)[1])

    rs = np.linspace(0, 0.95, 96)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 4.0))
    a1.plot(rs, [amplification(r) for r in rs])
    a1.set_xlabel("recycle fraction r (fraction of S sent back)")
    a1.set_ylabel("S / F (flow through separator per unit feed)")
    a1.set_title("A bigger recycle needs a bigger separator")
    a1.grid(alpha=0.3)
    for r in (0.5, 0.8, 0.9):
        _, _, h = go_round(100.0, r, max_rounds=60)
        a2.plot(range(1, len(h) + 1), h, label=f"r = {r}")
    a2.set_xlabel("round number")
    a2.set_ylabel("recycle guess R (mol/s)")
    a2.set_title("Going round: R creeps to its final value")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "loop.png", dpi=120)

# %% [markdown]
# ## Where this stops
# One number per pipe, a loop that only splits. Session 2 puts real physics in the boxes
# (temperature, composition, boiling), and Session 3 builds the engine that solves a whole flowsheet.
