"""Session 3 (Level 3): a true Neural ODE, trained through the solver, and validated.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: train a Neural ODE through the solver
# **A. Real-world problem.** In Session 2 the network was trained on single steps. Noise in
# the data then leaks into the learned rule, and small errors pile up when you predict far
# ahead. Here the network is the right-hand side of an ODE, `dx/dt = f_theta(x)`, and the
# **loss is measured after the solver has run for several steps** (a *rollout*). The gradient
# is computed by hand-coded backpropagation through the RK4 steps (no finite differences, no
# library). We then check the result against a system whose answer we know.

# %%
import functools
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

STIFF_K, DAMP_C = 4.0, 0.4                       # true system: x'' = -4 x - 0.4 x'
A_TRUE = np.array([[0.0, 1.0], [-STIFF_K, -DAMP_C]])
DT = 0.1                                         # time between observations (s)
WIDTH = 12                                       # hidden units: 12*2 + 12 + 2*12 + 2 = 62 parameters


# %% [markdown]
# ## Step 1: the truth, the solver and the data
# The truth is the damped oscillator again, so we know its exact flow
# `x(t) = exp(A t) x0` (computed from the eigenvalues of A). Data = exact positions and
# velocities at spacing 0.1 s, plus Gaussian noise of size `sigma`.

# %%
_LAM, _V = np.linalg.eig(A_TRUE)
_VI = np.linalg.inv(_V)


def true_field(x):
    """dx/dt for states stored as rows (..., 2): the true damped oscillator."""
    return x @ A_TRUE.T


def exact_flow(x0, t):
    """Exact state after time t for starting states x0 with shape (B, 2)."""
    return np.real((_V @ (np.exp(_LAM * t)[:, None] * (_VI @ np.asarray(x0).T))).T)


def rk4_step(f, x, h):
    k1 = f(x)
    k2 = f(x + 0.5 * h * k1)
    k3 = f(x + 0.5 * h * k2)
    k4 = f(x + h * k3)
    return x + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def make_data(n_traj=6, n_pts=25, sigma=0.05, seed=1, box=1.5, dt=DT):
    """Array (n_pts, n_traj, 2): noisy exact states, starting states uniform in [-box, box]^2."""
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(-box, box, (n_traj, 2))
    X = np.array([exact_flow(x0, k * dt) for k in range(n_pts)])
    return X + rng.normal(0.0, sigma, X.shape) if sigma > 0 else X


# %% [markdown]
# ## Step 2: the network and its hand-written derivative
# `f(x) = W2 tanh(W1 x + b1) + b2`. For backpropagation we need the *vector-Jacobian product*:
# given a vector `v` (how the loss changes with the output of f), return how the loss changes
# with the input x and with each weight. With `a = tanh(W1 x + b1)` and
# `d = (W2^T v) * (1 - a^2)`:
#
#     dL/dx = W1^T d     dL/dW2 = v a^T     dL/db2 = v     dL/dW1 = d x^T     dL/db1 = d

# %%
def init_params(width=WIDTH, seed=0):
    rng = np.random.default_rng(seed)
    return {"W1": rng.normal(0.0, 0.5, (width, 2)), "b1": np.zeros(width),
            "W2": rng.normal(0.0, 0.3, (2, width)), "b2": np.zeros(2)}


def n_params(P):
    return int(sum(v.size for v in P.values()))


def field(P, x):
    return np.tanh(x @ P["W1"].T + P["b1"]) @ P["W2"].T + P["b2"]


def field_vjp(P, x, v):
    """Return (dL/dx, dict of weight gradients) for a batch: rows of x and v are samples."""
    a = np.tanh(x @ P["W1"].T + P["b1"])
    d = (v @ P["W2"]) * (1.0 - a * a)
    grads = {"W2": v.T @ a, "b2": v.sum(axis=0), "W1": d.T @ x, "b1": d.sum(axis=0)}
    return d @ P["W1"], grads


# %% [markdown]
# ## Step 3: backpropagation through RK4 (the "discretise-then-optimise" gradient)
# One RK4 step computes four stages k1..k4 and combines them. Going backwards, the
# sensitivity `g` of the loss to the state after the step is pushed through the stages in
# reverse order, each stage using `field_vjp` once. We store only the states, and recompute
# the stages. The gradient is the *exact* gradient of the discrete loss, which is what we
# check against finite differences in the checkpoint.

# %%
def rollout(P, x0, h, n):
    """States after 0..n RK4 steps: array (n + 1, B, 2)."""
    xs = [x0]
    for _ in range(n):
        xs.append(rk4_step(lambda z: field(P, z), xs[-1], h))
    return np.array(xs)


def add_grads(total, new):
    for key in total:
        total[key] += new[key]


def rollout_loss_grad(P, x0, h, targets):
    """Mean squared error between the rollout and targets (m, B, 2); returns (loss, gradients)."""
    m = targets.shape[0]
    xs = rollout(P, x0, h, m)
    res = xs[1:] - targets
    loss = float(np.mean(res ** 2))
    grads = {k: np.zeros_like(v) for k, v in P.items()}
    g = np.zeros_like(x0)                                  # sensitivity of the loss to the current state
    for s in range(m - 1, -1, -1):
        g = g + 2.0 * res[s] / res.size
        x = xs[s]
        k1 = field(P, x)
        k2 = field(P, x + 0.5 * h * k1)
        k3 = field(P, x + 0.5 * h * k2)
        gk1, gk2, gk3, gk4 = h / 6 * g, h / 3 * g, h / 3 * g, h / 6 * g
        g_new = g.copy()                                   # the state also enters the sum directly
        gx, gw = field_vjp(P, x + h * k3, gk4)             # stage 4 sees x + h k3
        add_grads(grads, gw)
        g_new += gx
        gk3 = gk3 + h * gx
        gx, gw = field_vjp(P, x + 0.5 * h * k2, gk3)       # stage 3 sees x + h/2 k2
        add_grads(grads, gw)
        g_new += gx
        gk2 = gk2 + 0.5 * h * gx
        gx, gw = field_vjp(P, x + 0.5 * h * k1, gk2)       # stage 2 sees x + h/2 k1
        add_grads(grads, gw)
        g_new += gx
        gk1 = gk1 + 0.5 * h * gx
        gx, gw = field_vjp(P, x, gk1)                      # stage 1 sees x
        add_grads(grads, gw)
        g_new += gx
        g = g_new
    return loss, grads


# %% [markdown]
# ## Step 4: windows of data, Adam, and the two training modes
# From every observed point we start a rollout of `m` steps and compare each step with the
# next observed point. `m = 1` is the **one-step** loss (through the solver); `m = 8` is the
# **rollout** loss (0.8 s of simulated time). Adam is the optimiser of Session 2.

# %%
def make_windows(X, m):
    starts = np.arange(0, X.shape[0] - m)
    x0 = X[starts].reshape(-1, 2)
    targets = np.stack([X[starts + j + 1].reshape(-1, 2) for j in range(m)])
    return x0, targets


def train_neural_ode(X, m, width=WIDTH, iters=350, lr=0.06, seed=0, h=DT):
    """Adam on the rollout loss. Returns (parameters, list of loss values)."""
    P = init_params(width, seed)
    mom = {k: np.zeros_like(v) for k, v in P.items()}
    var = {k: np.zeros_like(v) for k, v in P.items()}
    x0, targets = make_windows(X, m)
    history = []
    for t in range(1, iters + 1):
        loss, G = rollout_loss_grad(P, x0, h, targets)
        history.append(loss)
        for k in P:
            mom[k] = 0.9 * mom[k] + 0.1 * G[k]
            var[k] = 0.999 * var[k] + 0.001 * G[k] ** 2
            P[k] = P[k] - lr * (mom[k] / (1 - 0.9 ** t)) / (np.sqrt(var[k] / (1 - 0.999 ** t)) + 1e-8)
    return P, history


@functools.lru_cache(maxsize=None)
def trained(sigma=0.05, m=8, n_traj=6, width=WIDTH, iters=350, seed=1):
    """Cached training run on make_data(n_traj, 25, sigma, seed)."""
    X = make_data(n_traj, 25, sigma, seed)
    P, hist = train_neural_ode(X, m, width, iters, lr=0.06)
    return P, hist


# %% [markdown]
# ## Step 5: judge a model by how far ahead it stays right
# Start from fresh initial conditions (never seen in training), run the true flow and the
# learned flow side by side, and measure the distance between them step by step.

# %%
def test_states(n=20, box=1.5, seed=99):
    return np.random.default_rng(seed).uniform(-box, box, (n, 2))


def prediction_error(P, steps=60, box=1.5, h=DT):
    """RMS distance (over 20 test starts) between learned and true flow after 0..steps steps."""
    x0 = test_states(box=box)
    true = np.array([exact_flow(x0, k * h) for k in range(steps + 1)])
    pred = rollout(P, x0, h, steps)
    return np.sqrt(((pred - true) ** 2).sum(axis=-1).mean(axis=1))


def design_error(n_traj, sigma, seeds=(1, 2), m=8):
    """Worst error after 6 s over several random data sets: a design check for 'how much data'."""
    return max(float(prediction_error(trained(sigma, m, n_traj, WIDTH, 350, s)[0], 60)[60]) for s in seeds)


def jacobian_at_origin(P):
    """d f / d x at x = 0 for the network: W2 diag(1 - tanh(b1)^2) W1."""
    return P["W2"] @ ((1.0 - np.tanh(P["b1"]) ** 2)[:, None] * P["W1"])


def eigenvalues(M):
    ev = np.linalg.eigvals(M)
    return ev[np.argsort(ev.imag)]


# %% [markdown]
# ## Step 6: where it breaks (failure cases)
# 1. **Stiffness.** Explicit RK4 multiplies the state by `R(z) = 1 + z + z^2/2 + z^3/6 + z^4/24`
#    each step, with `z = lambda h`. For `lambda = -1000` and `h = 0.01`, `z = -10` and
#    `R = 291`: the solution explodes instead of decaying.
# 2. **Extrapolation.** The network has seen states in a box; outside it nothing constrains `f`.
# 3. **Overfitting.** Too few noisy points and too many weights: the network fits the noise.

# %%
def rk4_amplification(z):
    return 1 + z + z ** 2 / 2 + z ** 3 / 6 + z ** 4 / 24


def stable_limit():
    """Largest |z| on the negative real axis with |R(z)| <= 1 (bisection)."""
    lo, hi = 1.0, 4.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if abs(rk4_amplification(-mid)) <= 1 else (lo, mid)
    return lo


def decay_with_rk4(lam, h, t_end):
    """Solve x' = lam x, x(0) = 1 with RK4 steps of size h; return x(t_end)."""
    x = np.array([1.0])
    for _ in range(int(round(t_end / h))):
        x = rk4_step(lambda z: lam * z, x, h)
    return float(x[0])


