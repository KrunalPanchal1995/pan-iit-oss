"""Session 3 (Level 3): Monte Carlo simulation, its error, and when it fails.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: Monte Carlo simulation, its error, and when it fails
# **A. Real-world problem.** When counting is too hard we can *simulate*: play the game
# thousands of times on a computer and count how often the event happens. How close is the
# answer, how many plays do we need, and why can nobody simulate their way to a lottery jackpot?
#
# *Education about chance only. The game and prizes are made-up; this is not betting advice.*
#
# **Plan.** (1) estimate a probability by simulation, (2) measure the error with the standard
# error, (3) look at the law of large numbers and the gambler's fallacy, (4) check a fair
# game, (5) see the 6-of-49 lottery break simulation.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

LOTTERY_TOTAL = math.comb(49, 6)      # 13983816 equally likely draws


# %% [markdown]
# ## Step 1: estimate by simulation and compare with the exact value
# Monte Carlo idea: p_hat = (trials where the event happened) / N. A *seeded* generator
# repeats exactly, so anyone can reproduce your number.

# %%
def estimate_sum_probability(target, n, seed=1):
    """Estimate P(sum of two dice >= target) from n simulated rolls."""
    rng = np.random.default_rng(seed)
    s = rng.integers(1, 7, size=n) + rng.integers(1, 7, size=n)
    return float(np.mean(s >= target))


def exact_sum_at_least(target):
    """Exact P(sum of two dice >= target) by counting the 36 outcomes."""
    good = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b >= target)
    return good / 36


def estimate_birthday(people, trials, seed=1):
    """Estimate P(at least two of `people` share a birthday) by simulation."""
    rng = np.random.default_rng(seed)
    days = np.sort(rng.integers(0, 365, size=(trials, people)), axis=1)
    return float(np.mean((np.diff(days, axis=1) == 0).any(axis=1)))


# %% [markdown]
# ## Step 2: the error of a simulation
# The estimate is itself random. For N independent trials of an event with probability p,
# its typical error (the standard error) is
#
#     SE = sqrt(p (1 - p) / N)
#
# About 95 percent of estimates fall within 1.96 SE of the truth. To get a 95 percent half-width
# of at most e, we need N >= 1.96^2 p (1 - p) / e^2. Ten times the accuracy costs 100 times the trials.

# %%
def standard_error(p, n):
    return math.sqrt(p * (1 - p) / n)


def trials_needed(p, half_width, z=1.96):
    """Smallest N so that z * SE <= half_width."""
    if half_width <= 0:
        raise ValueError("half_width must be positive")
    return math.ceil(z * z * p * (1 - p) / half_width ** 2)


def running_estimate(target, n, seed=1):
    """Estimate after 1, 2, ..., n rolls (array of length n)."""
    rng = np.random.default_rng(seed)
    s = rng.integers(1, 7, size=n) + rng.integers(1, 7, size=n)
    return np.cumsum(s >= target) / np.arange(1, n + 1)


# %% [markdown]
# ## Step 3: law of large numbers, and the gambler's fallacy
# The law of large numbers says the *fraction* settles near p. It does not say the counts
# even out: after a run of heads the next flip is still 50:50.

# %%
def next_flip_after_streak(n, streak=5, seed=1):
    """Among n fair coin flips, the fraction of heads right after `streak` heads in a row."""
    rng = np.random.default_rng(seed)
    h = rng.integers(0, 2, size=n).astype(bool)
    run = np.ones(n - streak, dtype=bool)
    for k in range(streak):
        run &= h[k:n - streak + k]
    nxt = h[streak:]
    return float(nxt[run].mean()), int(run.sum())


# %% [markdown]
# ## Step 4: a fair game, checked by simulation
# Pay `price`, roll two dice, win a gross `payout` if the sum is at least 9 (probability 10/36).
# Expected net gain = p x payout - price. It is 0 when payout = price / p.

# %%
WIN_AT_LEAST = 9


def fair_payout(price, p):
    return price / p


def simulate_game(price, payout, n, seed=1):
    """Average net gain per play and its standard error over n simulated plays."""
    rng = np.random.default_rng(seed)
    s = rng.integers(1, 7, size=n) + rng.integers(1, 7, size=n)
    net = np.where(s >= WIN_AT_LEAST, payout - price, -price).astype(float)
    return float(net.mean()), float(net.std(ddof=1) / math.sqrt(n))


# %% [markdown]
# ## Step 5: the lottery, and why simulation fails
# A 6-of-49 ticket wins the jackpot with probability 1 / C(49, 6) = 1 / 13,983,816.
# With an illustrative ticket price and jackpot the expected loss per ticket is
# price - jackpot / 13983816 (smaller prizes ignored). To see a jackpot even once we
# would need about 14 million simulated draws, and ten times that to estimate p to within 30 percent.

# %%
def lottery_expected_loss(price, jackpot):
    """Expected loss per ticket if only the jackpot is counted."""
    return price - jackpot / LOTTERY_TOTAL


def simulate_lottery(draws, seed=1):
    """Number of simulated draws (out of `draws`) that equal the fixed ticket 1,2,3,4,5,6."""
    rng = np.random.default_rng(seed)
    hits, chunk = 0, 50000
    for start in range(0, draws, chunk):
        m = min(chunk, draws - start)
        picked = np.argpartition(rng.random((m, 49)), 6, axis=1)[:, :6] + 1
        hits += int(np.sum(np.all(np.sort(picked, axis=1) == np.arange(1, 7), axis=1)))
    return hits


def draws_for_relative_error(p, rel):
    """Trials so that the standard error is rel x p."""
    return math.ceil((1 - p) / (p * rel ** 2))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    p = exact_sum_at_least(9)
    print(f"exact P(sum >= 9) = 10/36 = {p:.4f}")
    for n in (100, 10000, 1000000):
        est = estimate_sum_probability(9, n)
        print(f"N = {n:7d}: estimate {est:.4f}, error {est - p:+.4f}, standard error {standard_error(p, n):.4f}")
    print("trials for 95% half-width 0.005 at p = 10/36:", trials_needed(p, 0.005))
    print(f"birthday, 23 people, 100000 trials: {estimate_birthday(23, 100000):.4f} (exact 0.5073)")
    frac, cnt = next_flip_after_streak(2000000)
    print(f"heads after 5 heads in a row: {frac:.4f} (from {cnt} streaks)")
    print("lottery total:", LOTTERY_TOTAL)
    print("expected loss on a Rs 100 ticket with a Rs 10 crore jackpot:", round(lottery_expected_loss(100, 1e8), 2))
    print("simulated jackpot hits in 200000 draws:", simulate_lottery(200000))
    print("draws needed for 30% relative error:", draws_for_relative_error(1 / LOTTERY_TOTAL, 0.3))

    # five seeded runs with the 95 percent error band
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ns = np.unique(np.logspace(1, 5, 40).astype(int))
    runs = np.array([[estimate_sum_probability(9, int(n), seed=s) for n in ns] for s in range(1, 6)])
    for r in runs:
        ax.semilogx(ns, r, alpha=0.6, lw=1)
    se = np.array([standard_error(p, n) for n in ns])
    ax.fill_between(ns, p - 1.96 * se, p + 1.96 * se, color="gray", alpha=0.2, label="exact +/- 1.96 SE")
    ax.axhline(p, color="red", ls="--", label="exact 10/36")
    ax.set_xlabel("number of simulated rolls N")
    ax.set_ylabel("estimate of P(sum >= 9)")
    ax.set_title("Five seeded runs inside the error band")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "error_band.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    pp = np.linspace(0.001, 1, 400)
    ax2.loglog(pp, [trials_needed(q, 0.01) for q in pp[:-1]] + [np.nan], label="half-width 0.01")
    ax2.loglog(pp, [trials_needed(q, 0.001) for q in pp[:-1]] + [np.nan], label="half-width 0.001")
    ax2.set_xlabel("true probability p")
    ax2.set_ylabel("trials N for 95 percent accuracy")
    ax2.set_title("Ten times the accuracy costs 100 times the trials")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "trials_needed.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Then try the mini-project in the README.
