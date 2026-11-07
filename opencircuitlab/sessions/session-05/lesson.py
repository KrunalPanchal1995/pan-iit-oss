"""Session 5 (Level 3): a nonlinear part. A diode inside the nodal solver, solved by Newton's method.

Run:  python start.py 5
Low-voltage educational circuits only (never mains). Ideal sources, linear resistors, Shockley diodes.
"""
# %% [markdown]
# # Session 5: the diode and Newton's method
# **A. Real-world problem.** Every part so far obeyed Ohm's law, so one matrix equation `G v = i` solved
# the whole circuit. A diode does not: its current grows *exponentially* with the voltage across it, so
# there is no fixed conductance to put in `G`. Yet a diode on a 5 V supply with a 1 kohm resistor is the
# simplest LED circuit there is. Today we keep the linear solver of Session 3 and put a loop around it:
# at each pass we replace the diode by the resistor and current source that match it *at the present
# voltage* (its tangent line), solve, and repeat until Kirchhoff's current law (KCL) holds. That is
# Newton's method, and it is inside every circuit simulator.
#
# **Plan.** (1) the diode law and its tangent, (2) one Newton step by hand, (3) the loop around the
# solver, (4) watch the plain loop fail, (5) the voltage limiter that repairs it, (6) check against an
# independent solution, (7) the mini-project: choose the resistor.

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 0: the linear solver from Session 3
# Unchanged. Take it as a black box: it solves `G v = i` for any network of resistors and ideal sources.

# %%
def solve_network(n_nodes, resistors, vsources=(), isources=()):
    """Solve a resistor network. Nodes are 0 (ground) to n_nodes.

    resistors: (a, b, ohm). vsources: (plus, minus, volts). isources: (a, b, amperes): the
    source pushes that current from node a, through itself, into node b.
    Returns (v, j): node voltages v[0..n_nodes] (v[0] = 0) and the current j[k] that each
    voltage source delivers (positive = the source is supplying power).
    Raises ValueError for a floating node or contradictory sources (singular matrix).
    """
    n, m = n_nodes, len(vsources)
    size = n + m
    a = np.zeros((size, size))
    rhs = np.zeros(size)
    for na, nb, r in resistors:
        if r <= 0:
            raise ValueError("resistance must be positive (a 0 ohm wire is a short circuit)")
        g = 1.0 / r
        for p, q, s in ((na, na, g), (nb, nb, g), (na, nb, -g), (nb, na, -g)):
            if p > 0 and q > 0:
                a[p - 1, q - 1] += s
    for na, nb, cur in isources:
        if na > 0:
            rhs[na - 1] -= cur
        if nb > 0:
            rhs[nb - 1] += cur
    for k, (p, q, volts) in enumerate(vsources):
        if p > 0:
            a[p - 1, n + k] -= 1.0
            a[n + k, p - 1] += 1.0
        if q > 0:
            a[q - 1, n + k] += 1.0
            a[n + k, q - 1] -= 1.0
        rhs[n + k] = volts
    if size == 0:
        return np.zeros(1), np.zeros(0)
    if np.linalg.cond(a) > 1e12:
        raise ValueError("singular matrix: a node is floating (no path to ground) or sources contradict each other")
    x = np.linalg.solve(a, rhs)
    return np.concatenate(([0.0], x[:n])), x[n:]


# %% [markdown]
# ## Step 1: the diode law and its tangent
# A silicon diode follows the Shockley law: `I = Is (exp(V / (n VT)) - 1)`.
# * `Is` is the saturation (leakage) current, here 1e-12 A; `n` = 1 is the ideality factor;
# * `VT = k T / q` is the thermal voltage, 25.852 mV at 300 K.
# Below about 0.4 V it carries almost nothing; every extra `n VT ln 10` = 60 mV multiplies the current
# by ten. The slope `g = dI/dV = (I + Is) / (n VT)` is the **conductance at that voltage**. The tangent
# line at the voltage `V0` is `I = g V + i_eq` with `i_eq = I(V0) - g V0`: a resistor `1/g` in parallel
# with a current source `i_eq`. That pair is the diode's **companion model**.

# %%
IS, NVT = 1e-12, 0.025852          # saturation current (A) and n x thermal voltage (V), 300 K
GMIN = 1e-12                       # tiny conductance added across every diode (as SPICE does)
EXP_MAX = 700.0                    # exp() overflows above 709; the model is clamped there


