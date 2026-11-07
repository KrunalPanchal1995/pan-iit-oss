"""Session 4 (Level 3): Romberg integration, far more accuracy from the same evaluations.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: Romberg integration
# **A. Real-world problem.** Some numbers are expensive. If every function value is one
# minute of simulation, or one reading from a slow instrument, you want the most accuracy
# from the fewest values. In Session 3 Simpson's rule with 17 evaluations gave an error of
# about 1.5e-7 for the area under e^x. Is there a way to get 1e-12 from the same 17 values?
# Today you combine trapezoid sums made with different step sizes so that their errors
# cancel (Romberg integration), check it against exact answers, and find out when it fails.
#
# *General education only: the numbers are for learning, not for engineering design.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: halve the step and reuse every value
# The trapezoid rule with n = 2^k slices is T_k. Going from T_(k-1) to T_k needs only the
# new midpoints: the old sample points are reused. So the table below costs 2^(levels-1) + 1
# evaluations in total, the same as one trapezoid rule on the finest grid.

# %%
def trapezoid_levels(f, a, b, levels):
    """Trapezoid sums T_0 ... T_(levels-1) with 1, 2, 4, ... slices.

    Returns (list of sums, number of function evaluations used). Every sample is computed once."""
    if levels < 1:
        raise ValueError("levels must be at least 1")
    if not a < b:
        raise ValueError("a must be smaller than b")
    h = b - a
    total = 0.5 * (f(a) + f(b))
    sums, evals = [h * total], 2
    for k in range(1, levels):
        h /= 2.0
        m = 2 ** (k - 1)                              # number of new midpoints
        total += sum(f(a + (2 * j - 1) * h) for j in range(1, m + 1))
        evals += m
        sums.append(h * total)
    return sums, evals


# %% [markdown]
# ## Step 2: cancel the h^2 error
# For a smooth function the trapezoid error has a series T(h) = I + c1 h^2 + c2 h^4 + c3 h^6 + ...
# with the same constants c1, c2, ... for every h. Halving h divides the h^2 term by 4, so
#
#     (4 T(h/2) - T(h)) / 3 = I + (small) h^4 + ...
#
# kills the h^2 term. This one combination is exactly Simpson's rule. Repeat with 16 and 15
# to kill h^4, then 64 and 63 for h^6, and so on: that is **Richardson extrapolation**.

# %%
def richardson(coarse, fine, power):
    """Remove the h**power term: (2**power * fine - coarse) / (2**power - 1), where fine used half the step."""
    q = 2.0 ** power
    return (q * fine - coarse) / (q - 1.0)


def romberg_table(f, a, b, levels):
    """Romberg table R[i][j], j <= i. R[i][0] is the trapezoid rule with 2^i slices;
    column j removes the errors h^2 ... h^(2j).  Returns (table, evaluations)."""
    sums, evals = trapezoid_levels(f, a, b, levels)
    table = [[s] for s in sums]
    for i in range(1, levels):
        for j in range(1, i + 1):
            table[i].append(richardson(table[i - 1][j - 1], table[i][j - 1], 2 * j))
    return table, evals


def romberg(f, a, b, levels=5):
    """Best entry of the table (the bottom-right corner) and the evaluations it cost."""
    table, evals = romberg_table(f, a, b, levels)
    return table[-1][-1], evals


def romberg_tol(f, a, b, tol=1e-10, max_levels=14):
    """Add rows until two successive diagonal entries differ by less than tol.

    Returns (value, evaluations, levels used, converged)."""
    table, evals = [], 0
    for levels in range(2, max_levels + 1):
        table, evals = romberg_table(f, a, b, levels)
        if abs(table[-1][-1] - table[-2][-1]) < tol:
            return table[-1][-1], evals, levels, True
    return table[-1][-1], evals, max_levels, False


def evaluations_for_levels(levels):
    return 2 ** (levels - 1) + 1


# %% [markdown]
# ## Step 3: measure the orders
# Column j of the table should have error about h^(2j+2). Fit the slopes again with
# `observed_order`, as in Session 3. (Column 0 is the trapezoid rule, order 2; column 1 is
# Simpson, order 4; column 2 is Boole's rule, order 6.)

# %%
def observed_order(hs, errors):
    """Slope of log(error) against log(h), fitted by least squares."""
    return float(np.polyfit(np.log(hs), np.log(errors), 1)[0])


def column_errors(f, a, b, exact, levels, column):
    """Absolute errors down one column of the table (rows column ... levels-1) and the step sizes of those rows."""
    table, _ = romberg_table(f, a, b, levels)
    rows = range(column, levels)
    return np.array([(b - a) / 2.0 ** i for i in rows]), np.array([abs(table[i][column] - exact) for i in rows])


def simpson_from_table(f, a, b, levels):
    """Column 1 of the table is Simpson's rule with 2^i slices: returns that list (rows 1 ...)."""
    table, _ = romberg_table(f, a, b, levels)
    return [row[1] for row in table[1:]]


