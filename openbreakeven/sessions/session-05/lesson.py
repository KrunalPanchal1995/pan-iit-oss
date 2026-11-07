"""Session 5 (Level 3): seasons and a loan.

Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: seasons and a loan
# **A. Real-world problem.** The made-up bakery of Sessions 2 to 4 sells the same number of loaves
# every month and pays for everything out of its own pocket. Real bakeries sell far more in
# December than in February, and most borrow part of the start-up money and repay it in equal
# monthly instalments. Over a whole year a seasonal bakery can earn exactly as much as a flat
# one and still run out of cash in March, because the instalment is due every month but the
# customers are not. Today you build a 12-month demand pattern and a loan, follow the running
# cash total month by month, and ask how much extra cash the owner needs.
#
# *General education only: the bakery, the loan and their numbers are made up, and this is not
# financial advice.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

F, P, V, Q = 1200.0, 3.50, 1.40, 800.0          # as in Sessions 2 to 4: planned profit 480 dollars a month
STARTUP = 6000.0                                # start-up cost of Session 3's payback example
MONTH_NAMES = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
# made-up seasonal factors (the average is exactly 1.0): quiet in winter, a December peak
SEASON = (0.85, 0.80, 0.90, 0.95, 1.00, 0.95, 0.90, 0.90, 1.00, 1.05, 1.15, 1.55)


# %% [markdown]
# ## Step 1: a 12-month demand pattern
# A **seasonal factor** says how a month's demand compares with the yearly average: 1.55 means
# 55 % more than average. We require the 12 factors to average exactly 1.0, so that the pattern
# moves sales *around* the yearly average and does not add or remove any. Then each month's
# profit is (p - v) x (planned demand x factor) - F, and because that is a straight line in the
# factor, the twelve profits add up to exactly twelve times the flat monthly profit.

# %%
def check_season(season):
    if len(season) != 12:
        raise ValueError("a seasonal pattern needs 12 factors")
    if min(season) < 0:
        raise ValueError("a seasonal factor cannot be negative")
    if abs(sum(season) / 12.0 - 1.0) > 1e-9:
        raise ValueError("the 12 seasonal factors must average 1.0")
    return tuple(season)


def scale_season(season, k):
    """Stronger (k > 1) or weaker (k < 1) seasons; k = 0 is a flat year. The average stays 1.0."""
    new = [1.0 + k * (x - 1.0) for x in check_season(season)]
    if min(new) < 0:
        raise ValueError("that k would make a seasonal factor negative")
    return check_season(new)


def monthly_profits(season=SEASON, months=24, start=1, p=P, v=V, d_mu=Q, fixed=F):
    """Profit of each month for `months` months; the pattern repeats every year; `start` is the opening month (1 = January)."""
    season = check_season(season)
    if not 1 <= start <= 12:
        raise ValueError("the opening month must be 1 to 12")
    return np.array([(p - v) * d_mu * season[(start - 1 + m) % 12] - fixed for m in range(months)])


# %% [markdown]
# ## Step 2: a loan repaid in equal monthly instalments
# Borrow L at an annual rate `apr` (a nominal rate, so the monthly rate is r = apr / 12) and repay
# it in n equal instalments at the end of each month. The instalment that clears the debt exactly is
# `L r / (1 - (1 + r)^-n)`, and with no interest it is simply L / n. Each instalment pays that
# month's interest (balance x r) first and the rest reduces the balance. (The openloan repo
# explains this in detail.)

# %%
def loan_payment(principal, apr, n):
    if n < 1 or principal < 0 or apr < 0:
        raise ValueError("need a positive term and a non-negative principal and rate")
    r = apr / 12.0
    return principal / n if r == 0 else principal * r / (1.0 - (1.0 + r) ** -n)


def loan_schedule(principal, apr, n):
    """One row per month: instalment, interest, repaid part and balance left."""
    pay, r, bal, rows = loan_payment(principal, apr, n), apr / 12.0, principal, []
    for m in range(1, n + 1):
        interest = bal * r
        repaid = pay - interest
        bal -= repaid
        rows.append({"month": m, "payment": pay, "interest": interest, "repaid": repaid, "balance": 0.0 if abs(bal) < 1e-9 else bal})
    return rows


def total_interest(principal, apr, n):
    return loan_payment(principal, apr, n) * n - principal


# %% [markdown]
# ## Step 3: the running cash total, month by month
# At month 0 the owner pays the part of the start-up cost that is *not* borrowed: `startup - loan`
# (this is the first running total, minus that amount). Each month the cash changes by that
# month's profit minus the loan instalment (while the loan lasts). The **extra cash needed** is
# how far the running total falls *below its starting point*: the owner must then add money from
# somewhere else. It is zero when the cash never falls below where it began.

# %%
def running_total(profits, startup=STARTUP, loan=0.0, apr=0.09, term=12):
    """Cash after each month (the owner's equity startup - loan is already spent at month 0)."""
    profits = np.asarray(profits, dtype=float)
    pay = loan_payment(loan, apr, term) if loan > 0 else 0.0
    inst = np.where(np.arange(len(profits)) < term, pay, 0.0)
    return -(startup - loan) + np.cumsum(profits - inst)


def extra_cash_needed(profits, loan=0.0, apr=0.09, term=12):
    """Largest fall of the running total below its starting level (dollars, 0 if it never falls)."""
    pay = loan_payment(loan, apr, term) if loan > 0 else 0.0
    inst = np.where(np.arange(len(profits)) < term, pay, 0.0)
    return float(max(0.0, -np.min(np.cumsum(np.asarray(profits, dtype=float) - inst))))


def lowest_month(profits, loan=0.0, apr=0.09, term=12):
    """(month number, change of the running total since the start) at the lowest point."""
    pay = loan_payment(loan, apr, term) if loan > 0 else 0.0
    inst = np.where(np.arange(len(profits)) < term, pay, 0.0)
    cs = np.cumsum(np.asarray(profits, dtype=float) - inst)
    return int(np.argmin(cs)) + 1, float(np.min(cs))


def equity_recovered_month(profits, startup=STARTUP, loan=0.0, apr=0.09, term=12):
    """First month in which the running total is back to zero (None if not within the profits given)."""
    ok = np.nonzero(running_total(profits, startup, loan, apr, term) >= -1e-9)[0]
    return int(ok[0]) + 1 if len(ok) else None


# %% [markdown]
# ## Step 4: the start month matters
# The pattern repeats every year, so *when* the bakery opens decides whether the weak months
# come before or after the strong ones. Opening in January puts the worst months (Jan to Mar)
# first, with no December cash in hand; opening in April puts December before the second winter.

# %%
def extra_cash_by_start(loan, apr, term, season=SEASON, months=24):
    return {s: extra_cash_needed(monthly_profits(season, months, s), loan, apr, term) for s in range(1, 13)}


# %% [markdown]
# ## Step 5: when demand is also random
# Add the randomness of Session 3: in each month the demand is the seasonal mean plus a normal
# error (sd 150 loaves, months independent). We draw many years (seeded) and report the share of
# years in which the owner needs more than a given buffer of extra cash.

# %%
def simulate_cash(n=5000, seed=42, season=SEASON, months=24, start=1, loan=4000.0, apr=0.09, term=12,
                  d_sd=150.0, p=P, v=V, d_mu=Q, fixed=F):
    """Cash change since the start, month by month, for n simulated years (shape n x months)."""
    season = check_season(season)
    rng = np.random.default_rng(seed)
    mean_d = np.array([d_mu * season[(start - 1 + m) % 12] for m in range(months)])
    dem = np.maximum(mean_d + d_sd * rng.standard_normal((n, months)), 0.0)
    pay = loan_payment(loan, apr, term) if loan > 0 else 0.0
    inst = np.where(np.arange(months) < term, pay, 0.0)
    return np.cumsum((p - v) * dem - fixed - inst, axis=1)


def shortfall_probability(buffer, **kw):
    """Share of simulated years in which the extra cash needed is more than `buffer` dollars."""
    cs = simulate_cash(**kw)
    return float(np.mean(-cs.min(axis=1) > buffer))


# %% [markdown]
# ## Step 6: choose the loan (the mini-project engine)
# For a loan size and a term, report the instalment, the total interest, the extra cash needed in
# the planned (non-random) year and the chance that more than the owner's buffer is needed.

# %%
def evaluate_loan(loan, term, apr=0.09, buffer=1000.0, start=1, season=SEASON, n=5000, seed=42):
    profits = monthly_profits(season, 24, start)
    return {"loan": loan, "term": term, "payment": loan_payment(loan, apr, term) if loan > 0 else 0.0,
            "interest": total_interest(loan, apr, term) if loan > 0 else 0.0,
            "extra": extra_cash_needed(profits, loan, apr, term),
            "risk": shortfall_probability(buffer, n=n, seed=seed, season=season, start=start, loan=loan, apr=apr, term=term)}


def loan_passes(r, buffer=1000.0, max_risk=0.10):
    """Mini-project rule: the planned year needs at most `buffer` of extra cash and the chance of needing more than `buffer` is at most 10 %."""
    return r["extra"] <= buffer and r["risk"] <= max_risk


# %% [markdown]
# ## See it
# Figure 1: the twelve monthly profits against the instalment of a 4000 dollar, 12-month loan.
# Figure 2: the running cash total of the seasonal bakery and of a flat bakery with the same
# yearly profit.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    prof = monthly_profits()
    print("monthly profits:", np.round(prof[:12], 1), "sum", round(prof[:12].sum(), 1), "flat x 12", 12 * (P - V) * Q - 12 * F)
    for n in (6, 12, 18, 24):
        a = loan_payment(4000, 0.09, n)
        print(f"4000 at 9 %, {n:2d} months: instalment {a:7.2f}  interest {total_interest(4000, 0.09, n):6.1f}  extra cash {extra_cash_needed(prof, 4000, 0.09, n):6.1f}  lowest month {lowest_month(prof, 4000, 0.09, n)}")
    print("extra cash by opening month (4000, 12 months):", {k: round(v_, 1) for k, v_ in extra_cash_by_start(4000, 0.09, 12).items()})
    flat = monthly_profits(scale_season(SEASON, 0.0))
    print("flat year extra cash:", extra_cash_needed(flat, 4000, 0.09, 12))
    for loan in (2000, 3000, 4000, 5000):
        for term in (6, 12, 18, 24):
            r = evaluate_loan(loan, term)
            print(f"loan {loan} term {term:2d}: instalment {r['payment']:6.1f} interest {r['interest']:6.1f} extra {r['extra']:6.1f} risk {100 * r['risk']:5.1f} % {'PASS' if loan_passes(r) else ''}")

    BLUE, ORANGE, MAGENTA = "#0072b2", "#c86a00", "#d81b60"
    pay12 = loan_payment(4000, 0.09, 12)
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.bar(range(12), prof[:12], color=[BLUE if x >= pay12 else MAGENTA for x in prof[:12]])
    ax.axhline(pay12, color="black", ls="--", lw=1.5)
    ax.text(0.1, pay12 + 25, f"instalment {pay12:.0f} dollars (4000 at 9 %, 12 months)", fontsize=8)
    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_NAMES, fontsize=8)
    ax.set_ylabel("monthly profit ($)")
    ax.set_title("Five months do not cover the instalment (magenta)", fontsize=10)
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "monthly_profit.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.0))
    months = np.arange(0, 25)
    for pr, col, ls, lab in ((prof, BLUE, "-", "seasonal bakery"), (flat, ORANGE, "--", "flat bakery, same yearly profit")):
        cs = np.concatenate([[0.0], np.cumsum(pr - np.where(np.arange(24) < 12, pay12, 0.0))])
        ax2.plot(months, cs, color=col, ls=ls, lw=2, marker="o", ms=3, label=lab)
    ax2.axhline(0, color="black", lw=0.8)
    ax2.set_xlabel("months since opening in January")
    ax2.set_ylabel("cash change since the start ($)")
    ax2.set_title("Same yearly profit, but the seasonal one dips by 365 dollars", fontsize=10)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "cash_dip.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
