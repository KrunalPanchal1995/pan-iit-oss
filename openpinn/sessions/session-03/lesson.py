"""Session 3 (Level 3): a physics-informed network for the 1D heat equation, validated, then used backwards.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: solve the heat equation with a network, and recover the diffusivity
# **A. Real-world problem.** A thin metal rod of length 1 (scaled units) has both ends held at
# temperature 0 and starts with a smooth hump of heat, `u(x, 0) = sin(pi x)`. Heat leaks out and
# the rod cools according to the heat equation `u_t = alpha u_xx`, where `alpha` is the
# diffusivity. The exact answer is `sin(pi x) exp(-alpha pi^2 t)`. We ask a network `u(x, t)` to
# satisfy the equation, the ends and the start, and we check it against the exact answer and
# against a classical finite-difference solver. Then we turn the problem around: given a few
# noisy readings, find `alpha`.
#
# **Honest warning.** For this easy forward problem a classical solver is far cheaper and more
# accurate. The point is the recipe, and the inverse problem where the network earns its keep.
# This is a simplified teaching model, not a validated engineering tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ALPHA = 0.1          # true diffusivity (scaled units: length^2 per time)


# %% [markdown]
# ## Step 1: the network and its derivatives, by hand
# One hidden layer of H tanh units: with `z_j = a_j x + b_j t + d_j` and `th_j = tanh(z_j)`,
#
#     u = sum_j c_j th_j + e
#
# Let `s = 1 - th^2` (the slope of tanh), `s2 = -2 th s` (its second derivative) and
# `s3 = s (6 th^2 - 2)` (its third derivative). The chain rule gives
#
#     u_t  = sum_j c_j b_j s_j
#     u_xx = sum_j c_j a_j^2 s2_j
#
# The residual of the heat equation is `r = u_t - alpha u_xx`.

# %%
def init_net(n_units, seed=0):
    rng = np.random.default_rng(seed)
    return {"a": rng.normal(0.0, 2.0, n_units), "b": rng.normal(0.0, 1.0, n_units),
            "d": rng.normal(0.0, 1.0, n_units), "c": rng.normal(0.0, 1.0 / np.sqrt(n_units), n_units),
            "e": np.zeros(1)}


def forward(P, x, t):
    """Return u, u_t, u_xx at the points (x_i, t_i) and a cache for the backward pass."""
    th = np.tanh(np.outer(x, P["a"]) + np.outer(t, P["b"]) + P["d"])
    s = 1.0 - th ** 2
    s2 = -2.0 * th * s
    s3 = s * (6.0 * th ** 2 - 2.0)
    u = th @ P["c"] + P["e"][0]
    u_t = s @ (P["c"] * P["b"])
    u_xx = s2 @ (P["c"] * P["a"] ** 2)
    return u, u_t, u_xx, (th, s, s2, s3)


# %% [markdown]
# ## Step 2: backpropagation through the derivatives
# A loss depends on the network through `u`, `u_t` and `u_xx` at the points. Given how the loss
# changes with each of them (`gu`, `gut`, `guxx`) the parameter gradients are sums of
#
#     u:     dc = th        da = c s x                       db = c s t                         dd = c s
#     u_t:   dc = b s       da = c b s2 x                    db = c (s + b s2 t)                dd = c b s2
#     u_xx:  dc = a^2 s2    da = c (2 a s2 + a^2 s3 x)       db = c a^2 s3 t                    dd = c a^2 s3
#
# (each row is d(quantity)/d(parameter) for hidden unit j; "x" and "t" are the point coordinates).

# %%
def backward(P, x, t, cache, gu, gut, guxx):
    th, s, s2, s3 = cache
    a, b, c = P["a"], P["b"], P["c"]
    X, T = x[:, None], t[:, None]
    gu_, gut_, guxx_ = gu[:, None], gut[:, None], guxx[:, None]
    return {
        "c": gu @ th + gut @ (s * b) + guxx @ (s2 * a ** 2),
        "a": (gu_ * c * s * X + gut_ * c * b * s2 * X + guxx_ * c * (2 * a * s2 + a ** 2 * s3 * X)).sum(axis=0),
        "b": (gu_ * c * s * T + gut_ * c * (s + b * s2 * T) + guxx_ * c * a ** 2 * s3 * T).sum(axis=0),
        "d": (gu_ * c * s + gut_ * c * b * s2 + guxx_ * c * a ** 2 * s3).sum(axis=0),
        "e": np.array([gu.sum()]),
    }


# %% [markdown]
# ## Step 3: the key correctness check
# Compare the formulas for `u_t` and `u_xx` with central finite differences of `u` itself, and
# the parameter gradients with finite differences of a loss. If either disagrees, training
# would silently solve the wrong problem.

# %%
def derivative_check(h=1e-4):
    """Largest gaps: (u_t formula vs finite difference, u_xx formula vs finite difference)."""
    P = init_net(8, 0)
    x = np.array([0.3, 0.7, 0.45])
    t = np.array([0.2, 0.5, 0.9])
    u, u_t, u_xx, _ = forward(P, x, t)
    fd_t = (forward(P, x, t + h)[0] - forward(P, x, t - h)[0]) / (2 * h)
    fd_xx = (forward(P, x + h, t)[0] - 2 * u + forward(P, x - h, t)[0]) / h ** 2
    return float(np.abs(u_t - fd_t).max()), float(np.abs(u_xx - fd_xx).max())


def gradient_check(h=1e-6):
    """Largest relative gap between hand gradients and finite-difference gradients of a test loss."""
    P = init_net(6, 1)
    x = np.array([0.3, 0.7])
    t = np.array([0.2, 0.5])

    def loss(Q):
        u, u_t, u_xx, _ = forward(Q, x, t)
        return float(np.sum(u ** 2) + 0.7 * np.sum(u_t ** 2) + 0.3 * np.sum(u_xx ** 2))

    u, u_t, u_xx, cache = forward(P, x, t)
    G = backward(P, x, t, cache, 2 * u, 2 * 0.7 * u_t, 2 * 0.3 * u_xx)
    worst = 0.0
    for key in P:
        for i in range(len(P[key])):
            Pp = {k: v.copy() for k, v in P.items()}
            Pm = {k: v.copy() for k, v in P.items()}
            Pp[key][i] += h
            Pm[key][i] -= h
            fd = (loss(Pp) - loss(Pm)) / (2 * h)
            worst = max(worst, abs(fd - G[key][i]) / max(1.0, abs(fd)))
    return worst


# %% [markdown]
# ## Step 4: the loss and the training loop (Adam, by hand)
# Three pieces, each a mean of squares:
#
#     residual  = mean of (u_t - alpha u_xx)^2 at N random points inside the rod and time span
#     boundary  = mean of u(0, t)^2 and u(1, t)^2 at points along the two ends
#     initial   = mean of (u(x, 0) - sin(k pi x))^2 along the start
#
#     loss = w_res * residual + boundary + initial
#
# `w_res` is the weight of the physics term. For the inverse problem a fourth piece compares
# the network with the noisy readings and `alpha` becomes a trainable number.

# %%
def exact(x, t, alpha=ALPHA, k=1):
    return np.sin(k * np.pi * x) * np.exp(-alpha * (k * np.pi) ** 2 * t)


def _adam(P, G, state, lr, step, lr_scale=None):
    m, v = state
    for key in P:
        m[key] = 0.9 * m[key] + 0.1 * G[key]
        v[key] = 0.999 * v[key] + 0.001 * G[key] ** 2
        rate = lr * (lr_scale or {}).get(key, 1.0)
        P[key] -= rate * (m[key] / (1 - 0.9 ** step)) / (np.sqrt(v[key] / (1 - 0.999 ** step)) + 1e-8)


def train_pinn(alpha=ALPHA, n_units=20, steps=1000, n_col=200, w_res=1.0, k=1, seed=0, lr=5e-3,
               readings=None, alpha_start=None, w_data=1.0, record_every=50):
    """Train a PINN. With `readings=(x, t, u)` and `alpha_start`, alpha is a trainable parameter.

    Returns (P, alpha_final, history) where history has the loss pieces and alpha every `record_every` steps."""
    rng = np.random.default_rng(seed)
    P = init_net(n_units, seed)
    xc, tc = rng.random(n_col), rng.random(n_col)
    s_ = np.linspace(0.0, 1.0, 50)
    xb, tb = np.r_[np.zeros(50), np.ones(50)], np.r_[s_, s_]
    xi, ti = s_, np.zeros(50)
    ui_target = np.sin(k * np.pi * xi)
    inverse = readings is not None
    if inverse:
        P["alpha"] = np.array([float(alpha_start)])
        xo, to, uo = readings
    state = ({key: np.zeros_like(v) for key, v in P.items()}, {key: np.zeros_like(v) for key, v in P.items()})
    hist = {"step": [], "residual": [], "boundary": [], "initial": [], "data": [], "alpha": []}
    for step in range(1, steps + 1):
        al = P["alpha"][0] if inverse else alpha
        u, u_t, u_xx, cache = forward(P, xc, tc)
        r = u_t - al * u_xx
        ub, _, _, cache_b = forward(P, xb, tb)
        ui, _, _, cache_i = forward(P, xi, ti)
        g_r = w_res * 2.0 * r / n_col
        G1 = backward(P, xc, tc, cache, np.zeros_like(r), g_r, -al * g_r)
        G2 = backward(P, xb, tb, cache_b, 2.0 * ub / len(xb), np.zeros_like(ub), np.zeros_like(ub))
        G3 = backward(P, xi, ti, cache_i, 2.0 * (ui - ui_target) / len(xi), np.zeros_like(ui), np.zeros_like(ui))
        G = {key: G1[key] + G2[key] + G3[key] for key in G1}
        data_loss = 0.0
        if inverse:
            uu, _, _, cache_o = forward(P, xo, to)
            G4 = backward(P, xo, to, cache_o, w_data * 2.0 * (uu - uo) / len(xo), np.zeros_like(uu), np.zeros_like(uu))
            G = {key: G[key] + G4[key] for key in G4}
            G["alpha"] = np.array([-np.sum(g_r * u_xx)])
            data_loss = float(np.mean((uu - uo) ** 2))
        _adam(P, G, state, lr, step, {"alpha": 2.0} if inverse else None)
        if step % record_every == 0 or step == 1:
            hist["step"].append(step)
            hist["residual"].append(float(np.mean(r ** 2)))
            hist["boundary"].append(float(np.mean(ub ** 2)))
            hist["initial"].append(float(np.mean((ui - ui_target) ** 2)))
            hist["data"].append(data_loss)
            hist["alpha"].append(float(al))
    alpha_final = float(P["alpha"][0]) if inverse else float(alpha)
    return P, alpha_final, hist


def rel_l2_error(P, alpha=ALPHA, k=1, n=101):
    """Relative L2 error of the network against the exact solution on an n x n grid of (x, t)."""
    g = np.linspace(0.0, 1.0, n)
    X, T = np.meshgrid(g, g)
    x, t = X.ravel(), T.ravel()
    u = forward(P, x, t)[0]
    ex = exact(x, t, alpha, k)
    return float(np.linalg.norm(u - ex) / np.linalg.norm(ex))


# %% [markdown]
# ## Step 5: the classical reference
# Explicit finite differences on `nx` intervals: each interior value moves towards the average
# of its two neighbours,
#
#     u_i(new) = u_i + r (u_{i-1} - 2 u_i + u_{i+1}),    r = alpha dt / dx^2
#
# This is stable only for `r <= 1/2`. With a tiny alternating ripple added to the start
# (`noise`), an unstable `r` makes the ripple explode.

# %%
def fd_heat(alpha=ALPHA, nx=20, r=0.4, t_end=1.0, noise=0.0):
    """Explicit scheme to time t_end. Returns (x, u, n_steps, dt)."""
    dx = 1.0 / nx
    x = np.linspace(0.0, 1.0, nx + 1)
    dt = r * dx ** 2 / alpha
    n_steps = int(round(t_end / dt))
    u = np.sin(np.pi * x)
    u[1:-1] += noise * (-1.0) ** np.arange(1, nx)
    for _ in range(n_steps):
        u[1:-1] = u[1:-1] + r * (u[:-2] - 2 * u[1:-1] + u[2:])
        u[0] = u[-1] = 0.0
    return x, u, n_steps, dt


def fd_error(alpha=ALPHA, nx=20, r=0.4, t_end=1.0):
    x, u, n_steps, dt = fd_heat(alpha, nx, r, t_end)
    ex = exact(x, n_steps * dt)
    return float(np.linalg.norm(u - ex) / np.linalg.norm(ex))


def pinn_error_at_time(P, t_end=1.0, alpha=ALPHA, n=101):
    x = np.linspace(0.0, 1.0, n)
    t = np.full(n, t_end)
    ex = exact(x, t, alpha)
    return float(np.linalg.norm(forward(P, x, t)[0] - ex) / np.linalg.norm(ex))


# %% [markdown]
# ## Step 6: the inverse problem
# Thirty noisy readings of the temperature at random places and times, `alpha` unknown. We keep
# the same network and loss, add a data term, and let `alpha` be trained together with the
# weights. The classical alternative when the form of the answer is known is to fit one number
# to the readings directly; we compute that too.

# %%
def make_readings(alpha=ALPHA, n=30, sigma=0.02, seed=0):
    rng = np.random.default_rng(seed + 1000)
    x, t = rng.uniform(0.05, 0.95, n), rng.uniform(0.05, 1.0, n)
    return x, t, exact(x, t, alpha) + sigma * rng.normal(size=n)


def fit_alpha_direct(readings):
    """Best alpha for u = sin(pi x) exp(-alpha pi^2 t) by scanning (valid only if that form is known)."""
    x, t, u = readings
    grid = np.linspace(0.005, 0.6, 5951)
    sse = ((np.sin(np.pi * x)[None, :] * np.exp(-grid[:, None] * np.pi ** 2 * t[None, :]) - u[None, :]) ** 2).sum(axis=1)
    return float(grid[np.argmin(sse)])


# %%
if __name__ == "__main__":
    import time

    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    d_t, d_xx = derivative_check()
    print(f"u_t formula vs finite difference: {d_t:.1e};  u_xx formula vs finite difference: {d_xx:.1e}")
    print(f"parameter gradients vs finite differences, worst relative gap: {gradient_check():.1e}")

    t0 = time.time()
    P, _, hist = train_pinn()
    err = rel_l2_error(P)
    print(f"PINN (20 units, 200 points, 1000 steps): relative L2 error {err:.4f}  ({time.time() - t0:.1f} s)")
    print(f"final loss pieces: residual {hist['residual'][-1]:.2e}, boundary {hist['boundary'][-1]:.2e}, "
          f"initial {hist['initial'][-1]:.2e}")
    x_fd, u_fd, n_steps, dt = fd_heat()
    print(f"finite differences (20 intervals, r = 0.4): {n_steps} steps of dt = {dt:.2f}, error at t = 1: "
          f"{fd_error():.5f}; PINN error at t = 1: {pinn_error_at_time(P):.4f}")
    x_u, u_u, _, _ = fd_heat(r=0.6, noise=1e-3)
    print(f"unstable r = 0.6: largest |u| at t = 1 is {np.abs(u_u).max():.1e} (should be below 1)")

    print("\nweight of the physics term (1000 steps):")
    for w in (0.01, 1.0, 100.0):
        Pw = P if w == 1.0 else train_pinn(w_res=w)[0]
        print(f"  w_res = {w:6.2f}: relative L2 error {rel_l2_error(Pw):.4f}")
    print("number of collocation points:")
    for n in (5, 20, 200):
        Pn = P if n == 200 else train_pinn(n_col=n)[0]
        print(f"  N = {n:3d}: relative L2 error {rel_l2_error(Pn):.4f}")
    print("higher spatial frequency k (initial hump sin(k pi x)), same network:")
    for k in (1, 3):
        Pk = P if k == 1 else train_pinn(k=k, steps=1500)[0]
        print(f"  k = {k}: relative L2 error {rel_l2_error(Pk, k=k):.4f}")

    readings = make_readings()
    t0 = time.time()
    Pi, a_fin, hist_i = train_pinn(readings=readings, alpha_start=0.3, steps=2000)
    print(f"\ninverse: alpha started at 0.3, recovered {a_fin:.4f} (true {ALPHA}); direct fit {fit_alpha_direct(readings):.4f} "
          f"({time.time() - t0:.1f} s)")

    # ---- figures
    g = np.linspace(0, 1, 101)
    X, T = np.meshgrid(g, g)
    U = forward(P, X.ravel(), T.ravel())[0].reshape(X.shape)
    E = exact(X, T)
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, Z, ttl, vmax in zip(axs, (E, U, np.abs(U - E)), ("exact", "network", "absolute error"), (1, 1, None)):
        im = ax.imshow(Z, origin="lower", extent=[0, 1, 0, 1], aspect="auto", cmap="inferno" if vmax else "viridis", vmin=0 if vmax else None, vmax=vmax)
        ax.set_title(ttl)
        ax.set_xlabel("position x (scaled units)")
        fig.colorbar(im, ax=ax, label="temperature u" if vmax else "|u - exact|")
    axs[0].set_ylabel("time t (scaled units)")
    fig.tight_layout()
    fig.savefig(OUT / "heatmaps.png", dpi=110)

    fig2, axs2 = plt.subplots(1, 2, figsize=(10, 4))
    for key in ("residual", "boundary", "initial"):
        axs2[0].semilogy(hist["step"], hist[key], label=key)
    axs2[0].set_xlabel("training step")
    axs2[0].set_ylabel("mean squared loss piece (scaled units^2)")
    axs2[0].set_title("The three loss pieces during training")
    axs2[0].legend()
    axs2[0].grid(alpha=0.3, which="both")
    for tt, col in ((0.0, "tab:blue"), (0.5, "tab:green"), (1.0, "tab:red")):
        axs2[1].plot(g, exact(g, tt), "--", color=col)
        axs2[1].plot(g, forward(P, g, np.full_like(g, tt))[0], color=col, label=f"t = {tt}")
    axs2[1].plot(x_fd, u_fd, "k.", label="finite differences, t = 1")
    axs2[1].set_xlabel("position x (scaled units)")
    axs2[1].set_ylabel("temperature u (scaled units)")
    axs2[1].set_title("Profiles: network (solid) vs exact (dashed)")
    axs2[1].legend(fontsize=8)
    axs2[1].grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "loss_and_profiles.png", dpi=110)

    fig3, ax3 = plt.subplots(figsize=(6.5, 4))
    ax3.plot(hist_i["step"], hist_i["alpha"], label="alpha during training")
    ax3.axhline(ALPHA, color="k", ls="--", label="true alpha = 0.1")
    ax3.set_xlabel("training step")
    ax3.set_ylabel("diffusivity alpha (scaled units)")
    ax3.set_title("Inverse problem: alpha recovered from 30 noisy readings")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "inverse_alpha.png", dpi=120)

# %% [markdown]
# ## Where this stops
# One space dimension, a smooth start, a one-hidden-layer network and a few thousand steps.
# Sharper or faster-oscillating solutions, several dimensions and long times are much harder for
# this recipe. That is the road to the Target: see `promo/roadmap.md`.