def data_loss_of_truth(X, m):
    """Rollout loss of the TRUE system on noisy data: the floor an honest model cannot beat much."""
    x0, targets = make_windows(X, m)
    xs = [x0]
    for _ in range(m):
        xs.append(rk4_step(true_field, xs[-1], DT))
    return float(np.mean((np.array(xs[1:]) - targets) ** 2))


@functools.lru_cache(maxsize=None)
def overfit_demo(width=48):
    """Two noisy trajectories of 12 points, a wide network, long training.
    Returns (training loss, loss of the true system on the same data, test error after 3 s)."""
    X = make_data(2, 12, 0.1, 5)
    P, hist = train_neural_ode(X, 3, width, 1500, lr=0.03)
    return hist[-1], data_loss_of_truth(X, 3), float(prediction_error(P, 30)[30])


# %% [markdown]
# ## Step 7: mini-project model, a damped pendulum
# State (angle theta in rad, angular velocity omega in rad/s). The rule is
# `theta' = omega`, `omega' = -4 sin(theta) - 0.3 omega`: nonlinear, so no matrix will do.

# %%
def pendulum_field(x):
    return np.stack([x[..., 1], -4.0 * np.sin(x[..., 0]) - 0.3 * x[..., 1]], axis=-1)


def small_angle_field(x):
    return np.stack([x[..., 1], -4.0 * x[..., 0] - 0.3 * x[..., 1]], axis=-1)


