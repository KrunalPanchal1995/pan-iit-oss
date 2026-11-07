"""Session 3 (Level 3): reaction networks as ODE systems, validated and stress-tested.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: reaction networks as ODEs
# **A. Real-world problem.** In a real flask many steps happen together: A turns into B, B can
# go back, B turns into C; an enzyme grabs a substrate, lets it go or turns it into product.
# Which step limits the output? Does a catalyst help if you put it on the wrong step? We write
# the whole network as one equation, dc/dt = S r(c), solve it with our own Runge-Kutta (RK4)
# code, and check it against exact answers. Simplified models; not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: dc/dt = S r(c)
# * `c` is the vector of concentrations (mol/L), one entry per species.
# * `r(c)` is the vector of reaction rates (mol/(L s)), one entry per reaction.
# * `S` is the stoichiometry matrix: S[i, j] = how many molecules of species i appear (+) or
#   disappear (-) each time reaction j happens once.
#
# A <-> B -> C has three reactions: A -> B (kf), B -> A (kr), B -> C (k2).

# %%
def rk4(f, y0, t_end, h):
    """Classic 4th-order Runge-Kutta with a fixed step h. Returns (t, y) with y[i] = state at t[i]."""
    n = int(round(t_end / h))
    t = np.arange(n + 1) * h
    y = np.empty((n + 1, len(y0)))
    y[0] = y0
    for i in range(n):
        yi = y[i]
        k1 = f(yi)
        k2 = f(yi + 0.5 * h * k1)
        k3 = f(yi + 0.5 * h * k2)
        k4 = f(yi + h * k3)
        y[i + 1] = yi + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y


def abc_network(kf, kr, k2):
    """A <-> B -> C. Returns (S, rates) where rates(c) gives the three reaction rates."""
    S = np.array([[-1, 1, 0],
                  [1, -1, -1],
                  [0, 0, 1]], dtype=float)
    return S, lambda c: np.array([kf * c[0], kr * c[1], k2 * c[1]])


def rhs(S, rates):
    """The ODE right-hand side dc/dt = S r(c) as a function of c."""
    return lambda c: S @ rates(c)


def linear_matrix(kf, kr, k2):
    """For a network of first-order steps, dc/dt = K c. K = S @ (d rates / d c)."""
    return np.array([[-kf, kr, 0.0], [kf, -(kr + k2), 0.0], [0.0, k2, 0.0]])


def exact_linear(K, c0, t):
    """Exact solution c(t) = V exp(L t) V^-1 c0 from the eigen-decomposition of K (distinct eigenvalues)."""
    lam, V = np.linalg.eig(K)
    coef = np.linalg.solve(V, np.asarray(c0, float))
    return np.real(np.array([V @ (coef * np.exp(lam * ti)) for ti in np.atleast_1d(t)]))


# %% [markdown]
# ## Step 2: an enzyme-like cycle and mass conservation
# E + S <-> ES -> E + P. Species order: E, S, ES, P. Reactions: binding (k1), unbinding (km1),
# making product (k2). Two sums must never change: free enzyme + bound enzyme (E + ES), and
# substrate in every form (S + ES + P).

# %%
def enzyme_network(k1, km1, k2):
    S = np.array([[-1, 1, 1],     # E
                  [-1, 1, 0],     # S
                  [1, -1, -1],    # ES
                  [0, 0, 1]], dtype=float)   # P
    return S, lambda c: np.array([k1 * c[0] * c[1], km1 * c[2], k2 * c[2]])


def conserved_sums(c):
    """Columns of c are (E, S, ES, P). Returns the two conserved totals for every time row."""
    return np.column_stack([c[:, 0] + c[:, 2], c[:, 1] + c[:, 2] + c[:, 3]])


def full_enzyme(k1, km1, k2, E0, S0, t_end, h):
    S, rates = enzyme_network(k1, km1, k2)
    return rk4(rhs(S, rates), [E0, S0, 0.0, 0.0], t_end, h)


# %% [markdown]
# ## Step 3: the quasi-steady-state approximation (QSSA)
# If there is little enzyme compared with substrate, ES stays almost constant after a short
# start-up, and the whole cycle collapses to one equation, the Michaelis-Menten rate:
#
#     v = Vmax S / (Km + S),   Vmax = k2 E0,   Km = (km1 + k2) / k1
#
# We compare the product from the full four-species model with the QSSA product, for several
# ratios E0/S0.

# %%
def michaelis_menten(S, Vmax, Km):
    return Vmax * S / (Km + S)


def qssa_product(k1, km1, k2, E0, S0, t_end, h):
    Vmax, Km = k2 * E0, (km1 + k2) / k1
    t, s = rk4(lambda y: np.array([-michaelis_menten(y[0], Vmax, Km)]), [S0], t_end, h)
    return t, S0 - s[:, 0]


def qssa_error(ratio, k1=10.0, km1=5.0, k2=1.0, S0=1.0, h=0.005):
    """Largest |P_full - P_qssa| / S0 until the QSSA says 90 percent of S0 is converted."""
    E0 = ratio * S0
    Vmax, Km = k2 * E0, (km1 + k2) / k1
    t_end = (Km * np.log(10.0) + 0.9 * S0) / Vmax      # integrated Michaelis-Menten equation
    t, y = full_enzyme(k1, km1, k2, E0, S0, t_end, h)
    _, p_q = qssa_product(k1, km1, k2, E0, S0, t_end, h)
    return float(np.abs(y[:, 3] - p_q).max() / S0)


# %% [markdown]
# ## Step 4: the rate-determining step
# In a chain A -> B -> C -> D the slowest step is the bottleneck. Speeding up that step raises
# the yield of D; speeding up another one does almost nothing.

# %%
def chain_yield(ks, t_end, h=None):
    """Yield of the last species of A -> ... (steps with rate constants ks) after t_end, A0 = 1.
    If h is None the step is chosen small enough for the fastest step (h * k_max = 0.1)."""
    if h is None:
        h = min(0.01, 0.1 / max(ks))
    n = len(ks) + 1
    K = np.zeros((n, n))
    for i, k in enumerate(ks):
        K[i, i] -= k
        K[i + 1, i] += k
    c0 = np.zeros(n)
    c0[0] = 1.0
    _, y = rk4(lambda c: K @ c, c0, t_end, h)
    return float(y[-1, -1])


def speed_up_one(ks, i, factor):
    out = list(ks)
    out[i] = out[i] * factor
    return out


# %% [markdown]
# ## Step 5: stiffness - when rate constants differ by 10000
# A -> B at k = 10000 1/s and B -> C at k = 1 1/s. Explicit RK4 is stable only if h * 10000 is
# below about 2.8. A bigger step does not give a "bit of error"; it explodes. An implicit step
# (backward Euler: solve (I - h K) c_new = c_old) stays stable for any h.

# %%
def stiff_matrix(k_fast=1.0e4, k_slow=1.0):
    return np.array([[-k_fast, 0.0, 0.0], [k_fast, -k_slow, 0.0], [0.0, k_slow, 0.0]])


def explicit_rk4_linear(K, c0, t_end, h):
    with np.errstate(all="ignore"):          # an unstable run overflows to inf / nan: that is the point
        return rk4(lambda c: K @ c, c0, t_end, h)


def backward_euler_linear(K, c0, t_end, h):
    n = int(round(t_end / h))
    t = np.arange(n + 1) * h
    y = np.empty((n + 1, len(c0)))
    y[0] = c0
    step = np.linalg.inv(np.eye(len(c0)) - h * K)
    for i in range(n):
        y[i + 1] = step @ y[i]
    return t, y


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    c0 = [1.0, 0.0, 0.0]
    S, rates = abc_network(0.5, 0.2, 0.1)
    t, y = rk4(rhs(S, rates), c0, 30.0, 0.01)
    ex = exact_linear(linear_matrix(0.5, 0.2, 0.1), c0, t)
    print("A <-> B -> C: largest |RK4 - exact| =", f"{np.abs(y - ex).max():.2e}", "; largest |sum - 1| =", f"{np.abs(y.sum(1) - 1).max():.2e}")
    S1, r1 = abc_network(0.5, 0.0, 0.0)
    t1, y1 = rk4(rhs(S1, r1), c0, 10.0, 0.01)
    print("A -> B only: error vs A0 exp(-k t) =", f"{np.abs(y1[:, 0] - np.exp(-0.5 * t1)).max():.2e}")

    fig, ax = plt.subplots(figsize=(6.4, 4))
    for j, name in enumerate("ABC"):
        ax.plot(t, y[:, j], label=f"[{name}] (RK4)")
        ax.plot(t[::300], ex[::300, j], "k.", ms=4)
    ax.plot([], [], "k.", label="exact (eigen-solution)")
    ax.plot(t, y.sum(1), "--", color="gray", label="sum of all three")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("concentration (mol/L)")
    ax.set_title("A <-> B -> C: RK4 agrees with the exact solution")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "abc_network.png", dpi=120)

    # enzyme cycle
    te, ye = full_enzyme(10.0, 5.0, 1.0, 0.1, 1.0, 40.0, 0.005)
    cs = conserved_sums(ye)
    print("enzyme: E+ES drift", f"{np.abs(cs[:, 0] - 0.1).max():.1e}", " S+ES+P drift", f"{np.abs(cs[:, 1] - 1.0).max():.1e}")
    tq, pq = qssa_product(10.0, 5.0, 1.0, 0.1, 1.0, 40.0, 0.005)
    ratios = [0.01, 0.03, 0.1, 0.3, 1.0]
    errs = [qssa_error(r) for r in ratios]
    for r, e in zip(ratios, errs):
        print(f"E0/S0 = {r:5.2f}: largest QSSA error in product = {e:.4f} of S0")
    fig2, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].plot(te, ye[:, 3], label="product P, full model")
    axes[0].plot(tq, pq, "--", label="product P, QSSA (Michaelis-Menten)")
    axes[0].plot(te, ye[:, 2], label="complex ES")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("concentration (mol/L)")
    axes[0].set_title("E0/S0 = 0.1: full model and QSSA", fontsize=9)
    axes[0].legend(fontsize=8)
    axes[1].loglog(ratios, errs, "o-")
    axes[1].set_xlabel("enzyme-to-substrate ratio E0/S0 (no unit)")
    axes[1].set_ylabel("largest error in P / S0 (no unit)")
    axes[1].set_title("QSSA is good when enzyme is scarce", fontsize=9)
    for a in axes:
        a.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "qssa_vs_full.png", dpi=120)

    # rate-determining step
    ks = [0.8, 0.05, 0.6]
    base = chain_yield(ks, 10.0)
    print("chain yield of D at 10 s with k =", ks, ":", round(base, 4))
    for i in range(3):
        print(f"  step {i + 1} made 10 times faster: yield {chain_yield(speed_up_one(ks, i, 10), 10.0):.4f}")

    # stiffness
    K = stiff_matrix()
    ex_s = exact_linear(K, c0, [2.0])[0]
    print("stiff system, exact at t = 2 s:", np.round(ex_s, 4))
    for h in (1e-3, 2e-4, 1e-4):
        tt, yy = explicit_rk4_linear(K, c0, 2.0, h)
        print(f"  explicit RK4, h = {h:g}: B(2 s) = {yy[-1, 1]:.4g}   (h * k_fast = {h * 1e4:g})")
    tb, yb = backward_euler_linear(K, c0, 2.0, 0.05)
    print(f"  backward Euler, h = 0.05 (40 steps): B(2 s) = {yb[-1, 1]:.4f}, error {abs(yb[-1, 1] - ex_s[1]):.1e}")
    fig3, ax3 = plt.subplots(figsize=(6.4, 4))
    tt, yy = explicit_rk4_linear(K, c0, 0.05, 1e-3)
    ax3.semilogy(tt, np.abs(yy[:, 1]) + 1e-12, label="explicit RK4, h = 1e-3 (blows up)")
    tt, yy = explicit_rk4_linear(K, c0, 0.05, 1e-4)
    ax3.semilogy(tt, np.abs(yy[:, 1]) + 1e-12, label="explicit RK4, h = 1e-4 (stable)")
    ax3.set_xlabel("time (s)")
    ax3.set_ylabel("|[B]| (mol/L), log scale")
    ax3.set_title("Stiffness: step too large for the fastest rate")
    ax3.grid(alpha=0.3, which="both")
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "stiffness.png", dpi=120)

# %% [markdown]
# ## Where this stops
# All steps here are mass-action steps at one fixed temperature. Real networks have many more
# species, temperature changes and heat release; the roadmap points to that.
