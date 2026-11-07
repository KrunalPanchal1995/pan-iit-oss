"""Session 1 (Level 1): rainfall and crop yield, and the line that misses least.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: the line that misses least
# **A. Real-world problem.** A farmer has ten seasons of records: how much rain fell, and how much
# grain the field gave. Next season's rain forecast is known. What yield should the farmer expect?
# We draw a straight line through the dots and read the answer off it. But many lines are possible,
# so we need a fair rule for "best". All data here are made up for teaching.
#
# **Plan.** (1) store the dots, (2) draw any line y = a + b x, (3) measure each miss (a residual),
# (4) add up the squared misses, (5) find the line with the smallest total.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# rain in hundreds of mm per season (3.0 means 300 mm); yield in tonnes per hectare
RAIN = np.array([3.0, 3.8, 4.5, 5.2, 5.8, 6.5, 7.2, 7.9, 8.6, 9.2])
YIELD = np.array([2.0, 2.3, 2.4, 2.5, 2.8, 2.9, 3.4, 4.1, 3.8, 3.9])


# %% [markdown]
# ## Step 1: a line and its misses
# A line is y = a + b x. Here `a` is the yield with no rain (the intercept, t/ha) and `b` is the
# extra yield for each extra 100 mm of rain (the slope, t/ha per 100 mm). A *residual* is
# observed yield minus the line's prediction: positive when the dot is above the line.

# %%
def predict(a, b, x):
    """Line prediction a + b x."""
    return a + b * np.asarray(x, float)


def residuals(a, b, x, y):
    """Observed minus predicted (the vertical miss of each dot)."""
    return np.asarray(y, float) - predict(a, b, x)


def sse(a, b, x, y):
    """Sum of squared residuals: the total squared miss."""
    return float(np.sum(residuals(a, b, x, y) ** 2))


# %% [markdown]
# ## Step 2: why squares?
# Misses above and below the line would cancel if we just added them. Squaring makes every miss
# positive and makes one big miss count more than several small ones. The best line is the one
# with the smallest total squared miss. Calculus gives it in closed form (Session 2 derives it):
#
#     b = sum((x - xbar) * (y - ybar)) / sum((x - xbar)^2)        a = ybar - b * xbar

# %%
def best_line(x, y):
    """Least-squares intercept and slope from the closed form."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    xm, ym = x.mean(), y.mean()
    b = np.sum((x - xm) * (y - ym)) / np.sum((x - xm) ** 2)
    return float(ym - b * xm), float(b)


def sse_for_slope(b, x, y):
    """Smallest total squared miss over all intercepts when the slope is fixed at b."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    a = y.mean() - b * x.mean()
    return sse(a, b, x, y)


def scan_best_slope(x, y, lo=0.0, hi=0.8, n=801):
    """Brute force: try many slopes, return the slope with the smallest squared miss."""
    slopes = np.linspace(lo, hi, n)
    errs = np.array([sse_for_slope(b, x, y) for b in slopes])
    return float(slopes[np.argmin(errs)])


# %% [markdown]
# ## Step 3: see it
# Left: the dots, a guess line and the residuals as vertical bars; the best line has the smallest
# total bar-area. Right: total squared miss against slope; the lowest point of the bowl is the
# best slope.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    a0, b0 = best_line(RAIN, YIELD)
    print(f"best line: yield = {a0:.3f} + {b0:.4f} * rain   (t/ha, rain in 100 mm)")
    print(f"total squared miss, best line: {sse(a0, b0, RAIN, YIELD):.3f}")
    print(f"total squared miss, guess line 1.0 + 0.30 x: {sse(1.0, 0.30, RAIN, YIELD):.3f}")
    print(f"brute-force slope: {scan_best_slope(RAIN, YIELD):.3f}")
    xs = np.linspace(2.5, 9.7, 50)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    ax = axs[0]
    ax.scatter(RAIN, YIELD, color="tab:blue", zorder=3, label="seasons")
    ax.plot(xs, predict(1.0, 0.30, xs), color="tab:red", ls="--", label="guess: 1.0 + 0.30 x")
    ax.vlines(RAIN, predict(1.0, 0.30, RAIN), YIELD, color="tab:red", alpha=0.6)
    ax.plot(xs, predict(a0, b0, xs), color="tab:green", label=f"best: {a0:.2f} + {b0:.3f} x")
    ax.set_xlabel("rainfall (hundreds of mm)")
    ax.set_ylabel("yield (t/ha)")
    ax.set_title("Residuals are the vertical bars")
    ax.grid(alpha=0.3)
    ax.legend()
    bs = np.linspace(0, 0.8, 100)
    axs[1].plot(bs, [sse_for_slope(b, RAIN, YIELD) for b in bs])
    axs[1].axvline(b0, color="gray", ls=":")
    axs[1].set_xlabel("slope b (t/ha per 100 mm)")
    axs[1].set_ylabel("total squared miss (t/ha)^2")
    axs[1].set_title("Smallest total squared miss at the best slope")
    axs[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "dots_and_line.png", dpi=120)
    print("predicted yield at 600 mm:", round(float(predict(a0, b0, 6.0)), 2), "t/ha")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