def diode_current(v, i_s=IS, nvt=NVT):
    """Current (A) through the diode from anode to cathode for the voltage v (V) across it."""
    return i_s * (math.exp(min(v / nvt, EXP_MAX)) - 1.0)


def diode_conductance(v, i_s=IS, nvt=NVT):
    """Slope dI/dV (S) of the diode law at v, plus GMIN."""
    return i_s / nvt * math.exp(min(v / nvt, EXP_MAX)) + GMIN


def diode_voltage(i, i_s=IS, nvt=NVT):
    """Inverse law: the voltage across the diode that carries the current i (A, positive)."""
    return nvt * math.log(i / i_s + 1.0)


def companion(v0, i_s=IS, nvt=NVT):
    """Tangent of the diode law at v0: returns (g, i_eq) with I(v) ~ g v + i_eq near v0."""
    g = diode_conductance(v0, i_s, nvt)
    return g, diode_current(v0, i_s, nvt) - g * v0


# %% [markdown]
# ## Step 2: one Newton step by hand
# A source `Vs` feeds a resistor `R` and a diode in series. The only unknown is the diode voltage `Vd`.
# KCL at the diode node: `(Vd - Vs)/R + I(Vd) = 0`. Replace `I(Vd)` by its tangent at the guess `V0`:
#
#     (Vd - Vs)/R + g Vd + i_eq = 0     so     Vd = (Vs / R - i_eq) / (1 / R + g)
#
# That is a *linear* equation: one Newton step. The new `Vd` becomes the next guess.

# %%
def newton_step_series(vs, r, v0):
    """One Newton step for the series circuit Vs - R - diode - ground, from the guess v0 for the diode voltage."""
    g, i_eq = companion(v0)
    return (vs / r - i_eq) / (1.0 / r + g)


# %% [markdown]
# ## Step 3: the loop around the solver
# For a whole network the same idea is done with the Session 3 solver as it is:
# 1. guess all node voltages (start at 0 V);
# 2. replace every diode by its companion (a resistor `1/g` and a current source `i_eq`);
# 3. call `solve_network`;
# 4. compute the **KCL residual** of that solution: at every node, the sum of the *true* (nonlinear)
#    currents leaving it, which is the amount by which KCL fails. Stop when every residual is below
#    `tol` = 1e-9 A and each diode voltage agrees with the one it was linearised at; otherwise make the
#    solution the new working point and go to 2.
# Diodes are given as `(anode, cathode)`; the voltage-source currents `j` are part of the state.

# %%
class NewtonError(ValueError):
    """The iteration did not converge, or the linear solve failed."""


def kcl_residual(n_nodes, resistors, vsources, isources, diodes, v, j):
    """KCL residual (A) at nodes 1..n: sum of currents leaving each node, using the true diode law."""
    res = np.zeros(n_nodes + 1)
    for a, b, r in resistors:
        i = (v[a] - v[b]) / r
        res[a] += i
        res[b] -= i
    for d in diodes:
        i = diode_current(v[d[0]] - v[d[1]])
        res[d[0]] += i
        res[d[1]] -= i
    for a, b, cur in isources:
        res[a] += cur
        res[b] -= cur
    for k, (p, q, _) in enumerate(vsources):
        res[p] -= j[k]
        res[q] += j[k]
    return res[1:]


def limit_step(vd_old, vd_new, nvt=NVT):
    """Limit a rising diode voltage: a step dv is shortened to nvt ln(1 + dv / nvt). Falling steps are kept."""
    if vd_new <= vd_old:
        return vd_new
    return vd_old + nvt * math.log(1.0 + (vd_new - vd_old) / nvt)