# %% [markdown]
# ## Step 4: three functions with known areas
# * **e^x on [0, 1]**: smooth. Exact area e - 1.
# * **Gaussian bell exp(-x^2) on [0, 2]**: smooth but it bends a lot. Exact area sqrt(pi)/2 erf(2).
# * **sqrt(x) on [0, 1]**: the slope is infinite at 0, so it is not smooth there. Exact area 2/3.
# * **exp(sin(2 pi x)) on [0, 1]**: smooth and **periodic**. Exact area I0(1) = 1.26606...
# Romberg shines on the first two and fails on the last two, for different reasons.

# %%
EXACT_EXP = math.e - 1.0
EXACT_GAUSS = math.sqrt(math.pi) / 2.0 * math.erf(2.0)
EXACT_SQRT = 2.0 / 3.0


def bessel_i0(x):
    """Modified Bessel function I0 by its power series (good for small x): the exact area of exp(sin(2 pi t)) over a period is I0(1)."""
    term, total, k = 1.0, 1.0, 0
    while term > 1e-18 * total:
        k += 1
        term *= (x / 2.0) ** 2 / (k * k)
        total += term
    return total


EXACT_PERIODIC = bessel_i0(1.0)

FUNCTIONS = {
    1: ("e^x on [0, 1]", math.exp, 0.0, 1.0, EXACT_EXP),
    2: ("exp(-x^2) on [0, 2]", lambda x: math.exp(-x * x), 0.0, 2.0, EXACT_GAUSS),
    3: ("sqrt(x) on [0, 1]", math.sqrt, 0.0, 1.0, EXACT_SQRT),
    4: ("exp(sin(2 pi x)) on [0, 1]", lambda x: math.exp(math.sin(2.0 * math.pi * x)), 0.0, 1.0, EXACT_PERIODIC),
}


def table_errors(number, levels):
    """Absolute errors of every table entry for function `number` (1 to 4)."""
    _, f, a, b, exact = FUNCTIONS[number]
    table, evals = romberg_table(f, a, b, levels)
    return [[abs(x - exact) for x in row] for row in table], evals


# %% [markdown]
# ## Step 5: the evaluation budget (used by the mini-project)
# For a target error, how many function values does each rule need? The trapezoid and Simpson
# rules use the grids with 2^k slices (2^k + 1 values). Romberg uses the diagonal of the table
# (2^(levels-1) + 1 values for `levels` rows).

# %%
def evaluations_needed(number, target, rule, max_levels=18):
    """Smallest number of evaluations (on the 2^k grids) for which `rule` is within `target` of the exact area.

    rule is "trapezoid", "simpson" or "romberg". Returns None if max_levels is not enough."""
    _, f, a, b, exact = FUNCTIONS[number]
    table, _ = romberg_table(f, a, b, max_levels)
    for i in range(max_levels):
        if rule == "trapezoid":
            value = table[i][0]
        elif rule == "simpson":
            if i < 1:
                continue
            value = table[i][1]
        elif rule == "romberg":
            value = table[i][i]
        else:
            raise ValueError("rule must be trapezoid, simpson or romberg")
        if abs(value - exact) <= target:
            return evaluations_for_levels(i + 1)
    return None


