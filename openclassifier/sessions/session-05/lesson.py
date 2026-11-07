"""Session 5 (Level 3): one threshold for each group: equalise the false-positive rates and see what it costs.

Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: a threshold for each group
# **A. Real-world problem.** In Session 3 one threshold on the score gave group A a false-positive rate
# of 0.16 and group B a rate of 0.31: twice as many false alarms for B, because B's measuring instrument
# reads 0.5 too high. Session 3 showed the gap but not the repair. Today you build a tool that picks
# **one threshold per group** so that the false-positive rates agree, and you find out what the repair
# costs: it is free in the Session 3 setting, and it is *not* free when the groups differ in how common
# the condition is, or in how good the instrument is. We also see why the fairness definitions cannot
# all hold at once, and how many cases it takes to set the thresholds from data. All data are
# synthetic, and nothing here says anything about real people.
#
# **Plan.** (1) a model of a group, (2) the repair, (3) three situations, (4) the identity behind the
# impossibility, (5) setting the thresholds from data, (6) how many cases are needed, (7) failure cases.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 0: the pieces from Session 3, unchanged
# `phi` is the standard normal CDF. In Session 3 negatives score around 0 and positives around `d`
# (spread 1), group B's scores are all shifted up by `shift`, and 30 percent of the cases are positive.

# %%
def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def group_rates_analytic(t, shift, d=1.5):
    return {"fpr_A": 1 - phi(t), "tpr_A": 1 - phi(t - d),
            "fpr_B": 1 - phi(t - shift), "tpr_B": 1 - phi(t - shift - d)}


def simulate_group(n, shift, d=1.5, seed=0):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < 0.3).astype(int)
    return rng.normal(d * y + shift, 1.0), y


def empirical_rates(scores, y, t):
    pred = scores >= t
    return float(np.mean(pred[y == 0])), float(np.mean(pred[y == 1]))


# %% [markdown]
# ## Step 1: a group has three numbers
# A group is described by `prev` (the share of positive cases), `d` (how far apart the instrument puts
# positives and negatives: bigger means a better instrument) and `shift` (how much the instrument reads
# too high). With a threshold `t` every rate follows from the normal curve:
#
#     FPR = 1 - Phi(t - shift)          TPR = 1 - Phi(t - shift - d)
#     flagged = prev * TPR + (1 - prev) * FPR          PPV = prev * TPR / flagged
#     errors per person = prev * (1 - TPR) + (1 - prev) * FPR
#
# PPV (positive predictive value) is the share of flagged people who really are positive.
# To go the other way, from a wanted FPR to a threshold, we need the inverse of Phi.

# %%
def make_group(name, prev=0.3, d=1.5, shift=0.0):
    if not 0.0 < prev < 1.0:
        raise ValueError("prev must be strictly between 0 and 1")
    if d <= 0:
        raise ValueError("d must be positive (positives must score higher than negatives)")
    return {"name": name, "prev": float(prev), "d": float(d), "shift": float(shift)}


GROUP_A = make_group("A")
GROUP_B = make_group("B", shift=0.5)


def inv_phi(p):
    """Inverse of phi by bisection (phi is increasing, so this is safe)."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be strictly between 0 and 1")
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def rates(g, t):
    fpr = 1 - phi(t - g["shift"])
    tpr = 1 - phi(t - g["shift"] - g["d"])
    flagged = g["prev"] * tpr + (1 - g["prev"]) * fpr
    ppv = g["prev"] * tpr / flagged if flagged > 1e-300 else float("nan")
    errors = g["prev"] * (1 - tpr) + (1 - g["prev"]) * fpr
    return {"fpr": fpr, "tpr": tpr, "ppv": ppv, "flagged": flagged, "errors": errors}


def threshold_for_fpr(g, target_fpr):
    """The threshold at which group g has the false-positive rate target_fpr."""
    if not 0.0 < target_fpr < 1.0:
        raise ValueError("target_fpr must be strictly between 0 and 1")
    return g["shift"] + inv_phi(1 - target_fpr)


def spread(values):
    values = list(values)
    return max(values) - min(values)


