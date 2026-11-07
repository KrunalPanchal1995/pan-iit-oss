"""Session 2 (Level 2): a tiny network trained by hand-coded backpropagation, then trained on a law.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: train a network, then train it on a differential equation
# **A. Real-world problem.** Hot tea cools so that its excess temperature u obeys `du/dx = -u`
# with `u(0) = 1` (scaled units, x is time). The exact answer is `exp(-x)`. Instead of
# stepping the equation forward, a physics-informed network (PINN) is asked to *be* a function
# whose slope plus value is zero at chosen "collocation" points and whose value at x = 0 is 1.
# How many collocation points does it need?
#
# **Plan.** (1) a one-hidden-layer tanh network, (2) its gradients by hand (backpropagation),
# checked against finite differences, (3) Adam, (4) fit noisy data, (5) train on the equation,
# (6) count the collocation points, (7) a fast linear cousin that the app uses.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the network and its slope
# With H hidden units, parameters a (input weights), d (shifts), c (output weights), e (offset):
#
#     z_j = a_j x + d_j,   th_j = tanh(z_j),   u(x) = sum_j c_j th_j + e
#
# Differentiate with the chain rule. Since d tanh(z)/dz = 1 - tanh(z)^2 =: s_j,
#
#     du/dx = sum_j c_j a_j s_j
#
# Both u and du/dx are cheap sums, so we get them together in one forward pass.

# %%
def init_net(n_units, seed=0):
    rng = np.random.default_rng(seed)
    return {"a": rng.normal(0.0, 1.0, n_units), "d": rng.normal(0.0, 1.0, n_units),
            "c": rng.normal(0.0, 1.0 / np.sqrt(n_units), n_units), "e": np.zeros(1)}


def forward(P, x):
    """Return u, du/dx and a cache for the backward pass."""
    th = np.tanh(np.outer(x, P["a"]) + P["d"])
    s = 1.0 - th ** 2
    u = th @ P["c"] + P["e"][0]
    ux = s @ (P["c"] * P["a"])
    return u, ux, (th, s, -2.0 * th * s)


# %% [markdown]
# ## Step 2: backpropagation by hand
# A loss L depends on the network only through u(x_i) and du/dx(x_i). If we know how L changes
# with those (`gu`, `gux`), the chain rule gives how L changes with every parameter.
# Write s = 1 - th^2 and s' = d s / dz = -2 th s. Then
#
#     du/dc_j = th_j                du/dx depends on c_j through  a_j s_j
#     du/da_j = c_j s_j x           d(du/dx)/da_j = c_j (s_j + a_j s'_j x)
#     du/dd_j = c_j s_j             d(du/dx)/dd_j = c_j a_j s'_j
#     du/de   = 1
#
# Sum over the points. This is the whole of backpropagation for one hidden layer.

# %%
def backward(P, x, cache, gu, gux):
    th, s, s2 = cache
    a, c = P["a"], P["c"]
    X = x[:, None]
    return {
        "c": gu @ th + gux @ (s * a),
        "a": (gu[:, None] * c * s * X + gux[:, None] * c * (s + a * s2 * X)).sum(axis=0),
        "d": (gu[:, None] * c * s + gux[:, None] * c * a * s2).sum(axis=0),
        "e": np.array([gu.sum()]),
    }


def gradient_check(seed=1, h=1e-6):
    """Largest relative gap between the hand gradient and a finite-difference gradient."""
    P = init_net(5, seed)
    x = np.array([0.1, 0.8, 1.3])

    def loss(Q):
        u, ux, _ = forward(Q, x)
        return float(np.sum(u ** 2) + 0.5 * np.sum(ux ** 2))

    u, ux, cache = forward(P, x)
    G = backward(P, x, cache, 2.0 * u, ux)
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
# ## Step 3: Adam, written by hand
# Plain gradient descent uses one step size for every parameter. Adam keeps running averages
# of the gradient (m) and of its square (v) and divides: parameters with small, steady
# gradients still move.
#
#     m = 0.9 m + 0.1 g,   v = 0.999 v + 0.001 g^2,   p = p - lr * m_hat / (sqrt(v_hat) + 1e-8)
#
# where m_hat and v_hat undo the start-up bias of m and v.

# %%
class Adam:
    def __init__(self, P, lr=1e-2):
        self.lr = lr
        self.t = 0
        self.m = {k: np.zeros_like(v) for k, v in P.items()}
        self.v = {k: np.zeros_like(v) for k, v in P.items()}

    def step(self, P, G):
        self.t += 1
        for k in P:
            self.m[k] = 0.9 * self.m[k] + 0.1 * G[k]
            self.v[k] = 0.999 * self.v[k] + 0.001 * G[k] ** 2
            m_hat = self.m[k] / (1 - 0.9 ** self.t)
            v_hat = self.v[k] / (1 - 0.999 ** self.t)
            P[k] -= self.lr * m_hat / (np.sqrt(v_hat) + 1e-8)


# %% [markdown]
# ## Step 4: fit noisy samples of a function (no physics yet)
# Twenty noisy samples (noise 0.1) of sin(2 pi x) on 0 to 1. Loss = mean of (u - y)^2.

# %%
def noisy_samples(n=20, noise=0.1, seed=3):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.random(n))
    return x, np.sin(2 * np.pi * x) + noise * rng.normal(size=n)


def fit_data(x, y, n_units=10, steps=3000, seed=0, lr=1e-2):
    P = init_net(n_units, seed)
    opt = Adam(P, lr)
    for _ in range(steps):
        u, _, cache = forward(P, x)
        opt.step(P, backward(P, x, cache, 2.0 * (u - y) / len(x), np.zeros_like(u)))
    return P


# %% [markdown]
# ## Step 5: train on the equation
# Now there are no data at all. We choose N collocation points x_i between 0 and 2 and minimise
#
#     loss = mean over i of ( du/dx(x_i) + u(x_i) )^2  +  ( u(0) - 1 )^2
#            \_____ residual term _____/                 \_ boundary term _/
#
# The residual term is zero exactly when the law holds at the points. The boundary term pins
# the amplitude (the law alone allows any multiple of exp(-x)).

# %%
def train_ode(n_col, n_units=10, steps=3000, seed=0, lr=1e-2, w_bc=1.0, length=2.0):
    P = init_net(n_units, seed)
    opt = Adam(P, lr)
    x = np.linspace(0.0, length, n_col)
    x0 = np.array([0.0])
    for _ in range(steps):
        u, ux, cache = forward(P, x)
        r = ux + u
        G = backward(P, x, cache, 2.0 * r / n_col, 2.0 * r / n_col)
        u0, _, c0 = forward(P, x0)
        G0 = backward(P, x0, c0, w_bc * 2.0 * (u0 - 1.0), np.zeros_like(u0))
        opt.step(P, {k: G[k] + G0[k] for k in P})
    return P


def ode_loss(u, ux, u_at_zero):
    """Residual term (mean of (u' + u)^2 at the points) plus boundary term (u(0) - 1)^2."""
    return float(np.mean((ux + u) ** 2) + (u_at_zero - 1.0) ** 2)


def ode_errors(P, length=2.0):
    """(largest |u - exp(-x)|, largest |u' + u|) on a fine grid, i.e. between the points as well."""
    x = np.linspace(0.0, length, 401)
    u, ux, _ = forward(P, x)
    return float(np.abs(u - np.exp(-x)).max()), float(np.abs(ux + u).max())


# %% [markdown]
# ## Step 6: a fast linear cousin (used by the app)
# If the bumps are fixed in place (as in Session 1) the residual is *linear* in the weights, so
# the whole PINN is one least-squares solve. The app uses this form so it can answer instantly.

# %%
STEEP = 3.0


def bump_features(x, n_units):
    x = np.asarray(x, dtype=float)
    centres = np.linspace(0.0, 2.0, n_units)
    th = np.tanh(STEEP * (x[:, None] - centres))
    ones = np.ones((len(x), 1))
    return np.hstack([th, ones]), np.hstack([STEEP * (1.0 - th ** 2), np.zeros((len(x), 1))])


def linear_pinn(n_col, n_units, w_bc=10.0, ridge=1e-6):
    """Weights that minimise sum (u' + u)^2 at n_col points on [0, 2] plus w_bc^2 (u(0) - 1)^2."""
    x = np.linspace(0.0, 2.0, n_col)
    F, D = bump_features(x, n_units)
    R = D + F
    F0, _ = bump_features([0.0], n_units)
    A = R.T @ R + w_bc ** 2 * (F0.T @ F0) + ridge * np.eye(n_units + 1)
    return np.linalg.solve(A, w_bc ** 2 * F0.T @ np.array([1.0]))


def linear_errors(c):
    x = np.linspace(0.0, 2.0, 401)
    F, D = bump_features(x, len(c) - 1)
    return float(np.abs(F @ c - np.exp(-x)).max()), float(np.abs((F + D) @ c).max())


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"gradient check: worst relative gap hand vs finite difference = {gradient_check():.2e}")

    xd, yd = noisy_samples()
    P = fit_data(xd, yd)
    xt = np.linspace(0, 1, 201)
    rms_data = float(np.sqrt(np.mean((forward(P, xd)[0] - yd) ** 2)))
    rms_true = float(np.sqrt(np.mean((forward(P, xt)[0] - np.sin(2 * np.pi * xt)) ** 2)))
    print(f"data fit: rms to the noisy samples = {rms_data:.3f}, rms to the true sin curve = {rms_true:.3f}")

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(xt, np.sin(2 * np.pi * xt), "k--", label="true sin(2 pi x)")
    ax.plot(xt, forward(P, xt)[0], color="tab:blue", label="network (10 tanh units)")
    ax.plot(xd, yd, "ko", ms=4, label="20 noisy samples")
    ax.set_xlabel("x (scaled units)")
    ax.set_ylabel("u (scaled units)")
    ax.set_title("Step 4: a tiny network fitted by hand-coded backpropagation")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "data_fit.png", dpi=120)

    xs = np.linspace(0, 2, 401)
    counts = (2, 3, 4, 5, 8, 12, 20)
    print("collocation points -> largest |u - exp(-x)|, largest |u' + u| (between points too)")
    nets = {}
    for n in counts:
        nets[n] = train_ode(n)
        e, r = ode_errors(nets[n])
        print(f"  N = {n:2d}: {e:.4f}, {r:.4f}")

    fig2, axs = plt.subplots(1, 2, figsize=(10, 4.2))
    axs[0].plot(xs, np.exp(-xs), "k--", label="exact exp(-x)")
    for n in (3, 5, 12):
        axs[0].plot(xs, forward(nets[n], xs)[0], label=f"N = {n}")
        axs[0].plot(np.linspace(0, 2, n), forward(nets[n], np.linspace(0, 2, n))[0], "o", ms=4, color=axs[0].lines[-1].get_color())
    axs[0].set_xlabel("x (scaled units)")
    axs[0].set_ylabel("u (scaled units)")
    axs[0].set_title("Solution of u' = -u, u(0) = 1")
    axs[0].legend(fontsize=8)
    axs[0].grid(alpha=0.3)
    errs = [ode_errors(nets[n])[0] for n in counts]
    axs[1].semilogy(counts, errs, "o-")
    axs[1].axhline(0.01, color="r", ls="--", label="0.01 target")
    axs[1].set_xlabel("number of collocation points N")
    axs[1].set_ylabel("largest error |u - exp(-x)| (scaled units)")
    axs[1].set_title("More collocation points, smaller error")
    axs[1].grid(alpha=0.3, which="both")
    axs[1].legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "collocation.png", dpi=120)

    print("linear cousin (8 units): N -> largest error, largest residual")
    for n in (3, 5, 8, 10, 25):
        e, r = linear_errors(linear_pinn(n, 8))
        print(f"  N = {n:2d}: {e:.4f}, {r:.4f}")

# %% [markdown]
# ## Where this stops
# The equation here involves one variable. The heat equation has two (position and time) and a
# second derivative. Session 3 extends the same hand-coded recipe to that case.
