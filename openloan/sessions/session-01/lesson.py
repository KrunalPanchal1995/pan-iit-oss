"""Session 1 (Level 1): why you pay back more than you borrowed.

Run:  python start.py 1
General education only, not financial advice. All lenders and rates are made up.
"""
# %% [markdown]
# # Session 1: why you pay back more than you borrowed
# **A. Real-world problem.** A friend lends you 10000 units today. A bank does the same, but
# it charges *interest*: a price for using its money. How much do you owe after 3 years, and
# why does "interest on interest" make the amount grow faster and faster?
#
# **Plan.** (1) simple interest, (2) compound interest, (3) compare them over time,
# (4) ask how long it takes for a debt to double.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: simple interest
# Interest is charged only on the original amount `P` (the principal), at a yearly rate `r`
# (0.10 means 10 percent a year). After `t` years you owe  A = P (1 + r t).
# Example: P = 10000, r = 0.10, t = 3  ->  interest 3000, amount 13000.

# %%
def simple_amount(P, r, t):
    """Amount owed after t years with simple interest."""
    return P * (1 + r * t)


# %% [markdown]
# ## Step 2: compound interest
# Now each year's interest is added to the debt, so next year you pay interest on it too:
#     after 1 year: P (1 + r),  after 2 years: P (1 + r)^2,  after t years: P (1 + r)^t.
# Same example: 10000 * 1.1 * 1.1 * 1.1 = 13310. That is 310 more than simple interest.

# %%
def compound_amount(P, r, t):
    """Amount owed after t whole years with interest added once a year."""
    return P * (1 + r) ** t


# %% [markdown]
# ## Step 3: how long until the debt doubles?
# Simple interest adds the same slice every year, so doubling takes 1 / r years.
# Compound interest grows by a *factor*, so we need (1 + r)^t = 2, i.e. t = ln 2 / ln(1 + r).

# %%
def doubling_time_simple(r):
    return 1.0 / r


def doubling_time_compound(r):
    return float(np.log(2.0) / np.log(1.0 + r))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    P, r = 10000.0, 0.10
    for t in (1, 2, 3):
        print(f"year {t}: simple {simple_amount(P, r, t):.0f}, compound {compound_amount(P, r, t):.0f}")
    print(f"doubling time at 10 percent: simple {doubling_time_simple(r):.2f} y, compound {doubling_time_compound(r):.2f} y")
    t = np.linspace(0, 20, 201)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(t, simple_amount(P, r, t), label="simple interest")
    ax.plot(t, compound_amount(P, r, t), label="compound interest")
    ax.axhline(2 * P, color="gray", ls=":")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("amount owed (units)")
    ax.set_title("Borrow 10000 at 10 percent a year")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "simple_vs_compound.png", dpi=120)
    yrs = np.arange(0, 4)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(yrs - 0.2, simple_amount(P, r, yrs) - P, 0.4, label="simple: interest so far")
    ax2.bar(yrs + 0.2, compound_amount(P, r, yrs) - P, 0.4, label="compound: interest so far")
    ax2.set_xlabel("time (years)")
    ax2.set_ylabel("interest owed so far (units)")
    ax2.set_title("The first three years")
    ax2.set_xticks(yrs)
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "first_three_years.png", dpi=120)

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
