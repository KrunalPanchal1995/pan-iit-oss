"""Session 5 (Level 3): Gaussian quadrature, choosing the sample points as well as the weights.

Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: Gaussian quadrature
# **A. Real-world problem.** In Session 4 Romberg integration needed 65 function values to
# reach 1e-12 for a bell curve, and Simpson's rule needed 513. If every value is a one-minute
# simulation that is a long wait. All those rules used *equally spaced* points and only chose
# the weights. What if we also choose **where** to sample? Today you build the Gauss-Legendre
# rule: n well-chosen points that are exact for every polynomial up to degree 2n - 1, check
# it against exact areas, compare it with Simpson and Romberg for the same number of values,
# and find out when it fails.
#
# *General education only: the numbers are for learning, not for engineering design.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the points are the roots of a Legendre polynomial
# The Legendre polynomials P_0 = 1, P_1 = x, P_2 = (3x^2 - 1)/2, ... come from the recurrence
# (k + 1) P_(k+1) = (2k + 1) x P_k - k P_(k-1). The n sample points of the n-point Gauss rule
# on [-1, 1] are the n roots of P_n; they lie inside the interval, crowd towards the ends and
# are symmetric about 0. We find each root with Newton's method, starting from a good guess.

# %%
def legendre_and_derivative(n, x):
    """P_n(x) and its derivative, by the three-term recurrence."""
    if n < 0:
        raise ValueError("n must be at least 0")
    p_prev, p = 1.0, x
    if n == 0:
        return 1.0, 0.0
    for k in range(1, n):
        p_prev, p = p, ((2 * k + 1) * x * p - k * p_prev) / (k + 1)
    dp = n * (x * p - p_prev) / (x * x - 1.0)
    return p, dp


def gauss_legendre_nodes(n):
    """Nodes (increasing) and weights of the n-point Gauss-Legendre rule on [-1, 1]."""
    if n < 1:
        raise ValueError("n must be at least 1")
    nodes, weights = [], []
    for k in range(1, n + 1):
        x = math.cos(math.pi * (k - 0.25) / (n + 0.5))      # good starting guess for the k-th root
        for _ in range(100):
            p, dp = legendre_and_derivative(n, x)
            step = p / dp
            x -= step
            if abs(step) < 1e-15:
                break
        _, dp = legendre_and_derivative(n, x)
        nodes.append(x)
        weights.append(2.0 / ((1.0 - x * x) * dp * dp))
    order = np.argsort(nodes)
    return np.array(nodes)[order], np.array(weights)[order]


# %% [markdown]
# ## Step 2: the rule on any interval
# Map [-1, 1] to [a, b] with x = m + r t (m = midpoint, r = half-length). The integral is
# r times the weighted sum of f at the mapped points. A rule with n points costs exactly n
# function values.

# %%
def gauss_legendre(f, a, b, n):
    """Integral of f from a to b with the n-point Gauss-Legendre rule (n function values)."""
    if not a < b:
        raise ValueError("a must be smaller than b")
    t, w = gauss_legendre_nodes(n)
    m, r = 0.5 * (a + b), 0.5 * (b - a)
    return float(r * sum(wi * f(m + r * ti) for ti, wi in zip(t, w)))


def composite_gauss(f, edges, n):
    """Apply the n-point rule on every piece between consecutive edges. Cost: n values per piece.

    Put an edge exactly where the function stops being smooth."""
    if len(edges) < 2 or any(b <= a for a, b in zip(edges[:-1], edges[1:])):
        raise ValueError("edges must be increasing, with at least two entries")
    return float(sum(gauss_legendre(f, a, b, n) for a, b in zip(edges[:-1], edges[1:])))


# %% [markdown]
# ## Step 3: why 2n - 1?
# An n-point rule has 2n numbers to choose (n points, n weights). A polynomial of degree 2n - 1
# has 2n coefficients, so we can ask for exactness on all of them: that is what the Legendre
# roots achieve. Equally spaced points with chosen weights reach only about degree n - 1 (n
# for Simpson's three points). `monomial_errors` tests the rule on x^k over [0, 1] (exact area
# 1/(k + 1)): the error is at round-off up to degree 2n - 1 and then jumps.

# %%
def monomial_errors(n, max_degree=20):
    """Absolute error of the n-point rule for the area of x^k on [0, 1], k = 0 ... max_degree."""
    return [abs(gauss_legendre(lambda x, k=k: x ** k, 0.0, 1.0, n) - 1.0 / (k + 1)) for k in range(max_degree + 1)]


def exact_degree(n, tol=1e-14, max_degree=40):
    """Highest degree k such that the rule is exact (error below tol) for x^j, every j <= k."""
    k = -1
    for j, e in enumerate(monomial_errors(n, max_degree)):
        if e > tol:
            break
        k = j
    return k


# %% [markdown]
# ## Step 4: four functions with known areas
# The same four as in Session 4, so the rules can be compared with Romberg and Simpson:
# e^x on [0, 1], the bell curve exp(-x^2) on [0, 2], sqrt(x) on [0, 1] (not smooth at 0) and
# the periodic exp(sin(2 pi x)) over one period. Number 5 is the corner |x - 0.37| on [0, 1].

# %%
def bessel_i0(x):
    """Modified Bessel function I0 by its power series: the exact area of exp(sin(2 pi t)) over a period is I0(1)."""
    term, total, k = 1.0, 1.0, 0
    while term > 1e-18 * total:
        k += 1
        term *= (x / 2.0) ** 2 / (k * k)
        total += term
    return total


KINK = 0.37
FUNCTIONS = {
    1: ("e^x on [0, 1]", math.exp, 0.0, 1.0, math.e - 1.0),
    2: ("exp(-x^2) on [0, 2]", lambda x: math.exp(-x * x), 0.0, 2.0, math.sqrt(math.pi) / 2.0 * math.erf(2.0)),
    3: ("sqrt(x) on [0, 1]", math.sqrt, 0.0, 1.0, 2.0 / 3.0),
    4: ("exp(sin(2 pi x)) on [0, 1]", lambda x: math.exp(math.sin(2.0 * math.pi * x)), 0.0, 1.0, bessel_i0(1.0)),
    5: ("|x - 0.37| on [0, 1]", lambda x: abs(x - KINK), 0.0, 1.0, (KINK ** 2 + (1.0 - KINK) ** 2) / 2.0),
}


def gauss_error(number, n):
    """Absolute error of the n-point rule for function `number`."""
    _, f, a, b, exact = FUNCTIONS[number]
    return abs(gauss_legendre(f, a, b, n) - exact)


# %% [markdown]
# ## Step 5: the evaluation budget (used by the mini-project)
# How many values does Gauss need for a target error? And if you do not know in advance which
# n to use, you can raise n until two successive rules agree. But the rules are **not nested**:
# the 6-point rule shares no points with the 5-point rule, so every rule you try costs n new
# values. `gauss_tol` counts the whole bill.

# %%
def gauss_values_needed(number, target, max_n=40):
    """Smallest n whose error is at most `target` (needs the exact answer), or None."""
    for n in range(1, max_n + 1):
        if gauss_error(number, n) <= target:
            return n
    return None


def gauss_tol(f, a, b, tol=1e-10, n_start=2, max_n=60):
    """Raise n until the n-point and (n+1)-point rules differ by less than tol.

    Returns (value of the (n+1)-point rule, n + 1, total values computed on the way, converged)."""
    spent = 0
    previous = gauss_legendre(f, a, b, n_start)
    spent += n_start
    for n in range(n_start + 1, max_n + 1):
        current = gauss_legendre(f, a, b, n)
        spent += n
        if abs(current - previous) < tol:
            return current, n, spent, True
        previous = current
    return previous, max_n, spent, False


def observed_order(hs, errors):
    """Slope of log(error) against log(h), fitted by least squares (use h = 1/n for algebraic convergence)."""
    return float(np.polyfit(np.log(hs), np.log(errors), 1)[0])


# %% [markdown]
# ## See it
# Figure 1: the 5 Gauss points and weights on [0, 1], drawn as weighted rectangles, next to
# 5 equally spaced Simpson points. Figure 2: error against function values for Simpson,
# Romberg (from Session 4) and Gauss on e^x and on the bell curve. Figure 3: error of the
# n-point rule for x^k, jumping after degree 2n - 1; and where Gauss fails.

# %%
def simpson_values(f, a, b, m):
    """Simpson's rule on m values (m odd, m >= 3)."""
    n = m - 1
    h = (b - a) / n
    s = f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, n))
    return h / 3.0 * s