# %% [markdown]
# ## See it
# Figure 1: the table of errors for e^x on [0, 1], one cell per entry (darker orange means a
# smaller error). Figure 2: error against the number of function values for the three rules.
# Figure 3: where Romberg fails, the square root and the periodic function.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA = "#0072b2", "#c86a00", "#d81b60"
    errs, ev = table_errors(1, 6)
    print(f"e^x on [0, 1], 6 levels = {ev} evaluations:")
    for i, row in enumerate(errs):
        print("  ", i, "  ".join(f"{e:8.1e}" for e in row))
    value, ev17 = romberg(math.exp, 0.0, 1.0, 5)
    print(f"Romberg with {ev17} evaluations: {value:.15f}, error {abs(value - EXACT_EXP):.1e}; Simpson with 17: {abs(simpson_from_table(math.exp, 0.0, 1.0, 5)[-1] - EXACT_EXP):.1e}")
    for j in range(3):
        hs, es = column_errors(math.exp, 0.0, 1.0, EXACT_EXP, 6, j)
        print(f"column {j} observed order: {observed_order(hs[:4], es[:4]):.2f}")
    for number in (2, 3, 4):
        name = FUNCTIONS[number][0]
        e, _ = table_errors(number, 7)
        print(f"{name}: last row errors", "  ".join(f"{x:.1e}" for x in e[-1]))
    for target in (1e-4, 1e-6, 1e-8, 1e-10, 1e-12):
        print(f"target {target:.0e}: " + ", ".join(f"{rule} {evaluations_needed(2, target, rule)}" for rule in ("trapezoid", "simpson", "romberg")))

    # figure 1: the error table of e^x
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    n = 6
    grid = np.full((n, n), np.nan)
    for i, row in enumerate(errs):
        for j, e in enumerate(row):
            grid[i, j] = np.log10(max(e, 1e-17))
    im = ax.imshow(grid, cmap="cividis_r", vmin=-17, vmax=0)
    for i, row in enumerate(errs):
        for j, e in enumerate(row):
            ax.text(j, i, f"{e:.0e}", ha="center", va="center", fontsize=8, color="white" if grid[i, j] < -9 else "black")
    ax.set_xticks(range(n), [f"col {j}" for j in range(n)])
    ax.set_yticks(range(n), [f"{evaluations_for_levels(i + 1)} values" for i in range(n)])
    ax.set_xlabel("column j: removes errors up to h^(2j)")
    ax.set_ylabel("row: trapezoid sum with 2^i slices")
    ax.set_title("Error of every Romberg table entry for e^x on [0, 1]", fontsize=10)
    fig.colorbar(im, ax=ax, label="log10 of the absolute error")
    fig.tight_layout()
    fig.savefig(OUT / "romberg_table.png", dpi=120)

    # figure 2: error against evaluations
    fig2, axs = plt.subplots(1, 2, figsize=(10, 4.0))
    for ax, number in zip(axs, (1, 2)):
        name, f, a, b, exact = FUNCTIONS[number]
        table, _ = romberg_table(f, a, b, 9)
        evs = [evaluations_for_levels(i + 1) for i in range(9)]
        ax.loglog(evs, [max(abs(table[i][0] - exact), 1e-17) for i in range(9)], "o-", color=MAGENTA, label="trapezoid")
        ax.loglog(evs[1:], [max(abs(table[i][1] - exact), 1e-17) for i in range(1, 9)], "s-", color=ORANGE, label="Simpson (column 1)")
        ax.loglog(evs, [max(abs(table[i][i] - exact), 1e-17) for i in range(9)], "^-", color=BLUE, label="Romberg (diagonal)")
        ax.axhline(2.2e-16, color="#666666", ls=":", lw=1)
        ax.text(2.2, 3.5e-16, "round-off floor", fontsize=8, color="#444444")
        ax.set_xlabel("function evaluations")
        ax.set_ylabel("absolute error")
        ax.set_title(name, fontsize=10)
        ax.set_ylim(1e-17, 1)
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=8, loc="lower left")
    fig2.tight_layout()
    fig2.savefig(OUT / "error_vs_evaluations.png", dpi=120)

    # figure 3: failures
    fig3, axs3 = plt.subplots(1, 2, figsize=(10, 4.0))
    for ax, number in zip(axs3, (3, 4)):
        name, f, a, b, exact = FUNCTIONS[number]
        table, _ = romberg_table(f, a, b, 9)
        evs = [evaluations_for_levels(i + 1) for i in range(9)]
        ax.loglog(evs, [max(abs(table[i][0] - exact), 1e-17) for i in range(9)], "o-", color=MAGENTA, label="trapezoid")
        ax.loglog(evs, [max(abs(table[i][i] - exact), 1e-17) for i in range(9)], "^-", color=BLUE, label="Romberg (diagonal)")
        ax.set_xlabel("function evaluations")
        ax.set_ylabel("absolute error")
        ax.set_title(name, fontsize=10)
        ax.set_ylim(1e-17, 1)
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=8, loc="lower left")
    axs3[0].text(3, 3e-3, "no gain from extrapolation", fontsize=9)
    axs3[1].text(3, 1e-1, "trapezoid already at round-off by 16 values;\nRomberg is worse", fontsize=9)
    fig3.tight_layout()
    fig3.savefig(OUT / "failure_cases.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. The mini-project (README) asks how many function values each rule needs.