def simulate(f, x0, h, n, sub=10):
    """Accurate reference solution: RK4 with `sub` small steps inside each interval h."""
    xs = [np.asarray(x0, float)]
    for _ in range(n):
        x = xs[-1]
        for _ in range(sub):
            x = rk4_step(f, x, h / sub)
        xs.append(x)
    return np.array(xs)


@functools.lru_cache(maxsize=None)
def pendulum_model(sigma=0.03, n_traj=8, width=16, iters=500, m=8):
    rng = np.random.default_rng(2)
    X = simulate(pendulum_field, rng.uniform(-2.0, 2.0, (n_traj, 2)), DT, 30)
    X = X + np.random.default_rng(3).normal(0.0, sigma, X.shape)
    P, hist = train_neural_ode(X, m, width, iters, lr=0.05)
    return P, hist


def pendulum_angle_error(f, steps=60, seed=77):
    """RMS angle error (rad) of the dynamics f over 0..steps steps from 20 unseen starts."""
    x0 = np.random.default_rng(seed).uniform(-1.8, 1.8, (20, 2))
    true = simulate(pendulum_field, x0, DT, steps)
    pred = simulate(f, x0, DT, steps)
    return np.sqrt(((pred - true)[..., 0] ** 2).mean(axis=1))


# %%
if __name__ == "__main__":
    import time

    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    steps = 60
    t_axis = DT * np.arange(steps + 1)
    P_roll, h_roll = trained(0.05, 8)
    P_one, h_one = trained(0.05, 1)
    e_roll, e_one = prediction_error(P_roll, steps), prediction_error(P_one, steps)
    print(f"parameters {n_params(P_roll)}; error after 1 s: one-step {e_one[10]:.3f}, rollout {e_roll[10]:.3f}; "
          f"after 6 s: one-step {e_one[60]:.3f}, rollout {e_roll[60]:.3f}")
    print("true eigenvalues   ", np.round(eigenvalues(A_TRUE), 3))
    print("learned eigenvalues", np.round(eigenvalues(jacobian_at_origin(P_roll)), 3))

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].semilogy(h_one, label="one-step loss (m = 1)")
    ax[0].semilogy(h_roll, label="rollout loss (m = 8)")
    ax[0].set_xlabel("Adam iteration")
    ax[0].set_ylabel("training loss")
    ax[0].set_title("Training loss (noise sigma = 0.05)")
    ax[0].legend()
    ax[0].grid(alpha=0.3)
    ax[1].plot(t_axis, e_one, label="trained one step at a time")
    ax[1].plot(t_axis, e_roll, label="trained on 8-step rollouts")
    ax[1].set_xlabel("prediction time (s)")
    ax[1].set_ylabel("distance to true flow")
    ax[1].set_title("Prediction error on unseen starts")
    ax[1].legend()
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "rollout_vs_onestep.png", dpi=120)

    x0 = np.array([[1.2, 0.0], [-0.8, 1.0]])
    true = np.array([exact_flow(x0, k * DT) for k in range(steps + 1)])
    pred = rollout(P_roll, x0, DT, steps)
    g = np.linspace(-1.5, 1.5, 13)
    gx, gy = np.meshgrid(g, g)
    pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
    fig2, ax2 = plt.subplots(figsize=(5.5, 5.5))
    ft, fl = true_field(pts), field(P_roll, pts)
    ax2.quiver(pts[:, 0], pts[:, 1], ft[:, 0], ft[:, 1], color="0.7", angles="xy")
    ax2.quiver(pts[:, 0], pts[:, 1], fl[:, 0], fl[:, 1], color="tab:blue", angles="xy", alpha=0.6)
    for i in range(2):
        ax2.plot(true[:, i, 0], true[:, i, 1], "k-", lw=2, label="true flow" if i == 0 else None)
        ax2.plot(pred[:, i, 0], pred[:, i, 1], "r--", lw=2, label="Neural ODE" if i == 0 else None)
    ax2.set_xlabel("position x (m)")
    ax2.set_ylabel("velocity v (m/s)")
    ax2.set_title("Learned (blue) and true (grey) field; two trajectories")
    ax2.legend(loc="upper right", fontsize=8)
    ax2.set_aspect("equal")
    fig2.tight_layout()
    fig2.savefig(OUT / "learned_field.png", dpi=120)

    print("noise sweep (rollout m = 8), error after 6 s:")
    for sg in (0.0, 0.05, 0.1):
        print(f"  sigma {sg:.2f}: {prediction_error(trained(sg, 8)[0], steps)[60]:.3f}")
    print("horizon sweep (sigma 0.05), error after 6 s:")
    for mm in (1, 3, 8):
        print(f"  m = {mm}: {prediction_error(trained(0.05, mm)[0], steps)[60]:.3f}")

    ext = [prediction_error(P_roll, 30, box=b)[30] for b in (1.5, 3.0)]
    print(f"extrapolation, error after 3 s: inside training box {ext[0]:.3f}, starts in a box twice as big {ext[1]:.3f}")
    tr_loss, truth_loss, ov_err = overfit_demo()
    print(f"overfitting: training loss {tr_loss:.4f} is below the true system's loss {truth_loss:.4f} on the same data; test error after 3 s {ov_err:.3f}")
    print(f"stiff: RK4 with lambda h = -10 multiplies by {rk4_amplification(-10.0):.0f} per step; limit |z| = {stable_limit():.4f}")

    fig3, ax3 = plt.subplots(figsize=(6, 4))
    boxes = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 4.0])
    ax3.plot(boxes, [prediction_error(P_roll, 30, box=b)[30] for b in boxes], "o-")
    ax3.axvline(1.5, color="gray", ls=":", label="edge of training box")
    ax3.set_xlabel("size of the box the test starts are drawn from")
    ax3.set_ylabel("distance to true flow after 3 s")
    ax3.set_title("Failure: leaving the training region")
    ax3.legend()
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "extrapolation.png", dpi=120)

    Pp, hp = pendulum_model()
    e_nn = pendulum_angle_error(lambda z: field(Pp, z))
    e_lin = pendulum_angle_error(small_angle_field)
    print(f"pendulum: angle error after 6 s: Neural ODE {e_nn[60]:.3f} rad, small-angle model {e_lin[60]:.3f} rad")
    print(f"total run time {time.time() - t0:.1f} s")

# %% [markdown]
# ## The adjoint method (concept only)
# Backpropagating through every solver step stores all the stages, so memory grows with the
# number of steps. The *adjoint method* instead solves a second ODE backwards in time for the
# sensitivity, so memory does not grow with the number of steps. The price: it recomputes the
# trajectory backwards, which can be inaccurate for unstable or stiff dynamics. We do not
# implement it here; it is a milestone on the roadmap.