def trapezoid_values(f, a, b, m):
    """Trapezoid rule on m equally spaced values (m >= 2)."""
    n = m - 1
    h = (b - a) / n
    return h * (0.5 * (f(a) + f(b)) + sum(f(a + i * h) for i in range(1, n)))


def romberg_corner(f, a, b, levels):
    """Corner of the Romberg table with `levels` rows (2^(levels-1) + 1 values), as in Session 4."""
    h = b - a
    total = 0.5 * (f(a) + f(b))
    rows = [[h * total]]
    for k in range(1, levels):
        h /= 2.0
        total += sum(f(a + (2 * j - 1) * h) for j in range(1, 2 ** (k - 1) + 1))
        row = [h * total]
        for j in range(1, k + 1):
            row.append((4 ** j * row[j - 1] - rows[k - 1][j - 1]) / (4 ** j - 1))
        rows.append(row)
    return rows[-1][-1]


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA = "#0072b2", "#c86a00", "#d81b60"
    t5, w5 = gauss_legendre_nodes(5)
    print("5-point nodes on [0, 1]:", np.round(0.5 + 0.5 * t5, 5), "weights", np.round(0.5 * w5, 5))
    print(f"e^x on [0, 1]: 5-point Gauss error {gauss_error(1, 5):.1e}; Simpson with 5 values {abs(simpson_values(math.exp, 0, 1, 5) - (math.e - 1)):.1e}")
    for n in range(1, 8):
        print(f"  n = {n}: error {gauss_error(1, n):.1e}, exact up to degree {exact_degree(n)}")
    for target in (1e-6, 1e-8, 1e-10, 1e-12):
        _, f2, a2, b2, _ = FUNCTIONS[2]
        v, nn, spent, ok = gauss_tol(f2, a2, b2, target)
        print(f"bell curve, target {target:.0e}: Gauss needs n = {gauss_values_needed(2, target)}; with the stopping rule it stops at n = {nn} having computed {spent} values")
    ns_s = [20, 40, 80, 160]
    print("sqrt(x): errors", [f"{gauss_error(3, n):.1e}" for n in ns_s], "observed order", round(observed_order([1.0 / n for n in ns_s], [gauss_error(3, n) for n in ns_s]), 2))
    print("periodic: Gauss errors n = 5, 8, 10:", [f"{gauss_error(4, n):.1e}" for n in (5, 8, 10)])
    print("corner: one rule on [0, 1] with 10 points", f"{gauss_error(5, 10):.1e}", "; split at 0.37 with 1 point per piece:",
          f"{abs(composite_gauss(FUNCTIONS[5][1], [0.0, KINK, 1.0], 1) - FUNCTIONS[5][4]):.1e}")

    # figure 1: nodes and weights
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.0), sharey=True)
    xx = np.linspace(0, 1, 400)
    xg, wg = 0.5 + 0.5 * t5, 0.5 * w5
    xs = np.linspace(0, 1, 5)
    for ax, xp, label in ((axs[0], xs, "5 equally spaced values (Simpson)"), (axs[1], xg, "5 Gauss-Legendre values")):
        ax.plot(xx, np.exp(xx), color=BLUE, lw=2)
        ax.plot(xp, np.exp(xp), "o", color=MAGENTA, ms=7)
        ax.set_title(label, fontsize=10)
        ax.set_xlabel("x")
        ax.grid(alpha=0.3)
    for xi, wi in zip(xg, wg):
        axs[1].bar(xi, np.exp(xi), width=wi, color=ORANGE, alpha=0.35, edgecolor=ORANGE)
    axs[0].set_ylabel("f(x) = e^x")
    axs[0].text(0.03, 0.2, f"error {abs(simpson_values(math.exp, 0, 1, 5) - (math.e - 1)):.1e}", transform=axs[0].transAxes)
    axs[1].text(0.03, 0.2, f"error {gauss_error(1, 5):.1e}", transform=axs[1].transAxes)
    fig.tight_layout()
    fig.savefig(OUT / "nodes_weights.png", dpi=120)

    # figure 2: error against values
    fig2, axs2 = plt.subplots(1, 2, figsize=(10, 4.0))
    for ax, number in zip(axs2, (1, 2)):
        name, f, a, b, exact = FUNCTIONS[number]
        gs = list(range(1, 17))
        ax.semilogy(gs, [max(gauss_error(number, n), 1e-17) for n in gs], "^-", color=BLUE, label="Gauss-Legendre")
        ms = [3, 5, 9, 17, 33]
        ax.semilogy(ms, [max(abs(simpson_values(f, a, b, m) - exact), 1e-17) for m in ms], "s-", color=ORANGE, label="Simpson")
        ax.semilogy(ms, [max(abs(romberg_corner(f, a, b, int(math.log2(m - 1)) + 1) - exact), 1e-17) for m in ms], "o-", color=MAGENTA, label="Romberg")
        ax.axhline(2.2e-16, color="#666666", ls=":", lw=1)
        ax.set_xlabel("function values")
        ax.set_ylabel("absolute error")
        ax.set_title(name, fontsize=10)
        ax.set_ylim(1e-17, 1)
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=8, loc="lower left")
    fig2.tight_layout()
    fig2.savefig(OUT / "error_vs_values.png", dpi=120)

    # figure 3: exactness by degree, and the failures
    fig3, axs3 = plt.subplots(1, 3, figsize=(13, 3.9))
    for n, col, mk in ((2, MAGENTA, "o"), (3, ORANGE, "s"), (5, BLUE, "^")):
        axs3[0].semilogy(range(21), [max(e, 1e-17) for e in monomial_errors(n)], mk + "-", color=col, ms=4, label=f"n = {n} (exact to degree {2 * n - 1})")
    axs3[0].set_xlabel("degree k of x^k")
    axs3[0].set_ylabel("absolute error of the area")
    axs3[0].set_title("Exactness: error jumps after degree 2n - 1", fontsize=10)
    axs3[0].legend(fontsize=8, loc="lower right")
    ns = np.arange(2, 81)
    axs3[1].loglog(ns, [gauss_error(3, int(n)) for n in ns], "^-", ms=3, color=BLUE, label="Gauss-Legendre")
    axs3[1].loglog([5, 9, 17, 33, 65], [abs(simpson_values(math.sqrt, 0, 1, m) - 2 / 3) for m in (5, 9, 17, 33, 65)], "s-", color=ORANGE, label="Simpson")
    axs3[1].set_xlabel("function values")
    axs3[1].set_xticks([2, 5, 10, 20, 40, 80], ["2", "5", "10", "20", "40", "80"])
    axs3[1].minorticks_off()
    axs3[1].set_title("sqrt(x): only algebraic decay (slope -3)", fontsize=10)
    axs3[1].legend(fontsize=8)
    f4, ex4 = FUNCTIONS[4][1], FUNCTIONS[4][4]
    axs3[2].semilogy(range(2, 21), [max(gauss_error(4, n), 1e-17) for n in range(2, 21)], "^-", ms=3, color=BLUE, label="Gauss-Legendre")
    ev = [2, 3, 5, 9, 17]
    axs3[2].semilogy(ev, [max(abs(trapezoid_values(f4, 0.0, 1.0, m) - ex4), 1e-17) for m in ev], "o-", color=MAGENTA, label="trapezoid")
    axs3[2].set_xlabel("function values")
    axs3[2].set_title("periodic: the trapezoid rule wins", fontsize=10)
    axs3[2].legend(fontsize=8, loc="lower left")
    for ax in axs3:
        ax.grid(alpha=0.3, which="both")
        ax.set_ylim(1e-17, 1)
    fig3.tight_layout()
    fig3.savefig(OUT / "exactness_and_failures.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. The mini-project (README) asks how many function values each rule needs.
