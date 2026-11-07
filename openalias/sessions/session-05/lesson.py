"""Session 5 (Level 3): a third clip extends the unambiguous range, and lowers the noise.

Educational model only. Not a measurement method for any real machine or safety decision.
Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: a third clip
# **A. Real-world problem.** Two clips at 30 and 24 fps cannot tell 22.5 rev/s from 142.5, 262.5 or
# 382.5 rev/s: the answer repeats every lcm(30, 24) = 120 rev/s. A fast machine, a turbine or a drill, can easily turn
# faster than that. A third clip at 25 fps stretches the unambiguous range to 600 rev/s. Why, which third frame
# rate helps and which one does not, and what happens to the noise?
#
# **Plan.** (1) the speeds that sit on all three ladders, (2) why the range is the lcm of all rates and
# when a third rate does not help, (3) choosing the third rate, (4) recovery from noisy clips with
# three numbers, and what the extra clip does to the uncertainty.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


def signed_alias(f, fs):
    """Apparent speed of a wheel turning f rev/s filmed at fs fps, in (-fs/2, fs/2] (negative = looks backwards)."""
    return f - fs * math.floor(f / fs + 0.5)


def candidates(a, fs, f_lo, f_hi):
    """Speeds in [f_lo, f_hi] that look like a at frame rate fs: the rungs a + k fs."""
    k0 = math.ceil((f_lo - a) / fs - 1e-9)
    k1 = math.floor((f_hi - a) / fs + 1e-9)
    return [a + k * fs for k in range(k0, k1 + 1)]


# %% [markdown]
# ## Step 1: the speeds that sit on every ladder
# Each clip allows a ladder of rungs a + k fs. A speed that is on all the ladders at once is compatible
# with all the clips. With two clips there are several of them; with a third, almost all disappear.

# %%
def common_speeds(apparents, rates, f_lo=0.0, f_hi=400.0, tol=1e-6):
    """Speeds in [f_lo, f_hi] on every ladder (within tol). One entry means the answer is unique."""
    if len(apparents) != len(rates) or len(rates) < 2:
        raise ValueError("give one apparent speed per frame rate, and at least two clips")
    ladders = [candidates(a, fs, f_lo, f_hi) for a, fs in zip(apparents, rates)]
    out = []
    for x in ladders[0]:
        if all(any(abs(x - y) <= tol for y in lad) for lad in ladders[1:]):
            out.append(round(x, 6))
    return out


# %% [markdown]
# ## Step 2: the range is the lcm of all the rates
# A wrong speed f' = f + d looks the same as f on a clip at fs when d is a whole number of frame
# rates, d = k fs. It looks the same on all the clips only when d is a common multiple of all the rates: d = k lcm(fs1, fs2, fs3). So the
# unambiguous range is the least common multiple of *all* the rates. A third rate adds
# nothing when it divides the lcm of the other two (20, 24, 30, 40 or 60 fps next to 30 and 24, whose lcm is 120).

# %%
def unambiguous_range(rates):
    """With whole-number rates and signed measurements, f and f + this look the same on every clip."""
    if any(int(round(r)) != r or r <= 0 for r in rates):
        raise ValueError("this rule needs positive whole-number frame rates")
    return int(np.lcm.reduce([int(r) for r in rates]))


def third_rate_helps(rate_a, rate_b, rate_c):
    """True when a third clip at rate_c extends the range of the pair (rate_a, rate_b)."""
    return unambiguous_range([rate_a, rate_b, rate_c]) > unambiguous_range([rate_a, rate_b])


def rate_table(rate_a, rate_b, third_rates):
    """(third rate, range of the three rates, does it help) for each candidate third rate."""
    return [(r, unambiguous_range([rate_a, rate_b, r]), third_rate_helps(rate_a, rate_b, r)) for r in third_rates]


# %% [markdown]
# ## Step 3: noisy clips and three numbers
# With noise (Session 4), pick the set of rungs, one per ladder, whose members are closest to each other:
# the score of a set is the sum of squared distances of the rungs from their mean, and the
# answer is the mean. For equal noise on every clip this is the least-squares answer. Its error is the mean of n
# independent errors, so the standard deviation is sigma / sqrt(n): three clips give 0.17 rev/s where two give 0.21 rev/s for sigma = 0.3, and the chance of being
# within t is erf(t sqrt(n) / (sigma sqrt 2)). As in Session 4, the rungs are searched 4 sigma beyond the range
# and the answer is clipped back into it.

# %%
MAX_SETS = 400_000


def rung_sets(apparents, rates, f_lo, f_hi, margin=0.0):
    """All sets of one rung per ladder: (rungs array [n_sets, n_clips])."""
    ladders = [np.array(candidates(a, fs, f_lo - margin, f_hi + margin)) for a, fs in zip(apparents, rates)]
    if any(len(lad) == 0 for lad in ladders):
        raise ValueError("a ladder has no rung inside the range")
    if np.prod([len(lad) for lad in ladders], dtype=float) > MAX_SETS:
        raise ValueError("too many rung sets: narrow the range")
    grid = np.meshgrid(*ladders, indexing="ij")
    return np.stack([g.ravel() for g in grid], axis=1)


def recover_noisy_n(apparents, rates, sigma, f_lo=5.0, f_hi=399.0):
    """Most likely true speed from n >= 2 noisy apparent speeds (equal noise sigma), with an uncertainty.
    Returns a dict: f (rev/s), sd (rev/s), margin (how many sigma the best set beats the runner-up by)."""
    if sigma < 0:
        raise ValueError("sigma must not be negative")
    if f_hi <= f_lo or len(apparents) != len(rates) or len(rates) < 2 or min(rates) <= 0:
        raise ValueError("need f_hi > f_lo, positive rates and one apparent speed per rate (at least two)")
    sets = rung_sets(apparents, rates, f_lo, f_hi, 4.0 * sigma)
    mean = sets.mean(axis=1)
    spread = ((sets - mean[:, None]) ** 2).sum(axis=1)
    order = np.argsort(spread)
    runner = spread[order[1]] if len(order) > 1 else math.inf
    margin = (math.sqrt(runner) - math.sqrt(spread[order[0]])) / sigma if sigma > 0 else math.inf
    return {"f": float(min(max(mean[order[0]], f_lo), f_hi)), "sd": sigma / math.sqrt(len(rates)), "margin": float(margin)}


def predicted_within(sigma, n_clips, tol=0.5):
    """Chance that the mean of the true rungs is within tol of the truth: erf(tol sqrt(n) / (sigma sqrt 2))."""
    return 1.0 if sigma <= 0 else math.erf(tol * math.sqrt(n_clips) / (sigma * math.sqrt(2.0)))


def run_trials(rates, sigma, n_trials=1000, seed=0, f_lo=5.0, f_hi=399.0, tol=0.5):
    """Share of trials (true speed uniform in the range) in which the recovery is within tol of the truth."""
    rng = np.random.default_rng(seed)
    good = 0
    for _ in range(n_trials):
        f = rng.uniform(f_lo, f_hi)
        a = [signed_alias(f, r) + rng.normal(0.0, sigma) for r in rates]
        good += abs(recover_noisy_n(a, rates, sigma, f_lo, f_hi)["f"] - f) <= tol
    return good / n_trials


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f_true = 22.5
    a30, a24, a25 = (signed_alias(f_true, r) for r in (30, 24, 25))
    print(f"apparent speeds of {f_true} rev/s: {a30} (30 fps), {a24} (24 fps), {a25} (25 fps)")
    print("two clips (30, 24), range 0 to 400:", common_speeds([a30, a24], [30, 24]))
    print("three clips (30, 24, 25), range 0 to 400:", common_speeds([a30, a24, a25], [30, 24, 25]))
    print("three clips, range 0 to 1000:", common_speeds([a30, a24, a25], [30, 24, 25], 0, 1000), "(repeats at 22.5 + 600)")
    print("\nthird rate next to 30 and 24 fps: range of the three rates")
    for r, rng_, helps in rate_table(30, 24, [20, 24, 25, 26, 27, 29, 36, 40, 45, 50]):
        print(f"  {r} fps: range {rng_:5d} rev/s, {'helps' if helps else 'no help'}")
    print("\nshare within 0.5 rev/s, true speed uniform 5 to 399 rev/s, 600 trials:")
    sig_list = [0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0]
    two = [run_trials([30, 24], s, 600) for s in sig_list]
    three = [run_trials([30, 24, 25], s, 600) for s in sig_list]
    print(f"{'noise':>6s} {'two clips':>10s} {'three clips':>12s} {'limit (3)':>10s}")
    for s, a, b in zip(sig_list, two, three):
        print(f"{s:6.1f} {a:10.3f} {b:12.3f} {predicted_within(s, 3):10.3f}")

    fig, axs = plt.subplots(2, 2, figsize=(11.5, 8))
    ax = axs[0, 0]
    rows = [(30, a30, "tab:blue"), (24, a24, "tab:orange"), (25, a25, "tab:green")]
    for i, (r, a, c) in enumerate(rows):
        xs = candidates(a, r, 0, 640)
        ax.plot(xs, np.full(len(xs), 2 - i), "|", ms=16, mew=2.5, color=c)
    ax.axvline(f_true, color="k", ls=":")
    ax.axvline(f_true + 600, color="k", ls=":")
    ax.set_yticks([2, 1, 0])
    ax.set_yticklabels(["30 fps", "24 fps", "25 fps"])
    ax.set_xlim(0, 640)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xlabel("candidate true speed (rev/s)")
    ax.set_title("Three ladders: 22.5 and 622.5 are the only rungs they share below 640", fontsize=9)
    ax = axs[0, 1]
    thirds = list(range(20, 61))
    tab = rate_table(30, 24, thirds)
    ax.bar(thirds, [t[1] for t in tab], color=["tab:green" if t[2] else "tab:red" for t in tab])
    ax.axhline(400, color="k", ls="--", lw=1)
    ax.set_yscale("log")
    ax.set_xlabel("third frame rate (fps), the first two are 30 and 24")
    ax.set_ylabel("unambiguous range (rev/s)")
    ax.set_title("Red: the third rate divides 120 and adds nothing (dashed: 400 rev/s)", fontsize=9)
    ax = axs[1, 0]
    ax.plot(sig_list, two, "o-", color="tab:red", label="two clips (30, 24)")
    ax.plot(sig_list, three, "s-", color="tab:blue", label="three clips (30, 24, 25)")
    ax.plot(sig_list, [predicted_within(s, 3) for s in sig_list], "k:", label="limit for three clips")
    ax.axhline(0.95, color="gray", ls="--")
    ax.set_xlabel("noise on each apparent speed (rev/s)")
    ax.set_ylabel("share within 0.5 rev/s")
    ax.set_title("True speed uniform from 5 to 399 rev/s, 600 trials per point", fontsize=9)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax = axs[1, 1]
    rng2 = np.random.default_rng(2)
    e2, e3 = [], []
    for _ in range(1500):
        f = rng2.uniform(5, 59)
        a = [signed_alias(f, r) + rng2.normal(0, 0.5) for r in (30, 24, 25)]
        e3.append(recover_noisy_n(a, [30, 24, 25], 0.5, 5, 59)["f"] - f)
        e2.append(recover_noisy_n(a[:2], [30, 24], 0.5, 5, 59)["f"] - f)
    bins = np.linspace(-1.6, 1.6, 49)
    ax.hist(e2, bins=bins, alpha=0.6, color="tab:red", label=f"two clips, sd {np.std(e2):.3f}")
    ax.hist(e3, bins=bins, alpha=0.6, color="tab:blue", label=f"three clips, sd {np.std(e3):.3f}")
    ax.set_xlabel("recovered minus true speed (rev/s), range 5 to 59, sigma = 0.5")
    ax.set_ylabel("trials (of 1500)")
    ax.set_title("A third clip also lowers the noise: sd falls by sqrt(2/3)", fontsize=9)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "third_clip.png", dpi=110)
    print("saved figure in", OUT)

# %% [markdown]
# ## Where this stops
# Whole-number frame rates, signed apparent speeds measured with equal Gaussian noise, one steady
# speed. Real cameras drift in frame rate, and a rate that is only nominally 24 or 25 makes the
# rungs slide apart at large k, which limits how far the lcm range is usable. The more clips, the more frames
# you must film and the more accurate the rates must be known: the range grows with the rates you add, but each
# clip costs time. A fan with several identical blades, a speed that changes and a rolling shutter are the later milestones of the
# roadmap.
