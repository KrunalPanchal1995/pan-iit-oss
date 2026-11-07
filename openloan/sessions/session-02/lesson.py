"""Session 2 (Level 2): compound growth and the EMI formula.

Run:  python start.py 2
General education only, not financial advice. All lenders and rates are made up.
"""
# %% [markdown]
# # Session 2: compound growth and the EMI
# **A. Real-world problem.** Most loans are not paid back in one lump. You pay the same
# amount every month, the EMI (equated monthly instalment). Where does that number come
# from, how is each payment split between interest and principal, and why does a longer
# loan cost so much more in total?
#
# Convention used throughout: annual rate `annual` (0.12 = 12 percent a year), monthly
# rate r = annual / 12, `n` months.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: compound growth, n times a year, and the continuous limit
# Adding interest n times a year:  A = P (1 + r/n)^(n t).  Let n grow: the amount creeps up
# towards the limit  P e^(r t)  (continuous compounding) and never passes it.

# %%
def compound_growth(P, rate, n, t):
    """A = P (1 + rate/n)^(n t): interest added n times a year for t years."""
    return P * (1.0 + rate / n) ** (n * t)


def continuous_growth(P, rate, t):
    return P * float(np.exp(rate * t))


# %% [markdown]
# ## Step 2: the EMI formula
# Borrow P, pay the same EMI at the end of each of n months, monthly rate r:
#     EMI = P r (1+r)^n / ((1+r)^n - 1).
# (If r = 0 it is simply P / n.)

# %%
def emi(P, annual, months):
    r = annual / 12.0
    if r == 0:
        return P / months
    g = (1.0 + r) ** months
    return P * r * g / (g - 1.0)


# %% [markdown]
# ## Step 3: check the formula by simulating the balance
# Each month: interest = balance * r is added, then you pay the EMI. If the formula is right
# the balance reaches (almost exactly) zero after n months.

# %%
def simulate_balance(P, annual, months, payment=None):
    """Balance after each month, starting with P. Returns an array of length months + 1."""
    r = annual / 12.0
    pay = emi(P, annual, months) if payment is None else payment
    bal = [P]
    for _ in range(months):
        bal.append(bal[-1] * (1.0 + r) - pay)
    return np.array(bal)


# %% [markdown]
# ## Step 4: the amortisation schedule
# Month k: interest part = balance * r, principal part = EMI - interest part. As the balance
# falls, the interest part falls and the principal part rises. Total interest = n EMI - P.

# %%
def schedule(P, annual, months):
    """Return (interest, principal, balance_after) arrays, one entry per month."""
    r = annual / 12.0
    pay = emi(P, annual, months)
    interest = np.zeros(months)
    principal = np.zeros(months)
    balance = np.zeros(months)
    bal = P
    for k in range(months):
        interest[k] = bal * r
        principal[k] = pay - interest[k]
        bal -= principal[k]
        balance[k] = bal
    return interest, principal, balance


def total_interest(P, annual, months):
    return months * emi(P, annual, months) - P


# %% [markdown]
# ## Step 5: tenure trade-off and the effective annual rate
# A longer tenure lowers the EMI but raises the total interest. To compare offers quoted in
# different ways use the effective annual rate  (1 + annual/12)^12 - 1.

# %%
def tenure_table(P, annual, tenures):
    """List of (months, emi, total_interest) for each tenure."""
    return [(m, emi(P, annual, m), total_interest(P, annual, m)) for m in tenures]


def effective_annual_rate(annual, per_year=12):
    return (1.0 + annual / per_year) ** per_year - 1.0


# %% [markdown]
# ## Step 6: a design problem
# Two made-up offers for the same loan. Offer A has the lower headline rate but a processing
# fee. Total cost = interest + fee. Which is cheaper?

# %%
def total_cost(P, annual, months, fee_fraction=0.0):
    """Interest plus a one-off fee (fee_fraction of P). Money units."""
    return total_interest(P, annual, months) + fee_fraction * P


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    P, ann, m = 100000.0, 0.12, 24
    print(f"EMI for {P:.0f} at 12 percent over {m} months: {emi(P, ann, m):.2f}")
    print("final simulated balance:", round(simulate_balance(P, ann, m)[-1], 6))
    for n in (1, 2, 4, 12, 365, 100000):
        print(f"n = {n:6d}: {compound_growth(1000, 0.10, n, 5):.3f}")
    print(f"continuous limit: {continuous_growth(1000, 0.10, 5):.3f}")
    it, pr, bal = schedule(P, ann, m)
    print(f"month 1: interest {it[0]:.2f}, principal {pr[0]:.2f}; month {m}: interest {it[-1]:.2f}, principal {pr[-1]:.2f}")
    print(f"total interest {total_interest(P, ann, m):.2f}")
    for row in tenure_table(P, ann, (12, 24, 36, 48, 60)):
        print("tenure %2d months: EMI %9.2f, total interest %9.2f" % row)
    print(f"effective annual rate of 12 percent: {100 * effective_annual_rate(0.12):.3f} percent")
    for name, a, f in (("A", 0.090, 0.02), ("B", 0.098, 0.0)):
        print(f"offer {name}: EMI {emi(P, a, 36):.2f}, total cost {total_cost(P, a, 36, f):.2f}")

    months = np.arange(1, m + 1)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.bar(months, it, label="interest part")
    ax.bar(months, pr, bottom=it, label="principal part")
    ax.set_xlabel("month")
    ax.set_ylabel("EMI split (units)")
    ax.set_title("Each EMI: interest falls, principal rises")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "amortisation.png", dpi=120)

    ten = np.arange(6, 121, 6)
    tab = tenure_table(P, ann, ten)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.plot(ten, [x[1] for x in tab], "o-", color="C0", label="EMI (left)")
    ax2.set_xlabel("tenure (months)")
    ax2.set_ylabel("EMI (units per month)", color="C0")
    ax3 = ax2.twinx()
    ax3.plot(ten, [x[2] for x in tab], "s-", color="C3", label="total interest (right)")
    ax3.set_ylabel("total interest (units)", color="C3")
    ax2.set_title("Longer tenure: smaller EMI, much more interest")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "tenure_tradeoff.png", dpi=120)

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
