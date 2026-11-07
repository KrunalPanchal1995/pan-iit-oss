"""Session 3 (Level 3): a neural network from scratch, with hand-coded backpropagation.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: train a neural network and watch backpropagation
# **A. Real-world problem.** One line cannot separate two interleaved spirals (or XOR). Stack
# neurons in layers and the dividing curve can bend. But how do we find 100 weights? By
# *backpropagation*: the chain rule, applied layer by layer, to get the gradient of the loss
# for every weight at once. If one formula is wrong the network silently learns badly, so we
# test every gradient against finite differences.
#
# **Plan.** (1) forward pass, (2) backward pass (derived in the README, section B), (3) gradient
# check, (4) train on XOR, moons and spirals, (5) optimisers, (6) overfitting, initialisation,
# vanishing gradients and a learning rate that is too high.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: data made in code (seeded, so everyone gets the same numbers)
# Rows are samples. `y` is 0 or 1.

# %%
XOR_X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
XOR_Y = np.array([0.0, 1.0, 1.0, 0.0])


def make_moons(n, noise, seed):
    """Two interleaving half circles, n points in total, Gaussian noise of standard deviation `noise`."""
    rng = np.random.default_rng(seed)
    h = n // 2
    t = rng.uniform(0, np.pi, h)
    t2 = rng.uniform(0, np.pi, n - h)
    a = np.c_[np.cos(t), np.sin(t)]
    b = np.c_[1 - np.cos(t2), 0.5 - np.sin(t2)]
    X = np.r_[a, b] + rng.normal(0, noise, (n, 2))
    y = np.r_[np.zeros(h), np.ones(n - h)]
    order = rng.permutation(n)                            # shuffle so that slices are mixed
    return X[order], y[order]


def make_spirals(n, noise, seed, turns=1.5):
    """Two spiral arms (n points in total), the second arm is the first turned by 180 degrees."""
    rng = np.random.default_rng(seed)
    h = n // 2
    r = np.sqrt(rng.uniform(0.02, 1.0, h))               # radius 0.14 .. 1
    th = r * turns * 2 * np.pi
    arm = np.c_[r * np.cos(th), r * np.sin(th)]
    X = np.r_[arm, -arm] + rng.normal(0, noise, (2 * h, 2))
    y = np.r_[np.zeros(h), np.ones(h)]
    order = rng.permutation(2 * h)
    return X[order], y[order]


def split(X, y, test_fraction, seed):
    """Shuffle with a seed and cut into (X_train, y_train, X_test, y_test)."""
    idx = np.random.default_rng(seed).permutation(len(y))
    k = int(round(len(y) * (1 - test_fraction)))
    return X[idx[:k]], y[idx[:k]], X[idx[k:]], y[idx[k:]]


# %% [markdown]
# ## Step 2: activations
# Each hidden neuron applies a bend `phi` to its weighted sum. We store the derivative too.

# %%
ACT = {
    "tanh": (np.tanh, lambda z: 1.0 - np.tanh(z) ** 2),
    "relu": (lambda z: np.maximum(z, 0.0), lambda z: (z > 0).astype(float)),
    "sigmoid": (lambda z: 1.0 / (1.0 + np.exp(-np.clip(z, -60, 60))),
                lambda z: (1.0 / (1.0 + np.exp(-np.clip(z, -60, 60)))) * (1 - 1.0 / (1.0 + np.exp(-np.clip(z, -60, 60))))),
}


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60, 60)))


# %% [markdown]
# ## Step 3: parameters, forward pass, loss
# `params` is a list of `[W, b]` pairs, one per layer. For a two-layer network
# (2 inputs -> h hidden -> 1 output): `Z1 = X W1 + b1`, `H = phi(Z1)`, `Z2 = H W2 + b2`,
# `P = sigmoid(Z2)`, loss `L = -mean(y log P + (1 - y) log(1 - P))`.

# %%
def init_params(sizes, seed, scheme="xavier"):
    """sizes e.g. [2, 8, 1]. scheme: 'xavier' (std sqrt(1/fan_in)), 'he' (std sqrt(2/fan_in)),
    'zeros', or 'const' (every weight 0.5, a symmetric start)."""
    rng = np.random.default_rng(seed)
    params = []
    for fi, fo in zip(sizes[:-1], sizes[1:]):
        if scheme == "zeros":
            W = np.zeros((fi, fo))
        elif scheme == "const":
            W = np.full((fi, fo), 0.5)
        elif scheme == "he":
            W = rng.normal(0, np.sqrt(2.0 / fi), (fi, fo))
        else:
            W = rng.normal(0, np.sqrt(1.0 / fi), (fi, fo))
        params.append([W, np.zeros(fo)])
    return params


def forward(params, X, act="tanh"):
    """Returns (P, cache). cache = list of (layer input A_prev, pre-activation Z) per layer."""
    phi = ACT[act][0]
    A, cache = X, []
    for k, (W, b) in enumerate(params):
        Z = A @ W + b
        cache.append((A, Z))
        A = sigmoid(Z) if k == len(params) - 1 else phi(Z)
    return A.ravel(), cache


def bce(P, y):
    P = np.clip(P, 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(P) + (1 - y) * np.log(1 - P)))


def loss_of(params, X, y, act="tanh"):
    return bce(forward(params, X, act)[0], y)


# %% [markdown]
# ## Step 4: backpropagation
# Output layer: `dZ_last = (P - y) / N` (the same "prediction minus truth" as Session 2).
# For each layer, from the last to the first:
#     dW = A_prev^T dZ        db = column sums of dZ
#     dA_prev = dZ W^T        dZ_prev = dA_prev * phi'(Z_prev)
# For two layers this reads: `dL/dW2 = H^T dZ2`, `dL/dW1 = X^T (dZ2 W2^T * phi'(Z1))`.

# %%
def backward(params, cache, P, y, act="tanh"):
    """Gradients [[dW, db], ...] with the same shapes as params."""
    dphi = ACT[act][1]
    N = len(y)
    dZ = (P - y).reshape(-1, 1) / N
    grads = [None] * len(params)
    for k in range(len(params) - 1, -1, -1):
        A_prev, _ = cache[k]
        W = params[k][0]
        grads[k] = [A_prev.T @ dZ, dZ.sum(axis=0)]
        if k > 0:
            dZ = (dZ @ W.T) * dphi(cache[k - 1][1])
    return grads


def loss_and_grads(params, X, y, act="tanh"):
    P, cache = forward(params, X, act)
    return bce(P, y), backward(params, cache, P, y, act)


def grad_check(params, X, y, act="tanh", h=1e-5):
    """Largest relative error |a - n| / max(|a| + |n|, 1e-12) between the backprop gradient a and
    the central finite difference n, over every single weight and bias."""
    _, grads = loss_and_grads(params, X, y, act)
    worst = 0.0
    for k, (W, b) in enumerate(params):
        for arr, g in ((W, grads[k][0]), (b, grads[k][1])):
            it = np.nditer(arr, flags=["multi_index"])
            for _ in it:
                i = it.multi_index
                old = arr[i]
                arr[i] = old + h
                lp = loss_of(params, X, y, act)
                arr[i] = old - h
                lm = loss_of(params, X, y, act)
                arr[i] = old
                num = (lp - lm) / (2 * h)
                worst = max(worst, abs(g[i] - num) / max(abs(g[i]) + abs(num), 1e-12))
    return worst


# %% [markdown]
# ## Step 5: optimisers and the training loop
# Plain SGD: `w = w - lr * g`. Momentum: `v = beta v + g; w = w - lr * v`.
# Adam: running averages of g and g^2, with bias correction:
#     m = b1 m + (1 - b1) g;  v = b2 v + (1 - b2) g^2
#     m_hat = m / (1 - b1^t);  v_hat = v / (1 - b2^t);  w = w - lr * m_hat / (sqrt(v_hat) + eps)

# %%
class Optimiser:
    """kind: 'sgd', 'momentum' or 'adam'. Updates params in place."""

    def __init__(self, params, kind="adam", lr=0.01, beta=0.9, b1=0.9, b2=0.999, eps=1e-8):
        self.kind, self.lr, self.beta, self.b1, self.b2, self.eps, self.t = kind, lr, beta, b1, b2, eps, 0
        self.m = [[np.zeros_like(W), np.zeros_like(b)] for W, b in params]
        self.v = [[np.zeros_like(W), np.zeros_like(b)] for W, b in params]

    def step(self, params, grads):
        self.t += 1
        for k in range(len(params)):
            for j in range(2):
                g, w = grads[k][j], params[k][j]
                if self.kind == "sgd":
                    w -= self.lr * g
                elif self.kind == "momentum":
                    self.m[k][j] = self.beta * self.m[k][j] + g
                    w -= self.lr * self.m[k][j]
                else:
                    self.m[k][j] = self.b1 * self.m[k][j] + (1 - self.b1) * g
                    self.v[k][j] = self.b2 * self.v[k][j] + (1 - self.b2) * g * g
                    mh = self.m[k][j] / (1 - self.b1 ** self.t)
                    vh = self.v[k][j] / (1 - self.b2 ** self.t)
                    w -= self.lr * mh / (np.sqrt(vh) + self.eps)


def predict(params, X, act="tanh"):
    return (forward(params, X, act)[0] > 0.5).astype(int)


def accuracy(params, X, y, act="tanh"):
    return float(np.mean(predict(params, X, act) == y))


def train(params, X, y, act="tanh", kind="adam", lr=0.01, epochs=200, batch=None, seed=0, Xt=None, yt=None, snapshot=None):
    """Minibatch training (batch=None means the whole data set). Returns a history dict with the
    loss and accuracy after every epoch (and test accuracy if Xt, yt are given). snapshot(epoch, params)
    is called after every epoch if given."""
    rng = np.random.default_rng(seed)
    opt = Optimiser(params, kind, lr)
    N = len(y)
    bs = N if batch is None else batch
    hist = {"loss": [], "acc": [], "test_acc": []}
    for ep in range(epochs):
        idx = rng.permutation(N)
        for s in range(0, N, bs):
            sel = idx[s:s + bs]
            P, cache = forward(params, X[sel], act)
            opt.step(params, backward(params, cache, P, y[sel], act))
        hist["loss"].append(loss_of(params, X, y, act))
        hist["acc"].append(accuracy(params, X, y, act))
        if Xt is not None:
            hist["test_acc"].append(accuracy(params, Xt, yt, act))
        if snapshot is not None:
            snapshot(ep, params)
    return hist


def confusion(y_true, y_pred):
    """[[true 0 predicted 0, true 0 predicted 1], [true 1 predicted 0, true 1 predicted 1]]."""
    m = np.zeros((2, 2), dtype=int)
    for t, p in zip(y_true.astype(int), y_pred.astype(int)):
        m[t, p] += 1
    return m


# %% [markdown]
# ## Step 6: gradients layer by layer in a deep network
# With a sigmoid, `phi'(z) <= 0.25`. Each layer the gradient passes through multiplies it by
# `phi'` and by the weights, so in a deep sigmoid network the gradient reaching the first layers
# can be tiny. We measure the norm of dL/dW in each layer.

# %%
def layer_grad_norms(depth, width, act, scheme, X, y, seed=0):
    """Frobenius norm of dL/dW for each of the depth + 1 weight matrices (first layer first)."""
    params = init_params([X.shape[1]] + [width] * depth + [1], seed, scheme)
    _, grads = loss_and_grads(params, X, y, act)
    return [float(np.linalg.norm(g[0])) for g in grads]


def grid_predict(params, act, lim=1.6, n=120):
    gx, gy = np.meshgrid(np.linspace(-lim, lim, n), np.linspace(-lim, lim, n))
    P = forward(params, np.c_[gx.ravel(), gy.ravel()], act)[0].reshape(gx.shape)
    return gx, gy, P


# %% [markdown]
# ## Step 7: run the experiments

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # gradient check
    p = init_params([2, 6, 1], 0)
    err = grad_check(p, *make_moons(40, 0.2, 0))
    print(f"gradient check (tanh, 2-6-1): worst relative error {err:.1e}")

    # XOR
    p = init_params([2, 4, 1], 1)
    train(p, XOR_X, XOR_Y, lr=0.05, epochs=300)
    print("XOR predictions:", predict(p, XOR_X), "accuracy", accuracy(p, XOR_X, XOR_Y))

    # spirals
    X, y = make_spirals(400, 0.05, 0)
    Xtr, ytr, Xte, yte = split(X, y, 0.25, 0)
    p = init_params([2, 64, 1], 0)
    h = train(p, Xtr, ytr, lr=0.02, epochs=600, batch=32, seed=0, Xt=Xte, yt=yte)
    print(f"spirals: train accuracy {h['acc'][-1]:.3f}, test accuracy {h['test_acc'][-1]:.3f}")
    gx, gy, P = grid_predict(p, "tanh")
    fig, axs = plt.subplots(1, 2, figsize=(9, 4))
    axs[0].contourf(gx, gy, P, levels=[0, 0.5, 1], alpha=0.25, colors=["tab:orange", "tab:blue"])
    axs[0].scatter(*Xtr[ytr == 0].T, c="tab:orange", s=12)
    axs[0].scatter(*Xtr[ytr == 1].T, c="tab:blue", s=12)
    axs[0].set_xlabel("input x1")
    axs[0].set_ylabel("input x2")
    axs[0].set_title("Decision boundary on two spirals")
    axs[1].plot(h["loss"], label="training loss")
    axs[1].set_xlabel("epoch")
    axs[1].set_ylabel("cross-entropy loss (no unit)")
    ax2 = axs[1].twinx()
    ax2.plot(h["test_acc"], color="tab:green", label="test accuracy")
    ax2.set_ylabel("test accuracy (fraction)")
    axs[1].set_title("Loss falls, accuracy rises")
    axs[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "spiral_boundary.png", dpi=120)

    # optimisers
    Xm, ym = make_moons(300, 0.2, 1)
    fig2, ax3 = plt.subplots(figsize=(6, 4))
    for kind, lr in (("sgd", 0.05), ("momentum", 0.05), ("adam", 0.05)):
        pp = init_params([2, 16, 1], 2)
        hh = train(pp, Xm, ym, kind=kind, lr=lr, epochs=40, batch=32, seed=3)
        ax3.plot(hh["loss"], label=f"{kind} (lr {lr})")
        print(f"{kind}: loss after 40 epochs {hh['loss'][-1]:.3f}")
    ax3.set_xlabel("epoch")
    ax3.set_ylabel("training loss (no unit)")
    ax3.set_title("Minibatch training on moons: SGD, momentum, Adam")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "optimisers.png", dpi=120)

    # overfitting
    Xo, yo = make_moons(1040, 0.35, 5)
    Xs, ys, Xte2, yte2 = Xo[:40], yo[:40], Xo[40:], yo[40:]
    fig3, axs3 = plt.subplots(1, 2, figsize=(9, 4))
    for ax, hid in zip(axs3, (3, 100)):
        pp = init_params([2, hid, 1], 4)
        hh = train(pp, Xs, ys, lr=0.01, epochs=1500, Xt=Xte2, yt=yte2)
        ax.plot(hh["acc"], label="training accuracy")
        ax.plot(hh["test_acc"], label="test accuracy")
        ax.set_title(f"{hid} hidden neurons, 40 noisy points")
        ax.set_xlabel("epoch")
        ax.set_ylabel("accuracy (fraction)")
        ax.set_ylim(0.4, 1.02)
        ax.grid(alpha=0.3)
        ax.legend(loc="lower right")
        print(f"{hid} hidden: train {hh['acc'][-1]:.3f}, test {hh['test_acc'][-1]:.3f}")
    fig3.tight_layout()
    fig3.savefig(OUT / "overfitting.png", dpi=120)

    # vanishing gradients
    Xv, yv = make_moons(200, 0.2, 7)
    fig4, ax4 = plt.subplots(figsize=(6.5, 4))
    for act, scheme in (("sigmoid", "xavier"), ("tanh", "xavier"), ("relu", "he")):
        gn = layer_grad_norms(10, 16, act, scheme, Xv, yv)
        ax4.semilogy(range(1, len(gn) + 1), gn, "o-", label=f"{act} ({scheme})")
        print(f"{act}: gradient norm layer 1 = {gn[0]:.2e}, last layer = {gn[-1]:.2e}")
    ax4.set_xlabel("layer (1 = nearest the input)")
    ax4.set_ylabel("norm of dL/dW (log scale)")
    ax4.set_title("Gradient norm per layer in a 10-hidden-layer network")
    ax4.grid(alpha=0.3, which="both")
    ax4.legend()
    fig4.tight_layout()
    fig4.savefig(OUT / "vanishing_gradients.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
