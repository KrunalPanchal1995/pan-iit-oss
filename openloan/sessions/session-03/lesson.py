"""Session 3 (Level 3): prepayment, floating rates, flat versus reducing, inflation.

Run:  python start.py 3
General education only, not financial advice. All lenders and rates are made up.
"""
# %% [markdown]
# # Session 3: simulate real loans and validate the formulas
# **A. Real-world problem.** Real loans are messy: you may pay extra, the bank may change the
# rate, a "flat 8 percent" offer may hide a much higher true rate, and money loses value over
# time. We build a month-by-month simulator, check it against Session 2's formulas, and use
# it on these cases.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


def emi(P, annual, months):
    """EMI = P r (1+r)^n / ((1+r)^n - 1), r = annual / 12 (Session 2)."""
    r = annual / 12.0
    if r == 0:
        return P / months
    g = (1.0 + r) ** months
    return P * r * g / (g - 1.0)


# %% [markdown]
# ## Step 1: one simulator for everything
# Each month: add interest at the current rate, then subtract the payment (and a lump sum
# if one is due). Stop when the balance is paid off. If the balance has not reached zero
# after `max_months`, report that the loan never clears.

# %%
def simulate(P, rate_by_month, payment, lump=0.0, lump_month=None, max_months=1200):
    """rate_by_month(k) = annual rate in month k (k = 1, 2, ...).
    Returns (months_to_clear, total_interest, balances); months_to_clear is None if never cleared."""
    bal, paid_interest, hist = float(P), 0.0, [float(P)]
    for k in range(1, max_months + 1):
        i = bal * rate_by_month(k) / 12.0
        paid_interest += i
        bal = bal + i
        bal -= min(payment, bal)
        if lump_month is not None and k == lump_month:
            bal -= min(lump, bal)
        hist.append(bal)
        if bal <= 1e-6:
            return k, paid_interest, np.array(hist)
    return None, paid_interest, np.array(hist)


# %% [markdown]
# ## Step 2: prepayment
# Keep the EMI, but pay a lump sum after month 12 (or raise the EMI by 10 percent). The loan
# ends earlier and the interest saved is the drop in total interest.

# %%
def prepayment_case(P=200000.0, annual=0.12, months=60, lump=50000.0, lump_month=12, bump=0.10):
    """Tenure and total interest for: base, lump sum, higher EMI."""
    e = emi(P, annual, months)
    base = simulate(P, lambda k: annual, e)
    with_lump = simulate(P, lambda k: annual, e, lump, lump_month)
    higher = simulate(P, lambda k: annual, e * (1.0 + bump))
    return {"emi": e, "base": base[:2], "lump": with_lump[:2], "higher": higher[:2],
            "balances": (base[2], with_lump[2], higher[2])}


# %% [markdown]
# ## Step 3: a floating rate
# After `change_month` the bank moves the rate. Option 1: keep the EMI (the tenure changes).
# Option 2: recompute the EMI for the months that remain (the tenure stays).

# %%
def floating_case(P=100000.0, old=0.10, new=0.12, months=36, change_month=12):
    e0 = emi(P, old, months)
    keep = simulate(P, lambda k: old if k <= change_month else new, e0)
    bal = simulate(P, lambda k: old, e0, max_months=change_month)[2][change_month]
    e_new = emi(bal, new, months - change_month)
    b, tot = float(P), 0.0
    for k in range(1, months + 1):
        i = b * (old if k <= change_month else new) / 12.0
        tot += i
        b += i - (e0 if k <= change_month else e_new)
    return {"emi_old": e0, "emi_new": e_new, "balance_at_change": bal,
            "keep_emi": keep[:2], "recompute_interest": tot, "final_balance": b}


# %% [markdown]
# ## Step 4: flat rate versus reducing balance
# A flat 8 percent loan charges 8 percent of the ORIGINAL amount every year, for the whole
# tenure, and splits (P + interest) into equal instalments. But you repay principal every
# month, so you owe less than P most of the time. The true rate is the one that makes the
# reducing-balance EMI equal to the flat instalment. We find it by root-finding.

# %%
def flat_instalment(P, flat, months):
    return P * (1.0 + flat * months / 12.0) / months