# %% [markdown]
# ## Step 2: the repair, and the Session 3 numbers
# **One threshold** `t = 1`: group A has FPR 0.159 and group B has 0.309. The gap is the larger rate minus
# the smaller one. **One threshold per group**: pick a target FPR (here group A's value at `t = 1`) and
# move B's threshold to the point where B's FPR equals it. Because B's scores are exactly A's scores plus
# 0.5, the new threshold is `1 + 0.5 = 1.5`. In this special case every other rate becomes equal as well.

# %%
def single_threshold_report(groups, t):
    return {g["name"]: rates(g, t) for g in groups}


def equal_fpr_thresholds(groups, target_fpr):
    return {g["name"]: threshold_for_fpr(g, target_fpr) for g in groups}


def per_group_report(groups, thresholds):
    return {g["name"]: rates(g, thresholds[g["name"]]) for g in groups}


def fpr_gap(report):
    return spread(r["fpr"] for r in report.values())


def errors_per_1000(report):
    return {name: 1000 * r["errors"] for name, r in report.items()}


# %% [markdown]
# ## Step 3: what does the repair cost?
# Equal false-positive rates are one wish. Three others are natural: equal **true-positive rates** (the
# same share of positives found), equal **PPV** (a flag means the same thing in both groups), and the
# roadmap's floor that **no group's TPR drops below 0.6**. Three situations, all with the same repair
# (equal FPR at the Session 3 value 0.159):
#
# 1. **Pure instrument bias** (Session 3): B differs from A only by `shift`. Free.
# 2. **Different prevalence**: B has 50 percent positives instead of 30. FPR and TPR still agree, PPV does not.
# 3. **A weaker instrument for B**: `d = 1.0` instead of 1.5. FPR agrees, B's TPR collapses to 0.50.
#
# For situation 3 the way out is to raise the common FPR until the weaker group reaches the TPR floor.
# Raising the common FPR costs both groups more false alarms: that is the price of the floor.

# %%
GROUP_B_BASE = make_group("B", prev=0.5, shift=0.5)
GROUP_B_WEAK = make_group("B", d=1.0, shift=0.5)


def fpr_needed_for_tpr(g, tpr_floor):
    """Smallest FPR at which group g reaches the true-positive rate tpr_floor."""
    if not 0.0 < tpr_floor < 1.0:
        raise ValueError("tpr_floor must be strictly between 0 and 1")
    return 1 - phi(g["d"] + inv_phi(1 - tpr_floor))


def lowest_common_fpr(groups, tpr_floor):
    """Smallest common FPR at which every group has TPR >= tpr_floor."""
    return max(fpr_needed_for_tpr(g, tpr_floor) for g in groups)


def three_situations(target_fpr=None, tpr_floor=0.6):
    if target_fpr is None:
        target_fpr = rates(GROUP_A, 1.0)["fpr"]
    out = {}
    for label, gb in (("pure bias", GROUP_B), ("different prevalence", GROUP_B_BASE), ("weaker instrument", GROUP_B_WEAK)):
        groups = [GROUP_A, gb]
        out[label] = per_group_report(groups, equal_fpr_thresholds(groups, target_fpr))
    groups = [GROUP_A, GROUP_B_WEAK]
    common = max(target_fpr, lowest_common_fpr(groups, tpr_floor))
    out["weaker, with floor"] = per_group_report(groups, equal_fpr_thresholds(groups, common))
    return out, common


# %% [markdown]
# ## Step 4: the identity behind the impossibility
# Bayes' rule gives, for every group, the **odds form**
#
#     PPV / (1 - PPV) = prev / (1 - prev) * TPR / FPR
#
# Suppose two groups have the same FPR and the same TPR but different `prev`. The right side then
# differs, so their PPVs must differ: equal error rates and equal PPV cannot both hold. Forcing equal
# PPV *and* equal FPR means changing a TPR, by the factor below. When that TPR would have to exceed 1,
# equal PPV is impossible at that FPR altogether.

# %%
def ppv_from(prev, tpr, fpr):
    return prev * tpr / (prev * tpr + (1 - prev) * fpr)