def newton_solve(n_nodes, resistors, vsources=(), isources=(), diodes=(), limit=True, tol=1e-9, vtol=1e-6, max_iter=50, v0=None):
    """Solve a network with diodes by Newton's method around solve_network.

    v0: starting voltage across each diode (a list, default 0 V). Each pass linearises every diode at its
    working voltage, solves, and measures the KCL residual of the solution with the true diode law. The loop
    stops when the residual is below tol (A) and every diode voltage agrees with the voltage it was linearised
    at to within vtol (V). With limit=True a rising working voltage is shortened by limit_step.

    Returns a dict: v (node voltages), j (source currents), iterations, residual (largest KCL residual, A)
    and history (a list of (iteration, residual, working voltage of the first diode)).
    Raises NewtonError when the linear solve fails or max_iter is reached.
    """
    n = n_nodes
    work = [0.0] * len(diodes) if v0 is None else [float(x) for x in v0]
    history = []
    for it in range(1, max_iter + 1):
        extra_r, extra_i = [], []
        for (a, b), w in zip(diodes, work):
            g, i_eq = companion(w)
            extra_r.append((a, b, 1.0 / g))
            extra_i.append((a, b, i_eq))
        try:
            v, j = solve_network(n, list(resistors) + extra_r, vsources, list(isources) + extra_i)
        except ValueError as e:
            raise NewtonError(f"iteration {it}: the linear solve failed ({e})") from None
        res = float(np.abs(kcl_residual(n, resistors, vsources, isources, diodes, v, j)).max())
        proposed = [float(v[a] - v[b]) for a, b in diodes]
        history.append((it, res, work[0] if diodes else 0.0))
        if res < tol and all(abs(p - w) < vtol for p, w in zip(proposed, work)):
            return {"v": v, "j": j, "iterations": it, "residual": res, "history": history}
        work = [limit_step(w, p) if limit else p for w, p in zip(work, proposed)]
    raise NewtonError(f"no convergence in {max_iter} iterations (residual {res:.2e} A)")


# %% [markdown]
# ## Step 4: the plain loop fails, and why
# Run the loop with `limit=False` on the 5 V, 1 kohm circuit. At the first pass the diode is at 0 V, where
# its conductance is almost nothing, so the linearised diode is nearly an open circuit and the solver puts
# nearly all 5 V across it. The second pass then linearises the exponential at 5 V, where the conductance
# is about 1e61 siemens: the matrix is hopelessly ill-conditioned and the solver gives up. The tangent was
# a fine local model and a terrible guide for a big step.

# %%
SERIES = dict(n_nodes=2, resistors=[(1, 2, 1000.0)], vsources=[(1, 0, 5.0)], diodes=[(2, 0)])


def plain_newton_fails(**kw):
    """Run the loop without limiting on a network; return the error message, or None if it converged."""
    try:
        newton_solve(**{**SERIES, **kw}, limit=False)
    except NewtonError as e:
        return str(e)
    return None


# %% [markdown]
# ## Step 5: the limiter
# SPICE-style fix: never let the diode voltage *rise* by more than `n VT ln(1 + dv / n VT)` where `dv` is
# the step the linear solve asked for. For `dv` = 5 V that is only 0.136 V. The node voltages of each
# solve are kept as they are; only the point at which the *next* pass linearises the diode is shortened.
# Because the exponential is so steep, short steps keep the tangent honest. Falling steps are not limited.
# With the limiter the same circuit converges in 8 passes: the working voltage creeps up to 0.574 V and
# then the residual collapses from 2.5 mA through 1e-5 and 1e-12 to 1e-17 A.

# %%
def series_diode(vs, r, limit=True, **kw):
    """Diode in series with a resistor on a source. Returns (diode voltage, current, iterations)."""
    net = newton_solve(2, [(1, 2, r)], [(1, 0, vs)], diodes=[(2, 0)], limit=limit, **kw)
    return float(net["v"][2]), float((net["v"][1] - net["v"][2]) / r), net["iterations"]


# %% [markdown]
# ## Step 6: an independent check
# A converged residual proves KCL holds at the answer, but a second method guards against a wrong model.
# For the series circuit there is one unknown, so we can find the root of `f(Vd) = (Vs - Vd)/R - I(Vd)`
# by **bisection**: `f` falls from positive at 0 V to negative at `Vs`; keep halving the interval that
# contains the sign change. No derivatives, no matrices, so it shares nothing with the Newton code.

# %%
def series_diode_exact(vs, r, i_s=IS, nvt=NVT):
    """Diode voltage and current of the series circuit by bisection (independent of the Newton code)."""
    lo, hi = min(0.0, vs), max(0.0, vs)
    f = lambda vd: (vs - vd) / r - diode_current(vd, i_s, nvt)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if (f(mid) > 0) == (f(lo) > 0):
            lo = mid
        else:
            hi = mid
    vd = 0.5 * (lo + hi)
    return vd, (vs - vd) / r


