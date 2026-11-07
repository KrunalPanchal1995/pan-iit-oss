"""Session 1 (Level 1): every measurement has an error, and errors carry through a formula.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: every measurement has an error
# **A. Real-world problem.** You measure a table with a school ruler and read 12.3 cm. Is it
# exactly 12.3? No. The honest statement is 12.3 +- 0.1 cm: the true length is probably
# between 12.2 and 12.4. When you put two such lengths into the formula for area, the
# answer carries an error too. How big?
#
# **Plan.** (1) write a measurement as value +- error, (2) find the smallest and largest
# possible area, (3) compare the relative errors, (4) plot it.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a measurement is an interval
# "12.3 +- 0.1" means the true value is believed to lie in [12.2, 12.4]. The error 0.1 is
# about half the smallest ruler mark. The *relative error* is error / value, usually as a
# percentage: 0.1 / 12.3 = 0.81 percent.

# %%
def interval(value, err):
    """Return (low, high) of a measurement value +- err."""
    return value - err, value + err


def relative_error(value, err):
    """Error as a fraction of the value (multiply by 100 for percent)."""
    return err / abs(value)


def half_range(readings):
    """Half the spread of repeated readings: a first, rough estimate of the error."""
    r = np.asarray(readings, dtype=float)
    return float((r.max() - r.min()) / 2.0)


# %% [markdown]
# ## Step 2: carry the interval through the area formula
# Area = length * width. The smallest area uses both smallest lengths; the largest uses both
# largest lengths (all lengths are positive). This "worst case" is easy to see and a little
# pessimistic: it assumes both errors push the same way at once.

# %%
def rect_area(length, width):
    return length * width


def area_extremes(length, dl, width, dw):
    """Smallest and largest area when length and width are only known to +- dl and +- dw."""
    return rect_area(length - dl, width - dw), rect_area(length + dl, width + dw)


# %% [markdown]
# ## Step 3: see it
# Left: the measured rectangle with its smallest and largest versions. Right: area against
# length; the band is the range of area for a length known only to +- 0.1 cm.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    L, dL, W, dW = 12.3, 0.1, 8.4, 0.1
    lo, hi = area_extremes(L, dL, W, dW)
    area = rect_area(L, W)
    print(f"area = {area:.2f} cm^2, smallest {lo:.2f}, largest {hi:.2f}, half-range {(hi - lo) / 2:.2f}")
    print(f"relative errors: length {100 * relative_error(L, dL):.2f}%, width {100 * relative_error(W, dW):.2f}%, "
          f"area {100 * (hi - lo) / 2 / area:.2f}%")

    fig, ax = plt.subplots(figsize=(6, 4.5))
    for (l, w), col, name in [((L + dL, W + dW), "tab:red", "largest"), ((L, W), "tab:blue", "measured"),
                              ((L - dL, W - dW), "tab:green", "smallest")]:
        ax.add_patch(plt.Rectangle((0, 0), l, w, fill=False, edgecolor=col, lw=2, label=f"{name}: {l:.1f} x {w:.1f}"))
    ax.set_xlim(11.5, 12.6)
    ax.set_ylim(7.8, 8.7)
    ax.set_aspect("equal")
    ax.set_xlabel("length (cm)")
    ax.set_ylabel("width (cm)")
    ax.set_title("Top-right corners: three possible rectangles")
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "rectangles.png", dpi=120)

    ls = np.linspace(11.8, 12.8, 101)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(ls, rect_area(ls, W), label="area at width 8.4 cm")
    ax2.axvspan(L - dL, L + dL, alpha=0.2, color="tab:orange", label="length 12.3 +- 0.1 cm")
    ax2.axhspan(rect_area(L - dL, W), rect_area(L + dL, W), alpha=0.2, color="tab:orange")
    ax2.set_xlabel("length (cm)")
    ax2.set_ylabel("area (cm^2)")
    ax2.set_title("A small length error becomes an area error")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "area_band.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Change the lengths and errors, predict the area error before you run, then answer the
# questions in the README (section F) and run the checkpoint.