def tpr_for_equal_ppv(ppv, prev, fpr):
    """The TPR a group with prevalence prev needs, at false-positive rate fpr, to reach the PPV ppv."""
    if not 0.0 < ppv < 1.0:
        raise ValueError("ppv must be strictly between 0 and 1")
    odds = ppv / (1 - ppv)
    tpr = odds * (1 - prev) / prev * fpr
    if tpr > 1.0:
        raise ValueError(f"equal PPV is impossible at FPR {fpr:.3f}: it would need a TPR of {tpr:.2f}")
    return tpr


# %% [markdown]
# ## Step 5: set the thresholds from data
# We never know `d` and `shift`. We have labelled cases. For each group, the threshold with FPR `f` is the
# `(1 - f)` quantile of that group's *negative* scores: a share `f` of the negatives scores above it.
# Fit the thresholds on a **calibration set**, then judge them on cases that did not take part in the
# fit (here the Session 3 data, 20000 cases per group).

# %%
def simulate_group_g(n, g, seed=0):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < g["prev"]).astype(int)
    return rng.normal(g["d"] * y + g["shift"], 1.0), y


def fit_thresholds(data, target_fpr):
    if not 0.0 < target_fpr < 1.0:
        raise ValueError("target_fpr must be strictly between 0 and 1")
    out = {}
    for name, (scores, y) in data.items():
        neg = scores[y == 0]
        if len(neg) == 0:
            raise ValueError(f"group {name} has no negative cases, so its false-positive rate cannot be set")
        out[name] = float(np.quantile(neg, 1 - target_fpr))
    return out


def empirical_report(data, thresholds):
    out = {}
    for name, (scores, y) in data.items():
        pred = scores >= thresholds[name]
        fpr, tpr = empirical_rates(scores, y, thresholds[name])
        out[name] = {"fpr": fpr, "tpr": tpr, "flagged": float(np.mean(pred)),
                     "ppv": float(np.mean(y[pred])) if pred.any() else float("nan"),
                     "errors": float(np.mean(pred != y))}
    return out


def threshold_tool(calibration, test, target_fpr, single_t=None):
    """The mini-project: one threshold per group from the calibration data, reported on the test data."""
    th = fit_thresholds(calibration, target_fpr)
    out = {"thresholds": th, "per_group": empirical_report(test, th)}
    if single_t is not None:
        out["single"] = empirical_report(test, {name: single_t for name in test})
    return out


# %% [markdown]
# ## Step 6: how many cases does it take?
# The fitted threshold is only as good as the quantile estimate. With `n` calibration cases per group
# (70 percent negatives) the FPR of each fitted threshold has a standard error of about
# `sqrt(f (1 - f) / (0.7 n))`. The *true* gap of the fitted thresholds (from the normal curve, so with no
# test-set noise) is therefore random. `gap_study` repeats the fit with fresh calibration data.

# %%
def gap_study(n_cal, reps=100, target_fpr=None, groups=None, seed0=5000):
    groups = groups or [GROUP_A, GROUP_B]
    if target_fpr is None:
        target_fpr = rates(GROUP_A, 1.0)["fpr"]
    gaps, min_tprs = [], []
    for r in range(reps):
        cal = {g["name"]: simulate_group_g(n_cal, g, seed0 + 2 * r + i) for i, g in enumerate(groups)}
        th = fit_thresholds(cal, target_fpr)
        rep = per_group_report(groups, th)
        gaps.append(fpr_gap(rep))
        min_tprs.append(min(v["tpr"] for v in rep.values()))
    return np.array(gaps), np.array(min_tprs)


SIZES = (200, 500, 2000, 10000, 20000)


def size_table(sizes=SIZES, reps=100):
    return {n: gap_study(n, reps) for n in sizes}


