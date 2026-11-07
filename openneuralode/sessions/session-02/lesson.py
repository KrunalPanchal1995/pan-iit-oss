"""Session 2 (Level 2): solvers, least-squares fits and a small neural network for dx/dt = f(x).

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: from a known rule to a learned rule
# **A. Real-world problem.** A mass on a spring with friction is measured with a noisy
# sensor. We want a rule `dx/dt = f(x)` that predicts where it goes next. Today:
# (1) solve a *known* rule with Euler and RK4 and measure how accurate each is,
# (2) fit an *unknown* rule from data with least squares,
# (3) replace the rule by a small neural network with hand-written backpropagation,
# (4) ask how much data and how little noise we need.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

A_TRUE = np.array([[0.0, 1.0],
                   [-4.0, -0.4]])      # x' = v, v' = -4 x - 0.4 v  (stiffness 4 per s^2, damping 0.4 per s)


# %% [markdown]
# ## Step 1: Euler, RK4 and their order
# One **Euler** step follows the arrow once: `x + h f(x)`. One **RK4** step samples the arrow
# four times (start, two midpoints, end) and blends them with weights 1, 2, 2, 1 over 6.
# The *error after a fixed time T* shrinks like `h^p`: p = 1 for Euler, p = 4 for RK4. On
# log-log axes that is a straight line with slope p, so we measure p with a line fit.

# %%
def true_field(x):
    return A_TRUE @ x


def euler_step(f, x, h):
    return x + h * f(x)


def rk4_step(f, x, h):
    k1 = f(x)
    k2 = f(x + 0.5 * h * k1)
    k3 = f(x + 0.5 * h * k2)
    k4 = f(x + h * k3)
    return x + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


_LAM, _V = np.linalg.eig(A_TRUE)
_VI = np.linalg.inv(_V)


def exact_state(x0, t):
    """Exact solution x(t) = exp(A t) x0, from the eigenvalues of A."""
    return np.real(_V @ (np.exp(_LAM * t) * (_VI @ np.asarray(x0, float))))


def integrate(step, f, x0, h, t_end):
    x = np.asarray(x0, float)
    for _ in range(int(round(t_end / h))):
        x = step(f, x, h)
    return x


def error_at_T(step, h, t_end=2.0, x0=(1.0, 0.0)):
    return float(np.linalg.norm(integrate(step, true_field, x0, h, t_end) - exact_state(x0, t_end)))


def observed_order(step, hs, t_end=2.0):
    """Slope of log(error) against log(h)."""
    errs = [error_at_T(step, h, t_end) for h in hs]
    return float(np.polyfit(np.log(hs), np.log(errs), 1)[0])


# %% [markdown]
# ## Step 2: data, derivatives and a least-squares fit
# Sensor data: `K` runs from random starts, `n` samples each, spaced `dt` apart, with
# Gaussian noise of size `sigma`. The derivative at a sample is estimated from its two
# neighbours (central difference). If we *believe* `f(x) = A x` for an unknown 2x2 matrix
# `A`, then finding A is linear least squares: minimise the sum of squares of
# `x_dot - A x` over all samples.

# %%
def make_data(K=10, n=20, dt=0.1, sigma=0.01, seed=3, box=1.5):
    """Array of shape (n, K, 2) with noisy positions and velocities."""
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(-box, box, (K, 2))
    X = np.array([np.real((_V @ (np.exp(_LAM * k * dt)[:, None] * (_VI @ x0.T))).T) for k in range(n)])
    return X + rng.normal(0.0, sigma, X.shape)


def central_difference(X, dt):
    """Return (states, derivative estimates) as rows; the first and last sample of each run are dropped."""
    return X[1:-1].reshape(-1, 2), ((X[2:] - X[:-2]) / (2 * dt)).reshape(-1, 2)


def fit_linear_field(X, dt):
    S, D = central_difference(X, dt)
    return np.linalg.lstsq(S, D, rcond=None)[0].T


def mean_fit_error(K, sigma, dt=0.1, n=20, trials=30):
    """Average Frobenius norm of (A_hat - A) over several random data sets."""
    return float(np.mean([np.linalg.norm(fit_linear_field(make_data(K, n, dt, sigma, seed=s), dt) - A_TRUE)
                          for s in range(trials)]))


# %% [markdown]
# ## Step 3: a neural network as f
# `f(x) = W2 tanh(W1 x + b1) + b2` with 16 hidden units: 16*2 + 16 + 2*16 + 2 = 82 numbers.
# The **one-step loss** compares the network's output at each sample with the derivative
# estimate from its neighbours. Backpropagation by hand, for the mean squared error
# `L = mean((out - y)^2)`: with `r = out - y`, `g = 2 r / size`, `a = tanh(W1 x + b1)`,
# `d = (g W2) * (1 - a^2)` we get `dL/dW2 = g^T a`, `dL/db2 = sum g`, `dL/dW1 = d^T x`,
# `dL/db1 = sum d`. Adam then moves each number using a running average of its gradient.

# %%
def init_mlp(width=16, seed=0):
    rng = np.random.default_rng(seed)
    return {"W1": rng.normal(0.0, 0.5, (width, 2)), "b1": np.zeros(width),
            "W2": rng.normal(0.0, 0.3, (2, width)), "b2": np.zeros(2)}


def mlp(P, x):
    return np.tanh(x @ P["W1"].T + P["b1"]) @ P["W2"].T + P["b2"]


def mlp_loss_grad(P, x, y):
    a = np.tanh(x @ P["W1"].T + P["b1"])
    r = a @ P["W2"].T + P["b2"] - y
    g = 2.0 * r / r.size
    d = (g @ P["W2"]) * (1.0 - a * a)
    return float(np.mean(r ** 2)), {"W2": g.T @ a, "b2": g.sum(axis=0), "W1": d.T @ x, "b1": d.sum(axis=0)}


def train_one_step(S, D, iters=3000, lr=0.01, width=16, seed=0):
    """Adam on the one-step loss. Returns (parameters, loss history)."""
    P = init_mlp(width, seed)
    m = {k: np.zeros_like(v) for k, v in P.items()}
    v2 = {k: np.zeros_like(v) for k, v in P.items()}
    hist = []
    for t in range(1, iters + 1):
        loss, G = mlp_loss_grad(P, S, D)
        hist.append(loss)
        for k in P:
            m[k] = 0.9 * m[k] + 0.1 * G[k]
            v2[k] = 0.999 * v2[k] + 0.001 * G[k] ** 2
            P[k] = P[k] - lr * (m[k] / (1 - 0.9 ** t)) / (np.sqrt(v2[k] / (1 - 0.999 ** t)) + 1e-8)
    return P, hist


def field_rms_error(f_learned, box=1.5, n=500, seed=5):
    """RMS difference between a learned and the true field over random states in the box."""
    g = np.random.default_rng(seed).uniform(-box, box, (n, 2))
    return float(np.sqrt(np.mean((f_learned(g) - g @ A_TRUE.T) ** 2)))


def rollout_error(f_batch, x0=(1.2, -0.5), t_end=3.0, h=0.1):
    """Distance to the exact solution at t_end after integrating the learned field with RK4."""
    x = integrate(rk4_step, lambda z: f_batch(z[None, :])[0], x0, h, t_end)
    return float(np.linalg.norm(x - exact_state(x0, t_end)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    hs = np.array([0.2, 0.1, 0.05, 0.025, 0.0125])
    pe, pr = observed_order(euler_step, hs), observed_order(rk4_step, hs)
    print(f"observed order: Euler {pe:.2f}, RK4 {pr:.2f}")
    x1 = np.array([1.0, 0.0])
    print("one step of 0.1 s from (1, 0): Euler", np.round(euler_step(true_field, x1, 0.1), 4),
          " RK4", np.round(rk4_step(true_field, x1, 0.1), 4), " exact", np.round(exact_state(x1, 0.1), 4))

    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.loglog(hs, [error_at_T(euler_step, h) for h in hs], "o-", label=f"Euler, slope {pe:.2f}")
    ax.loglog(hs, [error_at_T(rk4_step, h) for h in hs], "s-", label=f"RK4, slope {pr:.2f}")
    ax.set_xlabel("step size h (s)")
    ax.set_ylabel("error at t = 2 s (distance in state space)")
    ax.set_title("Halving h: Euler error /2, RK4 error /16")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "order_loglog.png", dpi=120)

    X = make_data(10, 20, 0.1, 0.01)
    A_hat = fit_linear_field(X, 0.1)
    print("least-squares A_hat =\n", np.round(A_hat, 3), "\nerror", round(float(np.linalg.norm(A_hat - A_TRUE)), 3))
    Ks, sigmas = (1, 3, 10, 30), (0.01, 0.05, 0.2)
    table = np.array([[mean_fit_error(K, s) for K in Ks] for s in sigmas])
    print("fit error |A_hat - A| (rows sigma 0.01, 0.05, 0.2; columns K = 1, 3, 10, 30 runs):\n", np.round(table, 3))
    fig2, ax2 = plt.subplots(figsize=(6, 4.2))
    for row, s in zip(table, sigmas):
        ax2.loglog(Ks, row, "o-", label=f"noise sigma = {s}")
    ax2.axhline(0.1, color="red", ls="--", label="target error 0.1")
    ax2.set_xlabel("number of runs K (20 samples each)")
    ax2.set_ylabel("error |A_hat - A| (1/s)")
    ax2.set_title("More data helps until noise sets the floor")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "design_table.png", dpi=120)

    S, D = central_difference(X, 0.1)
    P, hist = train_one_step(S, D)
    e_nn = field_rms_error(lambda g: mlp(P, g))
    e_ls = field_rms_error(lambda g: g @ A_hat.T)
    print(f"network: {sum(v.size for v in P.values())} parameters, final loss {hist[-1]:.4f}")
    print(f"field RMS error: network {e_nn:.3f}, least squares {e_ls:.3f}")
    print(f"error after 3 s of prediction: network {rollout_error(lambda g: mlp(P, g)):.3f}, "
          f"least squares {rollout_error(lambda g: g @ A_hat.T):.3f}")

    g = np.linspace(-1.5, 1.5, 11)
    gx, gy = np.meshgrid(g, g)
    pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
    fig3, ax3 = plt.subplots(1, 2, figsize=(10, 4.2))
    ax3[0].semilogy(hist)
    ax3[0].set_xlabel("Adam iteration")
    ax3[0].set_ylabel("one-step loss")
    ax3[0].set_title("The loss stops at the noise level")
    ax3[0].grid(alpha=0.3)
    ft, fl = pts @ A_TRUE.T, mlp(P, pts)
    ax3[1].quiver(pts[:, 0], pts[:, 1], ft[:, 0], ft[:, 1], color="0.65", angles="xy", label="true f")
    ax3[1].quiver(pts[:, 0], pts[:, 1], fl[:, 0], fl[:, 1], color="tab:blue", angles="xy", alpha=0.6, label="network f")
    ax3[1].plot(X[:, :, 0], X[:, :, 1], "k.", ms=2)
    ax3[1].set_xlabel("position x (m)")
    ax3[1].set_ylabel("velocity v (m/s)")
    ax3[1].set_title("Learned field over the data (dots)")
    fig3.tight_layout()
    fig3.savefig(OUT / "network_field.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The loss above looks at one sample at a time. Errors in the field are never *compounded*
# by the solver during training, and noisy neighbours bias the derivative estimates. Session 3
# trains through the solver itself.