def load_line_point(vs, r, v):
    """Current the resistor allows at diode voltage v: the load line I = (Vs - V) / R."""
    return (vs - v) / r


# a network where the diode sits between two resistors (nothing here is a simple series formula
# for the solver, but the loop is still one unknown, so bisection can check it)
TWO_RESISTOR = dict(n_nodes=3, resistors=[(1, 2, 1000.0), (3, 0, 470.0)], vsources=[(1, 0, 9.0)], diodes=[(2, 3)])


def two_resistor_exact():
    """Series loop 9 V - 1000 - diode - 470: bisection on the loop current."""
    vd, i = series_diode_exact(9.0, 1470.0)
    return vd, i


# %% [markdown]
# ## Step 7: how good is "the diode drops 0.7 V"?
# By hand we replace the diode by a fixed drop of 0.6 or 0.7 V. The loop lets us measure the error that
# costs, over a wide range of resistors. (The right fixed drop depends on the current: 60 mV per decade.)

# %%
def constant_drop_error(vs, r, drop):
    """Relative error of the current found with a fixed diode drop, against the exact current."""
    exact = series_diode_exact(vs, r)[1]
    return ((vs - drop) / r - exact) / exact


# %% [markdown]
# ## Step 8: mini-project tools (choose the resistor)
# A 5 V supply that may be anywhere from 4.5 V to 5.5 V lights a diode (an indicator) through a series
# resistor from the E12 series. The current must be at least 3 mA at 4.5 V (so that it is visible) and at
# most 10 mA at 5.5 V (so that it is safe). Among the resistors that work, take the largest: it wastes the
# least power.

# %%
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E12_OHM = [round(m * 10 ** k, 1) for k in range(1, 5) for m in E12]


def indicator_table(rs=E12_OHM, v_lo=4.5, v_hi=5.5):
    """For each resistor: (R, current at v_lo, current at v_hi, diode voltage at v_hi, power in R at v_hi)."""
    rows = []
    for r in rs:
        _, i_lo = series_diode_exact(v_lo, r)
        vd, i_hi = series_diode_exact(v_hi, r)
        rows.append((r, i_lo, i_hi, vd, i_hi * i_hi * r))
    return rows


def choose_indicator_resistor(rs=E12_OHM, i_min=3e-3, i_max=10e-3):
    """Largest E12 resistor with i(4.5 V) >= i_min and i(5.5 V) <= i_max, and the table row; (None, None) if none."""
    ok = [row for row in indicator_table(rs) if row[1] >= i_min and row[2] <= i_max]
    return (ok[-1][0], ok[-1]) if ok else (None, None)


