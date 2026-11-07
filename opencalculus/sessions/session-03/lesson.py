"""Session 3 (Level 3): numerical derivatives and integrals, checked against exact answers.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: how good are numerical slopes and areas?
# **A. Real-world problem.** A data logger gives you numbers, not formulas. To get
# acceleration or distance from it you must differentiate and integrate numerically. Every
# method makes an error. How does the error shrink when the step shrinks, and when does it
# stop shrinking? We test four methods on functions whose exact answers we know.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: two ways to differentiate
# Forward difference (f(x+h) - f(x)) / h has error about h (order 1).
# Central difference (f(x+h) - f(x-h)) / (2h) has error about h^2 (order 2).

# %%
def forward_diff(f, x, h):
    return (f(x + h) - f(x)) / h


def central_diff(f, x, h):
    return (f(x + h) - f(x - h)) / (2.0 * h)


# %% [markdown]
# ## Step 2: two ways to integrate
# Trapezoid rule: join neighbouring points by straight lines (error about h^2, order 2).
# Simpson's rule: join triples of points by parabolas (error about h^4, order 4; n must be even).

# %%
def trapezoid(f, a, b, n):
    x = np.linspace(a, b, n + 1)
    y = f(x)
    h = (b - a) / n
    return float(h * (y.sum() - 0.5 * (y[0] + y[-1])))


def simpson(f, a, b, n):
    if n % 2:
        raise ValueError("Simpson's rule needs an even number of slices")
    x = np.linspace(a, b, n + 1)
    y = f(x)
    h = (b - a) / n
    return float(h / 3.0 * (y[0] + y[-1] + 4.0 * y[1:-1:2].sum() + 2.0 * y[2:-1:2].sum()))


# %% [markdown]
# ## Step 3: measure the order
# If error ~ C h^p then log(error) = log C + p log(h): on a log-log plot the points lie on a
# straight line of slope p. `observed_order` fits that line.

# %%
def observed_order(hs, errors):
    """Slope of log(error) against log(h), fitted by least squares."""
    return float(np.polyfit(np.log(hs), np.log(errors), 1)[0])


# %% [markdown]
# ## Step 4: adaptive steps
# Use small slices only where the function bends quickly. Adaptive Simpson compares one
# Simpson step with two half-steps; if they disagree by more than the tolerance, split.

# %%
def adaptive_simpson(f, a, b, tol=1e-8, panels=16):
    """Returns (value, number of function evaluations)."""
    count = [0]

    def ev(x):
        count[0] += 1
        return float(f(np.float64(x)))

    def s(fa, fm, fb, a_, b_):
        return (b_ - a_) / 6.0 * (fa + 4.0 * fm + fb)

    def rec(a_, b_, fa, fm, fb, whole, tol_, depth):
        m = 0.5 * (a_ + b_)
        lm, rm = 0.5 * (a_ + m), 0.5 * (m + b_)
        flm, frm = ev(lm), ev(rm)
        left, right = s(fa, flm, fm, a_, m), s(fm, frm, fb, m, b_)
        delta = left + right - whole
        if depth <= 0 or abs(delta) <= 15.0 * tol_:
            return left + right + delta / 15.0
        return (rec(a_, m, fa, flm, fm, left, tol_ / 2, depth - 1) +
                rec(m, b_, fm, frm, fb, right, tol_ / 2, depth - 1))

    # start from 16 equal panels so that a narrow feature cannot hide between the first 3 points
    edges = np.linspace(a, b, panels + 1)
    value = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        fa, fb, fm = ev(lo), ev(hi), ev(0.5 * (lo + hi))
        value += rec(lo, hi, fa, fm, fb, s(fa, fm, fb, lo, hi), tol / panels, 40)
    return value, count[0]


# %%
def peak(x):
    """A narrow peak at x = 0.35 (width 0.005): easy to miss on a coarse grid."""
    return np.exp(-((np.asarray(x, dtype=float) - 0.35) / 0.005) ** 2)


def peak_exact(a=0.0, b=1.0):
    """Exact area of the peak, from the error function erf."""
    from math import erf, sqrt, pi
    return 0.005 * sqrt(pi) / 2.0 * (erf((b - 0.35) / 0.005) - erf((a - 0.35) / 0.005))


KINK = 0.37   # position of the corner of |x - 0.37|


def kink_exact():
    """Exact area of |x - 0.37| on [0, 1]: two triangles."""
    return (KINK ** 2 + (1.0 - KINK) ** 2) / 2.0


# %% [markdown]
# ## Step 5: a noisy speedometer log (used by the mini-project)
# True speed 12 + 8 sin(2 pi t / 40) m/s, so the true distance is known exactly. The logged
# reading is 2 percent too high (a calibration error) plus random noise of 0.8 m/s, sampled 10
# times per second for 60 s.

# %%
def true_speed(t):
    return 12.0 + 8.0 * np.sin(2 * np.pi * np.asarray(t, dtype=float) / 40.0)


def true_distance(t):
    t = np.asarray(t, dtype=float)
    return 12.0 * t + 8.0 * 40.0 / (2 * np.pi) * (1.0 - np.cos(2 * np.pi * t / 40.0))


def speedometer_log(seed=4, scale=1.02, noise=0.8, rate=10, duration=60.0):
    """Returns (t in s, logged speed in m/s)."""
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, duration + 0.5 / rate, 1.0 / rate)
    return t, scale * true_speed(t) + rng.normal(0.0, noise, t.size)


def integrate_log(t, v):
    """Distance (m) from a sampled speed log: trapezoid rule on uneven or even samples."""
    return float(np.sum(0.5 * (v[1:] + v[:-1]) * np.diff(t)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # --- differentiation of sin at x = 1 (exact cos 1)
    x0, exact_d = 1.0, np.cos(1.0)
    hs = 10.0 ** -np.arange(0, 16, 0.5)
    ef = np.abs(forward_diff(np.sin, x0, hs) - exact_d)
    ec = np.abs(central_diff(np.sin, x0, hs) - exact_d)
    fit = hs >= 1e-4
    mid = (hs <= 1e-1) & (hs >= 1e-3)
    print(f"order forward diff: {observed_order(hs[mid], ef[mid]):.2f}; central diff: {observed_order(hs[mid], ec[mid]):.2f}")
    print(f"forward diff smallest error {ef.min():.1e} at h = {hs[ef.argmin()]:.1e}; central {ec.min():.1e} at h = {hs[ec.argmin()]:.1e}")
    print(f"at h = 1e-15: forward error {ef[-1]:.1e}, central error {ec[-1]:.1e}")

    # --- integration of exp on [0, 1] (exact e - 1)
    exact_i = np.e - 1.0
    ns = np.array([2, 4, 8, 16, 32, 64, 128, 256])
    h_i = 1.0 / ns
    et = np.array([abs(trapezoid(np.exp, 0, 1, n) - exact_i) for n in ns])
    es = np.array([abs(simpson(np.exp, 0, 1, n) - exact_i) for n in ns])
    ns4 = ns[:6]
    print(f"order trapezoid: {observed_order(h_i[:6], et[:6]):.2f}; Simpson: {observed_order(h_i[:5], es[:5]):.2f}")
    print(f"n = 16: trapezoid error {et[3]:.1e}, Simpson error {es[3]:.1e}")

    # --- adaptive
    val, evals = adaptive_simpson(peak, 0.0, 1.0, 1e-8)
    print(f"adaptive Simpson on the peak: {val:.10f} (exact {peak_exact():.10f}) with {evals} evaluations")
    for n in (10, 100, 1000):
        print(f"  trapezoid n = {n:<5}: {trapezoid(peak, 0, 1, n):.6f}")
    n_unif = 2
    while abs(simpson(peak, 0, 1, n_unif) - peak_exact()) > 1e-8:
        n_unif *= 2
    print(f"uniform Simpson needs n = {n_unif} ({n_unif + 1} evaluations) for 1e-8")

    # --- failure cases
    kink = lambda x: np.abs(np.asarray(x, dtype=float) - KINK)
    ns_k = np.array([6, 12, 24, 48, 96])
    ek = np.array([abs(simpson(kink, 0, 1, n) - kink_exact()) for n in ns_k])
    print(f"Simpson on |x - {KINK}| (kink between grid points): errors {ek}, order {observed_order(1.0 / ns_k, ek):.2f}")
    print(f"central difference of |x| at 0: {central_diff(np.abs, 0.0, 1e-3)} (true slope does not exist: left -1, right +1)")
    print(f"forward difference of |x| at 0: {forward_diff(np.abs, 0.0, 1e-3)}")

    t_log, v_log = speedometer_log()
    d_raw, d_true = integrate_log(t_log, v_log), float(true_distance(60.0))
    print(f"speedometer log: raw distance {d_raw:.1f} m, true {d_true:.1f} m, error {100 * (d_raw - d_true) / d_true:.2f} %")
    acc = central_diff(lambda tt: np.interp(tt, t_log, v_log), t_log[5:-5], 0.1)
    acc_true = 8.0 * 2 * np.pi / 40.0 * np.cos(2 * np.pi * t_log[5:-5] / 40.0)
    print(f"differentiating the noisy log: acceleration RMS error {np.sqrt(np.mean((acc - acc_true) ** 2)):.2f} m/s^2 (true amplitude 1.26 m/s^2)")

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].loglog(hs, ef, "o-", ms=3, label="forward difference")
    axs[0].loglog(hs, ec, "s-", ms=3, label="central difference")
    axs[0].loglog(hs[:8], 0.5 * hs[:8] * 0.84, "k:", lw=1, label="slope 1")
    axs[0].set_xlabel("step h")
    axs[0].set_ylabel("absolute error of d/dx sin at x = 1")
    axs[0].set_title("Slope methods: error falls, then round-off wins")
    axs[0].invert_xaxis()
    axs[1].loglog(h_i, et, "o-", label="trapezoid (order 2)")
    axs[1].loglog(h_i, es, "s-", label="Simpson (order 4)")
    axs[1].set_xlabel("step h = 1/n")
    axs[1].set_ylabel("absolute error of the integral of e^x on [0, 1]")
    axs[1].set_title("Area methods: error versus step")
    axs[1].invert_xaxis()
    for ax in axs:
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "error_vs_step.png", dpi=120)

    xx = np.linspace(0, 1, 2001)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(xx, peak(xx), label="narrow peak")
    pts = np.linspace(0, 1, 11)
    ax2.plot(pts, peak(pts), "o", color="#d62728", label="10 slices: the samples nearly miss it")
    ax2.set_xlabel("x")
    ax2.set_ylabel("f(x)")
    ax2.set_title("Failure case: a coarse grid misses a spike")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "spike_failure.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. The mini-project (README) puts these tools to work on a noisy speedometer log.