def true_annual_rate_bisect(P, instalment, months, tol=1e-12):
    """Annual nominal rate (monthly rate * 12) with emi(P, rate, months) = instalment, by bisection."""
    lo, hi = 0.0, 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if emi(P, mid, months) < instalment:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def true_annual_rate_newton(P, instalment, months, start=0.10, steps=60):
    """Same root by Newton's method with a numerical derivative."""
    x = start
    for _ in range(steps):
        f = emi(P, x, months) - instalment
        h = 1e-7
        d = (emi(P, x + h, months) - emi(P, x - h, months)) / (2 * h)
        x_new = x - f / d
        if abs(x_new - x) < 1e-13:
            return x_new
        x = x_new
    return x


# %% [markdown]
# ## Step 5: inflation and the present value of the EMI stream
# A payment k months away is worth less today. With yearly inflation `infl` the value today
# of a payment E in month k is E / (1 + infl/12)^k.

# %%
def present_value(payment, months, infl):
    k = np.arange(1, months + 1)
    return float(np.sum(payment / (1.0 + infl / 12.0) ** k))


# %% [markdown]
# ## Step 6: when a loan is too big (a failure case)
# Two warnings. (1) If the EMI is bigger than the share of income you can spare, the loan is
# not affordable. (2) If the payment is smaller than the monthly interest, the balance grows
# instead of shrinking (negative amortisation) and the loan never clears.

# %%
def max_affordable_loan(income, share, annual, months):
    """Largest P whose EMI is at most income * share."""
    r = annual / 12.0
    g = (1.0 + r) ** months
    return income * share * (g - 1.0) / (r * g)


def is_negative_amortisation(P, annual, payment):
    return payment < P * annual / 12.0


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    c = prepayment_case()
    print(f"EMI {c['emi']:.2f}")
    for key in ("base", "lump", "higher"):
        print(f"{key:7s}: {c[key][0]} months, interest {c[key][1]:.2f}")
    f = floating_case()
    print(f"floating: old EMI {f['emi_old']:.2f}, new EMI {f['emi_new']:.2f}, balance at change {f['balance_at_change']:.2f}")
    print(f"keep EMI: {f['keep_emi'][0]} months, interest {f['keep_emi'][1]:.2f}; recompute: interest {f['recompute_interest']:.2f}, final balance {f['final_balance']:.4f}")
    P = 100000.0
    inst = flat_instalment(P, 0.08, 36)
    rb, rn = true_annual_rate_bisect(P, inst, 36), true_annual_rate_newton(P, inst, 36)
    print(f"flat 8 percent, 36 months: instalment {inst:.2f}, true annual rate bisect {rb:.6f}, newton {rn:.6f}")
    print(f"reducing 8 percent EMI {emi(P, 0.08, 36):.2f}, interest {36 * emi(P, 0.08, 36) - P:.2f}; flat interest {36 * inst - P:.2f}")
    e = emi(P, 0.12, 24)
    print(f"PV of 24 EMIs at 6 percent inflation: {present_value(e, 24, 0.06):.2f} (sum {24 * e:.2f})")
    print(f"max loan at 40 percent of 30000, 12 percent, 60 months: {max_affordable_loan(30000, 0.4, 0.12, 60):.2f}")
    neg = simulate(100000.0, lambda k: 0.12, 800.0, max_months=60)
    print(f"pay 800 on 100000 at 12 percent: balance after 60 months {neg[2][-1]:.2f}")

    fig, ax = plt.subplots(figsize=(6.5, 4))
    for b, lab in zip(c["balances"], ("EMI only", "plus lump sum after month 12", "EMI +10 percent")):
        ax.plot(np.arange(len(b)), b, label=lab)
    ax.set_xlabel("month")
    ax.set_ylabel("balance owed (units)")
    ax.set_title("Prepayment bends the balance curve down")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "prepayment.png", dpi=120)

    rates = np.linspace(0.01, 0.30, 100)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.plot(100 * rates, [emi(P, x, 36) for x in rates], label="reducing-balance EMI")
    ax2.axhline(inst, color="C3", ls="--", label="flat 8 percent instalment")
    ax2.axvline(100 * rb, color="gray", ls=":")
    ax2.set_xlabel("annual rate (percent)")
    ax2.set_ylabel("monthly payment (units)")
    ax2.set_title("The root: the reducing rate that matches the flat offer")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "flat_vs_reducing.png", dpi=120)

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
