"""Session 1 (Level 1): a network is a flexible curve, and a physics law can bend it into shape.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a flexible curve that can also obey a law
# **A. Real-world problem.** A cooling cup of tea is measured six times in its first minute.
# The readings are a little noisy. You must predict the temperature excess for the whole next
# minute too. A flexible curve can pass near all six readings and still swing wildly where you
# have no readings. But you also know a law: the excess temperature falls at a rate proportional
# to itself, `u' = -u` (we use scaled units). Can a curve be asked to obey the law as well as
# the data?
#
# **Plan.** (1) build a flexible curve from "tanh bumps", (2) fit it to the six readings, (3) add
# the law as extra rows in the same fit, (4) measure the difference.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

STEEP = 3.0                                    # how sharp each bump is
DATA_X = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])           # times of the six readings
NOISE = np.array([0.02, -0.03, 0.025, -0.02, 0.03, -0.025])   # fixed "measurement errors"
DATA_Y = np.exp(-DATA_X) + NOISE                # the noisy readings


# %% [markdown]
# ## Step 1: one bump, then many bumps
# `tanh(s)` is a smooth step: it is -1 far to the left, +1 far to the right and passes through
# 0 at s = 0. Shift it with `x - centre` and sharpen it with STEEP. A "unit" of a network is one
# such bump; the curve is a weighted sum of units plus a constant:
#
#     u(x) = c_1 * tanh(STEEP (x - m_1)) + ... + c_H * tanh(STEEP (x - m_H)) + c_0
#
# Here the centres m_j are spread evenly over 0 to 2 and we only choose the weights c.
# The slope of the curve is also a sum: d tanh(s)/ds = 1 - tanh(s)^2.

# %%
def features(x, n_units):
    """Return (F, D): the bump values and their slopes at every x. The last column is the constant."""
    x = np.asarray(x, dtype=float)
    centres = np.linspace(0.0, 2.0, n_units)
    th = np.tanh(STEEP * (x[:, None] - centres))
    ones = np.ones((len(x), 1))
    F = np.hstack([th, ones])
    D = np.hstack([STEEP * (1.0 - th ** 2), np.zeros((len(x), 1))])
    return F, D


# %% [markdown]
# ## Step 2: fit the six readings (data only)
# We choose weights c that make the curve close to the readings, by least squares: minimise
# the sum of (curve - reading)^2. A tiny penalty on the size of c (the "ridge", 0.001) keeps
# the sums sensible when there are more weights than readings.

# %%
RIDGE = 1e-3


def fit(n_units, lam, n_law=21):
    """Weights c. lam = 0: data only. lam > 0: also ask u' + u = 0 at n_law points on [0, 2]."""
    F, _ = features(DATA_X, n_units)
    A = F.T @ F
    b = F.T @ DATA_Y
    if lam > 0:
        xs = np.linspace(0.0, 2.0, n_law)
        Fl, Dl = features(xs, n_units)
        R = Dl + Fl                    # row k gives u'(x_k) + u(x_k), which the law says is 0
        A = A + lam * (R.T @ R)
    A = A + RIDGE * np.eye(n_units + 1)
    return np.linalg.solve(A, b)


# %% [markdown]
# ## Step 3: add the law
# The law `u' = -u` says that at every time, slope + value = 0. We add "law rows" at 21 points
# between 0 and 2 (the second minute included, where we have no readings!). `lam` says how
# strongly we insist on the law compared with the data. Because the curve is a sum of bumps,
# slope + value is again a weighted sum, so the whole problem is still one linear fit.

# %%
def curve(c, x):
    F, _ = features(x, len(c) - 1)
    return F @ c


def law_residual(c, x):
    """u'(x) + u(x): zero everywhere if the curve obeys the law."""
    F, D = features(x, len(c) - 1)
    return (D + F) @ c


def rms_error(c, n_points=201):
    """Root-mean-square distance from the true curve exp(-x) over the whole range 0 to 2."""
    x = np.linspace(0.0, 2.0, n_points)
    return float(np.sqrt(np.mean((curve(c, x) - np.exp(-x)) ** 2)))


# %% [markdown]
# ## Step 4: measure
# The "true" answer exp(-x) is known here, so we can score both fits over the whole range
# 0 to 2, not only where the readings are.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    H = 12
    c_plain, c_law = fit(H, 0.0), fit(H, 1.0)
    print(f"{H} bumps, data only:    rms error over 0..2 = {rms_error(c_plain):.4f}")
    print(f"{H} bumps, data + law:   rms error over 0..2 = {rms_error(c_law):.4f}")
    xs = np.linspace(0, 2, 201)
    print(f"largest |u' + u| over 0..2: data only {np.abs(law_residual(c_plain, xs)).max():.3f}, "
          f"with law {np.abs(law_residual(c_law, xs)).max():.3f}")

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(xs, np.exp(-xs), "k--", label="true curve exp(-x)")
    ax.plot(xs, curve(c_plain, xs), color="tab:red", label="fit to readings only")
    ax.plot(xs, curve(c_law, xs), color="tab:green", label="fit to readings + law u' = -u")
    ax.plot(DATA_X, DATA_Y, "ko", label="six noisy readings")
    ax.set_ylim(-1.5, 2.0)
    ax.set_xlabel("time x (scaled units)")
    ax.set_ylabel("temperature excess u (scaled units)")
    ax.set_title("A flexible curve with and without the law")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fit_with_without_law.png", dpi=120)

    # the bumps behind one fit
    F, _ = features(xs, 6)
    c6 = fit(6, 1.0)
    fig2, ax2 = plt.subplots(figsize=(7, 4.2))
    for j in range(6):
        ax2.plot(xs, c6[j] * F[:, j], lw=1, alpha=0.7, label=f"unit {j + 1}" if j < 3 else None)
    ax2.plot(xs, curve(c6, xs), "k", lw=2, label="sum of units + constant")
    ax2.set_xlabel("time x (scaled units)")
    ax2.set_ylabel("weighted bump value (scaled units)")
    ax2.set_title("A curve built from 6 weighted tanh bumps (law fit)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "bumps_sum.png", dpi=120)

    print("\nrms error over 0..2 for different numbers of bumps and law strengths:")
    for n in (3, 6, 12):
        print(n, [round(rms_error(fit(n, lam)), 4) for lam in (0.0, 1.0, 10.0)])

# %% [markdown]
# ## Where this stops
# Here the bumps were fixed in place and only the weights were chosen. A real neural network also
# moves the bumps. That needs gradients and backpropagation: Session 2.