def headline(cal_seeds=(101, 102), test_seeds=(1, 2), n=20000, t_single=1.0):
    """The Session 3 settings: single threshold against fitted per-group thresholds, on the Session 3 test data."""
    cal = {"A": simulate_group_g(n, GROUP_A, cal_seeds[0]), "B": simulate_group_g(n, GROUP_B, cal_seeds[1])}
    test = {"A": simulate_group_g(n, GROUP_A, test_seeds[0]), "B": simulate_group_g(n, GROUP_B, test_seeds[1])}
    target = rates(GROUP_A, t_single)["fpr"]
    out = threshold_tool(cal, test, target, single_t=t_single)
    out["target"] = target
    out["true_report"] = per_group_report([GROUP_A, GROUP_B], out["thresholds"])
    return out


# %% [markdown]
# ## See it
# Figure 1: left, the false-positive rate of both groups against the threshold (one threshold, gap 0.15;
# one threshold per group, no gap); right, the same decisions on the ROC curve. Figure 2: the repair in
# the three situations plus the floor. Figure 3: how the gap of fitted thresholds shrinks with the
# number of calibration cases.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA, GREY = "#0072b2", "#c86a00", "#d81b60", "#555555"
    groups = [GROUP_A, GROUP_B]
    single = single_threshold_report(groups, 1.0)
    target = single["A"]["fpr"]
    thr = equal_fpr_thresholds(groups, target)
    fixed = per_group_report(groups, thr)
    print("single threshold t=1:", {k: {a: round(b, 4) for a, b in v.items()} for k, v in single.items()})
    print("gap with one threshold:", round(fpr_gap(single), 4))
    print("per-group thresholds:", {k: round(v, 4) for k, v in thr.items()})
    print("per-group report:", {k: {a: round(b, 4) for a, b in v.items()} for k, v in fixed.items()})
    print("gap with one threshold per group:", round(fpr_gap(fixed), 6))
    print("errors per 1000 people: single", {k: round(v, 1) for k, v in errors_per_1000(single).items()},
          " per group", {k: round(v, 1) for k, v in errors_per_1000(fixed).items()})

    sit, common = three_situations()
    for label, rep in sit.items():
        print(label, {k: {a: round(b, 3) for a, b in v.items() if a in ("fpr", "tpr", "ppv")} for k, v in rep.items()})
    print("common FPR needed for the TPR floor 0.6 with the weaker instrument:", round(common, 4))
    print("extra false alarms per 1000 negatives for group A:", round(1000 * (common - target), 1))

    ppv_a = single["A"]["ppv"]
    print("equal PPV and FPR for B with prevalence 0.5 needs TPR", round(tpr_for_equal_ppv(ppv_a, 0.5, target), 4))
    try:
        tpr_for_equal_ppv(ppv_a, 0.1, target)
    except ValueError as e:
        print("prevalence 0.1:", e)

    h = headline()
    print("fitted thresholds:", {k: round(v, 4) for k, v in h["thresholds"].items()})
    print("test report, single threshold:", {k: {a: round(b, 4) for a, b in v.items()} for k, v in h["single"].items()})
    print("test report, per group:", {k: {a: round(b, 4) for a, b in v.items()} for k, v in h["per_group"].items()})
    print("empirical gap:", round(fpr_gap(h["single"]), 4), "->", round(fpr_gap(h["per_group"]), 4),
          "  true gap of fitted thresholds:", round(fpr_gap(h["true_report"]), 4))

    table = size_table()
    for n, (gaps, mt) in table.items():
        print(f"n = {n:>5}: mean true gap {gaps.mean():.4f}, 95th percentile {np.quantile(gaps, .95):.4f}, "
              f"gap <= 0.01 in {int(np.sum(gaps <= 0.01))} of 100, smallest TPR over runs {mt.min():.3f}")

    # Figure 1
    fig1, axs = plt.subplots(1, 2, figsize=(9.6, 4))
    ts = np.linspace(-1.5, 3.5, 200)
    axs[0].plot(ts, [1 - phi(x) for x in ts], color=BLUE, label="group A")
    axs[0].plot(ts, [1 - phi(x - 0.5) for x in ts], color=ORANGE, label="group B")
    axs[0].axvline(1.0, color=GREY, ls=":")
    axs[0].plot([1.0, 1.0], [single["A"]["fpr"], single["B"]["fpr"]], "o", color=MAGENTA, label=f"one threshold: gap {fpr_gap(single):.2f}")
    axs[0].plot([thr["A"], thr["B"]], [target, target], "s", color="black", label="one threshold per group: gap 0")
    axs[0].axhline(target, color=GREY, ls=":", lw=1)
    axs[0].set_xlabel("threshold on the score"); axs[0].set_ylabel("false-positive rate"); axs[0].grid(alpha=0.3)
    axs[0].legend(fontsize=8); axs[0].set_title("False-positive rate against threshold", fontsize=10)
    fa = np.linspace(0.001, 0.999, 300)
    roc = [1 - phi(inv_phi(1 - f) - 1.5) for f in fa]
    axs[1].plot(fa, roc, color=GREY, lw=1.5, label="ROC curve (same for A and B)")
    axs[1].plot(single["A"]["fpr"], single["A"]["tpr"], "o", color=BLUE, label="A, t = 1")
    axs[1].plot(single["B"]["fpr"], single["B"]["tpr"], "o", color=ORANGE, label="B, t = 1")
    axs[1].plot(fixed["B"]["fpr"], fixed["B"]["tpr"], "s", color="black", ms=8, mfc="none", label="A and B, one threshold each")
    axs[1].axhline(0.6, color=MAGENTA, ls=":"); axs[1].text(0.55, 0.62, "TPR floor 0.6", color=MAGENTA, fontsize=8)
    axs[1].set_xlabel("false-positive rate"); axs[1].set_ylabel("true-positive rate"); axs[1].grid(alpha=0.3)
    axs[1].legend(fontsize=8, loc="lower right"); axs[1].set_title("The same decisions on the ROC curve", fontsize=10)
    fig1.tight_layout(); fig1.savefig(OUT / "fpr_and_roc.png", dpi=120)

    # Figure 2
    fig2, axs2 = plt.subplots(1, 4, figsize=(12, 3.8), sharey=True)
    titles = {"pure bias": "1. pure bias\n(Session 3)", "different prevalence": "2. B has 50%\npositives",
              "weaker instrument": "3. weaker instrument\nfor B, equal FPR", "weaker, with floor": f"4. same, common FPR\nraised to {common:.3f}"}
    for ax, (label, rep) in zip(axs2, sit.items()):
        xs = np.arange(3)
        for k, (nm, col) in enumerate((("A", BLUE), ("B", ORANGE))):
            vals = [rep[nm]["fpr"], rep[nm]["tpr"], rep[nm]["ppv"]]
            ax.bar(xs + (k - 0.5) * 0.38, vals, 0.36, color=col, label=f"group {nm}")
            for x, v in zip(xs + (k - 0.5) * 0.38, vals):
                ax.text(x, v + 0.015, f"{v:.2f}", ha="center", fontsize=7)
        ax.axhline(0.6, color=MAGENTA, ls=":", lw=1)
        ax.set_xticks(xs); ax.set_xticklabels(["FPR", "TPR", "PPV"]); ax.set_title(titles[label], fontsize=9); ax.set_ylim(0, 1.0)
    axs2[0].set_ylabel("rate"); axs2[0].legend(fontsize=8, loc="upper left")
    fig2.tight_layout(); fig2.savefig(OUT / "three_situations.png", dpi=120)

    # Figure 3
    fig3, ax3 = plt.subplots(figsize=(6.4, 4))
    ns = list(table)
    ax3.plot(ns, [table[n][0].mean() for n in ns], "o-", color=BLUE, label="mean gap")
    ax3.plot(ns, [np.quantile(table[n][0], .95) for n in ns], "s--", color=ORANGE, label="95th percentile")
    ax3.axhline(0.01, color=MAGENTA, ls=":", label="target 0.01")
    ax3.set_xscale("log"); ax3.set_xlabel("calibration cases per group"); ax3.set_ylabel("true false-positive-rate gap")
    ax3.set_title("The gap of fitted thresholds shrinks slowly with the data", fontsize=9); ax3.grid(alpha=0.3); ax3.legend(fontsize=8)
    fig3.tight_layout(); fig3.savefig(OUT / "gap_vs_size.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