# %% [markdown]
# ## See it
# Figure 1: the load line meets the diode curve; the Newton iterates climb up the curve (with and without
# the limiter). Figure 2: the residual against the pass number. Figure 3: the diode voltage
# against the supply for three resistors, and the 0.7 V rule.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA, GREY = "#0072b2", "#c86a00", "#d81b60", "#555555"
    vd, i = series_diode_exact(5.0, 1000.0)
    print(f"series 5 V, 1 kohm, diode: exact Vd = {vd:.6f} V, I = {1000 * i:.4f} mA")
    net = newton_solve(**SERIES)
    print(f"  Newton with limiter: {net['iterations']} passes, residual {net['residual']:.1e} A, Vd = {net['v'][2]:.6f} V")
    for it, res, v_ in net["history"]:
        print(f"    pass {it}: linearised at Vd = {v_:.4f} V, residual of the solution {res:.2e} A")
    print("  plain Newton:", plain_newton_fails())
    print("  one hand step from 0.6 V:", round(newton_step_series(5.0, 1000.0, 0.6), 6), "V")
    for v0 in (0.7, 0.6, 0.3):
        try:
            k = newton_solve(**SERIES, limit=False, v0=[v0])["iterations"]
        except NewtonError as e:
            k = f"fails ({str(e)[:40]}...)"
        print(f"  plain Newton starting at Vd = {v0} V: {k}")
    t = newton_solve(**TWO_RESISTOR)
    print("  two-resistor circuit: passes", t["iterations"], " Vd =", round(float(t["v"][2] - t["v"][3]), 6), "exact:", round(two_resistor_exact()[0], 6))
    rev = newton_solve(2, [(1, 2, 1000.0)], [(1, 0, 5.0)], diodes=[(0, 2)])
    print("  reversed diode: I =", f"{1000 * rev['j'][0]:.3e}", "mA, passes", rev["iterations"])
    for r_ in (100.0, 1000.0, 10000.0):
        print(f"  constant-drop error at R = {r_:.0f}: 0.7 V {100 * constant_drop_error(5.0, r_, 0.7):+.1f} %, 0.6 V {100 * constant_drop_error(5.0, r_, 0.6):+.1f} %")
    best, row = choose_indicator_resistor()
    print("indicator: chosen R =", best, "ohm; row (R, I at 4.5 V, I at 5.5 V, Vd at 5.5 V, P_R at 5.5 V) =", [f"{x:.4g}" for x in row])
    for r_, a, b, c, d in indicator_table([470, 560, 1000, 1200, 1500]):
        print(f"   {r_:6.0f} ohm: {1000 * a:5.2f} mA at 4.5 V, {1000 * b:5.2f} mA at 5.5 V, P_R {1000 * d:5.1f} mW")

    # Figure 1: load line and the iterates
    fig1, ax1 = plt.subplots(figsize=(7, 4.2))
    vv = np.linspace(0, 0.8, 400)
    ax1.plot(vv, [1000 * diode_current(x) for x in vv], color=BLUE, lw=2, label="diode curve")
    ax1.plot(vv, [1000 * load_line_point(5.0, 1000.0, x) for x in vv], color=ORANGE, lw=2, label="load line (5 V, 1 kohm)")
    its = [h[2] for h in net["history"]]
    ax1.plot(its, [1000 * diode_current(x) for x in its], "o", color=MAGENTA, ms=6, label="Newton iterates (limited)")
    for k, x in enumerate(its[:6]):
        ax1.annotate(str(k + 1), (x, 1000 * diode_current(x)), textcoords="offset points", xytext=(-9, 6), fontsize=8)
    ax1.plot([vd], [1000 * i], "k*", ms=12, label="solution %.3f V, %.2f mA" % (vd, 1000 * i))
    ax1.set_ylim(-0.3, 5.5)
    ax1.set_xlabel("voltage across the diode (V)")
    ax1.set_ylabel("current (mA)")
    ax1.set_title("The solution is where the load line meets the diode curve")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8)
    fig1.tight_layout()
    fig1.savefig(OUT / "load_line.png", dpi=120)

    # Figure 2: residual per pass for several starts, with the limiter
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    for kw, col, lab in ((dict(), BLUE, "start 0 V, limited"), (dict(v0=[0.7]), ORANGE, "start 0.7 V, limited")):
        h = newton_solve(**SERIES, **kw)["history"]
        ax2.semilogy([x[0] for x in h], [max(x[1], 1e-18) for x in h], "o-", color=col, label=lab)
    h = newton_solve(**SERIES, limit=False, v0=[0.7])["history"]
    ax2.semilogy([x[0] for x in h], [max(x[1], 1e-18) for x in h], "s--", color=GREY, label="start 0.7 V, plain")
    ax2.axhline(1e-9, color=MAGENTA, ls=":", lw=2, label="tolerance 1e-9 A")
    ax2.set_xlabel("pass number")
    ax2.set_ylabel("largest KCL residual (A)")
    ax2.set_title("The residual falls quickly once the iterate is near the solution")
    ax2.grid(alpha=0.3, which="major")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "residual.png", dpi=120)

    # Figure 3: diode voltage against the supply
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    vs_ = np.linspace(1.0, 12.0, 111)
    for r_, col in ((220.0, ORANGE), (1000.0, BLUE), (10000.0, GREY)):
        ax3.plot(vs_, [series_diode_exact(x, r_)[0] for x in vs_], color=col, lw=2, label=f"R = {r_:.0f} ohm")
    ax3.axhline(0.7, color=MAGENTA, ls="--", lw=1.5, label="the 0.7 V rule")
    ax3.set_xlabel("supply voltage (V)")
    ax3.set_ylabel("voltage across the diode (V)")
    ax3.set_title("The diode voltage moves only 0.1 V while the supply moves 11 V")
    ax3.set_ylim(0.3, 0.8)
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "diode_voltage.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
