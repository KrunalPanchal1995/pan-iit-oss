"""Session 4 (Level 3): recover the true speed from noisy apparent speeds, with an uncertainty.

Educational model only. Not a measurement method for any real machine or safety decision.
Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: noise-proof recovery
# **A. Real-world problem.** In Session 3 the apparent speeds were exact, and the true speed was the
# one number that sat on both ladders. Real measurements are noisy: a marker found a few pixels off, a clip
# of only a few frames. With 0.3 rev/s of noise on both apparent speeds the Session 3 rule, which
# demands a match within 0.3 rev/s, answers correctly only about half the time. We
# build a recovery that scores every pair of ladder rungs, picks the best pair, and reports an
# uncertainty, and then we measure how often it is right.
#
# **Plan.** (1) where the noise comes from, (2) why exact matching fails, (3) score the pairs of
# rungs, (4) the uncertainty, (5) 2000 trials against the roadmap line, (6) how much noise a pair
# of frame rates can survive.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
F_LO, F_HI = 5.0, 59.0       # the speeds we expect (rev/s)


def signed_alias(f, fs):
    """Apparent speed of a wheel turning f rev/s filmed at fs fps, in (-fs/2, fs/2] (negative = looks backwards)."""
    return f - fs * math.floor(f / fs + 0.5)


# %% [markdown]
# ## Step 1: where the noise comes from
# A clip of `n` frames gives `n` marker angles, and each angle is a little wrong (standard deviation
# `angle_sd`, in radians: a marker found 1 pixel off on a wheel of radius 20 pixels is 0.05 rad). The
# apparent speed is the mean turn per frame, and the mean of the turns telescopes: the errors in the
# middle cancel and only the first and the last angle matter. So the noise of the apparent speed is
#
#     sigma = fs * sqrt(2) * angle_sd / (2 pi (n - 1)),
#
# which falls as 1 / (n - 1): a longer clip is much better than a better marker. We check this by
# simulation. (The roadmap's 0.3 rev/s is, for example, a 5 frame clip with the marker 3.6 pixels off.)

# %%
def speed_noise(angle_sd, n_frames, fs):
    """Standard deviation (rev/s) of the apparent speed from n_frames marker angles with errors angle_sd (rad)."""
    if n_frames < 2:
        raise ValueError("a clip needs at least 2 frames to measure a speed")
    return fs * math.sqrt(2.0) * angle_sd / (2 * math.pi * (n_frames - 1))


def measured_speed(f, fs, n_frames, angle_sd, rng):
    """Apparent speed (rev/s) measured as in Session 3 from marker angles with random errors."""
    ang = 2 * np.pi * f * np.arange(n_frames) / fs + rng.normal(0.0, angle_sd, n_frames)
    steps = np.angle(np.exp(1j * np.diff(ang)))
    return float(np.angle(np.mean(np.exp(1j * steps))) / (2 * np.pi) * fs)


# %% [markdown]
# ## Step 2: why exact matching fails
# Session 3 lists the speeds that look like `a` on each clip (a ladder with rungs `fs` apart) and
# accepts a pair of rungs closer than `tol`. With noise `sigma` on each apparent speed, the two rungs of
# the true pair differ by n1 - n2, which has standard deviation sqrt(2) sigma = 0.42 rev/s for sigma = 0.3. A
# tolerance of 0.3 lets only about half of the true pairs through; the rest get no answer.

# %%
def candidates(a, fs, f_lo, f_hi):
    """Speeds in [f_lo, f_hi] that look like a at frame rate fs: the rungs a + k fs."""
    k0 = math.ceil((f_lo - a) / fs - 1e-9)
    k1 = math.floor((f_hi - a) / fs + 1e-9)
    return [a + k * fs for k in range(k0, k1 + 1)]


def recover_exact(a1, fs1, a2, fs2, f_lo=F_LO, f_hi=F_HI, tol=0.3):
    """The Session 3 rule: rung pairs closer than tol (list of speeds, possibly empty)."""
    c2 = candidates(a2, fs2, f_lo, f_hi)
    out = []
    for x in candidates(a1, fs1, f_lo, f_hi):
        near = [y for y in c2 if abs(x - y) <= tol]
        if near:
            out.append((x + near[0]) / 2.0)
    return out


def noisy_apparent(f, fs, sigma, rng):
    """Signed apparent speed plus Gaussian measurement noise (rev/s)."""
    return signed_alias(f, fs) + rng.normal(0.0, sigma)


# %% [markdown]
# ## Step 3: score every pair of rungs
# Instead of a yes/no tolerance, give every pair of rungs (c1 from clip 1, c2 from clip 2) a score,
# its gap |c1 - c2|, and choose the pair with the smallest gap. For equal noise on both clips the
# most likely true speed *for that pair* is the middle of the two rungs, (c1 + c2) / 2, which is
# the least-squares answer. Two details: the rungs are searched a few sigma beyond the expected
# range, because noise can push a rung of a speed near the edge outside it (the final answer is
# clipped back into the range), and the second-best gap tells how safe the choice was.

# %%
def rung_pairs(a1, fs1, a2, fs2, f_lo, f_hi, margin=0.0):
    """All pairs of rungs as (gap, middle), sorted by gap. Rungs are searched in [f_lo - margin, f_hi + margin]."""
    c1 = candidates(a1, fs1, f_lo - margin, f_hi + margin)
    c2 = candidates(a2, fs2, f_lo - margin, f_hi + margin)
    return sorted((abs(x - y), (x + y) / 2.0) for x in c1 for y in c2)


def recover_noisy(a1, fs1, a2, fs2, sigma, f_lo=F_LO, f_hi=F_HI):
    """Most likely true speed from noisy apparent speeds, with an uncertainty.

    Returns a dict: f (rev/s), sd (one standard deviation, rev/s), margin (how many sigma
    the best pair beats the runner-up by; below 3 the choice of pair is shaky)."""
    if sigma < 0:
        raise ValueError("sigma must not be negative")
    if f_hi <= f_lo or fs1 <= 0 or fs2 <= 0:
        raise ValueError("need f_hi > f_lo and positive frame rates")
    pairs = rung_pairs(a1, fs1, a2, fs2, f_lo, f_hi, margin=4.0 * sigma)
    if not pairs:
        raise ValueError("no pair of rungs inside the range")
    best = pairs[0]
    runner = pairs[1][0] if len(pairs) > 1 else math.inf
    s = sigma * math.sqrt(2.0)
    margin = (runner - best[0]) / s if s > 0 else math.inf
    return {"f": min(max(best[1], f_lo), f_hi), "sd": sigma / math.sqrt(2.0), "margin": margin}


# %% [markdown]
# ## Step 4: the uncertainty
# The two rungs of the true pair carry independent errors n1 and n2, so their middle has error
# (n1 + n2) / 2 with standard deviation sigma / sqrt(2) = 0.21 rev/s for sigma = 0.3. That is the best any
# recovery can do with these two numbers, whatever the rule: adding an error band of +-2 sd gives a 95
# percent interval, and the chance of being within a tolerance t is erf(t / sigma). A *wrong* pair
# only beats the true pair when |n1 - n2| exceeds half the gap between neighbouring pairs, and for whole-number
# rates that gap is gcd(fs1, fs2) (6 for 30 and 24 fps), which sets how much noise a pair of rates survives.

# %%
def predicted_within(sigma, tol=0.5):
    """Chance that the middle of the true pair is within tol of the true speed: erf(tol / sigma)."""
    return 1.0 if sigma <= 0 else math.erf(tol / sigma)


def wrong_pair_probability(sigma, fs1, fs2):
    """Upper bound for the chance that a wrong pair of rungs wins: P(|n1 - n2| > g / 2) with g = gcd(fs1, fs2)."""
    g = math.gcd(int(round(fs1)), int(round(fs2)))
    if sigma <= 0:
        return 0.0
    return math.erfc(g / 2.0 / (sigma * 2.0))


def run_trials(rule, sigma, n_trials=2000, seed=0, fs1=30.0, fs2=24.0, f_lo=F_LO, f_hi=F_HI, tol=0.5):
    """Fraction of trials in which the rule returns a speed within `tol` of the true one, and the fraction that got any answer.
    rule: 'exact' (Session 3, tol 0.3), 'wide' (exact matching with tolerance 1.3), or 'pairs' (Step 3)."""
    if rule not in ("exact", "wide", "pairs"):
        raise ValueError("rule must be 'exact', 'wide' or 'pairs'")
    rng = np.random.default_rng(seed)
    good = answered = 0
    for _ in range(n_trials):
        f = rng.uniform(f_lo, f_hi)
        a1, a2 = noisy_apparent(f, fs1, sigma, rng), noisy_apparent(f, fs2, sigma, rng)
        if rule == "pairs":
            est = [recover_noisy(a1, fs1, a2, fs2, sigma, f_lo, f_hi)["f"]]
        else:
            est = recover_exact(a1, fs1, a2, fs2, f_lo, f_hi, 0.3 if rule == "exact" else 1.3)
        if est:
            answered += 1
            good += abs(est[0] - f) <= tol
    return good / n_trials, answered / n_trials


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(4)
    print("noise of the apparent speed from marker errors (fs = 30):")
    for n, sd in ((5, 0.18), (10, 0.05), (40, 0.05)):
        mc = np.std([measured_speed(11.3, 30, n, sd, rng) for _ in range(4000)])
        print(f"  {n:2d} frames, marker error {sd} rad: formula {speed_noise(sd, n, 30):.3f}, simulation {mc:.3f} rev/s")
    print("\n2000 trials, true speed uniform 5 to 59 rev/s, 30 and 24 fps:")
    print(f"{'noise':>6s}  {'exact (S3)':>10s} {'wide tol':>9s} {'best pair':>10s}  {'theory':>7s}")
    sigmas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
    res = {r: [run_trials(r, s)[0] for s in sigmas] for r in ("exact", "wide", "pairs")}
    for i, s in enumerate(sigmas):
        print(f"{s:6.1f}  {res['exact'][i]:10.3f} {res['wide'][i]:9.3f} {res['pairs'][i]:10.3f}  {predicted_within(s):7.3f}")

    # one noisy trial
    f_true, sigma = 22.5, 0.3
    a1, a2 = noisy_apparent(f_true, 30, sigma, rng), noisy_apparent(f_true, 24, sigma, rng)
    out = recover_noisy(a1, 30, a2, 24, sigma)
    print(f"\none trial: measured {a1:.2f} and {a2:.2f}, recovered {out['f']:.2f} +- {out['sd']:.2f} (true {f_true}), margin {out['margin']:.1f} sigma")

    fig, axs = plt.subplots(2, 2, figsize=(11.5, 8))
    ax = axs[0, 0]
    c1, c2 = candidates(a1, 30, 0, 100), candidates(a2, 24, 0, 100)
    ax.plot(c1, np.ones(len(c1)), "o", color="tab:blue", ms=9, label="clip at 30 fps")
    ax.plot(c2, np.zeros(len(c2)), "s", color="tab:orange", ms=9, label="clip at 24 fps")
    ax.axvline(f_true, color="k", ls=":", label="true speed")
    ax.axvline(out["f"], color="tab:red", lw=2, label="best pair")
    ax.axvspan(out["f"] - 2 * out["sd"], out["f"] + 2 * out["sd"], color="tab:red", alpha=0.2)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["24 fps", "30 fps"])
    ax.set_ylim(-0.6, 1.8)
    ax.set_xlabel("candidate true speed (rev/s)")
    ax.set_title("Noisy ladders: the closest pair is still the true one", fontsize=10)
    ax.legend(fontsize=7, loc="upper right")
    ax = axs[0, 1]
    rr = np.random.default_rng(1)
    errs = []
    for _ in range(2000):
        f = rr.uniform(F_LO, F_HI)
        b1, b2 = noisy_apparent(f, 30, 0.3, rr), noisy_apparent(f, 24, 0.3, rr)
        errs.append(recover_noisy(b1, 30, b2, 24, 0.3)["f"] - f)
    errs = np.array(errs)
    ax.hist(errs, bins=np.linspace(-1.2, 1.2, 49), color="tab:blue", alpha=0.8)
    ax.axvline(-0.5, color="tab:red", ls="--")
    ax.axvline(0.5, color="tab:red", ls="--", label="+-0.5 rev/s")
    ax.set_xlabel("recovered minus true speed (rev/s)")
    ax.set_ylabel("trials (of 2000)")
    ax.set_title(f"Error at sigma = 0.3: sd {errs.std():.3f} (theory 0.212), {np.mean(np.abs(errs) <= 0.5):.1%} within 0.5", fontsize=9)
    ax.legend(fontsize=8)
    ax = axs[1, 0]
    ax.plot(sigmas, res["exact"], "o-", color="tab:red", label="exact match, tol 0.3 (Session 3)")
    ax.plot(sigmas, res["wide"], "s-", color="tab:orange", label="exact match, tol 1.3")
    ax.plot(sigmas, res["pairs"], "^-", color="tab:blue", label="best pair (this session)")
    ax.plot(sigmas, [predicted_within(s) for s in sigmas], "k:", label="limit: erf(0.5 / sigma)")
    ax.axhline(0.95, color="gray", ls="--")
    ax.set_xlabel("noise on each apparent speed (rev/s)")
    ax.set_ylabel("share of trials within 0.5 rev/s")
    ax.set_title("2000 trials per point", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    ax = axs[1, 1]
    partners = list(range(18, 30))
    rate = [run_trials("pairs", 0.3, 800, fs2=float(p))[0] for p in partners]
    ax.bar(partners, rate, color=["tab:green" if r >= 0.95 else "tab:red" for r in rate])
    for p, r in zip(partners, rate):
        ax.text(p, r + 0.01, f"g{math.gcd(30, p)}", ha="center", fontsize=7)
    ax.axhline(0.95, color="gray", ls="--")
    ax.set_ylim(0.6, 1.05)
    ax.set_xlabel("second frame rate (fps), first is 30; g = gcd")
    ax.set_ylabel("share within 0.5 rev/s at sigma = 0.3")
    ax.set_title("Close rates reach far but tolerate little noise (29 fps: g = 1)", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "noise_proof.png", dpi=110)
    print("saved figure in", OUT)

# %% [markdown]
# ## Where this stops
# Gaussian noise of one known size on both apparent speeds, no systematic error, and one steady speed.
# The noise size sigma has to be known or estimated (from the scatter of repeated clips); a wrong
# sigma changes the margin and the margin alone, not the pair that is chosen. A frame rate
# that is not exactly its nominal value, a speed that changes during the clip or a camera with
# rolling shutter (the later sessions of the roadmap) break the model. And no rule beats
# sigma / sqrt(2): to be within 0.5 rev/s in 99 percent of the trials you need sigma of about 0.2 or less.
