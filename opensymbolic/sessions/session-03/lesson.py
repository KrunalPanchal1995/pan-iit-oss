"""Session 3 (Level 3): a real symbolic regression search, built from scratch in numpy.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: search all small formulas and let the data choose
# **A. Real-world problem.** You have measurements and no formula. Instead of guessing, we
# let the computer *build every small formula*, fit its constants, and rank them by
# error and size. Then we ask the honest question: how often does it find the true law?
#
# **Plan.** (1) enumerate expression trees up to a size, with duplicates removed,
# (2) fit `y = a*f(x) + b` exactly by least squares for all of them at once,
# (3) keep the Pareto front and choose with a complexity penalty, (4) measure the success
# rate over seeded noisy trials, (5) study two failures, (6) add a units filter.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the true laws (our synthetic "nature")
# Four laws, each given as a function we can sample, then corrupt with noise.
# * quadratic: y = 3 x^2
# * pendulum: T = 2 pi sqrt(L / g) with g = 9.81 m/s^2
# * Arrhenius in 1/T form: with x = 1000 / T_kelvin, ln k = ln A - E x / 1000
#   (A = 1e10 per second, E = 20000 K). Taking the log makes the constant E *linear*.
# * saturating rate: y = 2 x / (1 + x), a harder law with a constant inside the formula.

# %%
G = 9.81
LN_A = float(np.log(1e10))
E_KELVIN = 20000.0

LAWS = {
    "quadratic": (lambda x: 3.0 * x ** 2, np.linspace(0.5, 5.0, 30)),
    "pendulum": (lambda L: 2 * np.pi * np.sqrt(L / G), np.linspace(0.2, 3.0, 30)),
    "arrhenius": (lambda x: LN_A - E_KELVIN * x / 1000.0, 1000.0 / np.linspace(500.0, 1500.0, 30)),
    "saturating": (lambda x: 2.0 * x / (1.0 + x), np.linspace(0.2, 5.0, 30)),
}


def noisy(y, level, rng):
    """Add Gaussian noise whose standard deviation is level times the spread (std) of y."""
    return y + level * np.std(y) * rng.standard_normal(len(y))


# %% [markdown]
# ## Step 2: enumerate every small formula
# An expression is a tree of tuples: ('x',), ('1',), ('sq', child), ('add', left, right)...
# We build trees by size (number of nodes). Two trees that give the same numbers on our
# x values are duplicates, so we keep only the smaller one. Formulas that produce nan or
# infinity (sqrt of a negative, divide by zero) are dropped.

# %%
UNARY = {"sqrt": np.sqrt, "sq": np.square, "exp": np.exp, "log": np.log}
BINARY = {"add": np.add, "sub": np.subtract, "mul": np.multiply, "div": np.divide}
COMMUTATIVE = {"add", "mul"}


def eval_tree(t, x):
    """Value of tree t at the array x (nan where the formula is not defined)."""
    with np.errstate(all="ignore"):
        k = t[0]
        if k == "x":
            return np.asarray(x, float)
        if k == "1":
            return np.ones(len(x))
        if k in UNARY:
            return UNARY[k](eval_tree(t[1], x))
        return BINARY[k](eval_tree(t[1], x), eval_tree(t[2], x))


def count_nodes(t):
    return 1 + sum(count_nodes(c) for c in t[1:] if isinstance(c, tuple))


def to_str(t):
    k = t[0]
    if k in ("x", "1"):
        return k
    if k in UNARY:
        return f"{k}({to_str(t[1])})"
    sym = {"add": "+", "sub": "-", "mul": "*", "div": "/"}[k]
    return f"({to_str(t[1])} {sym} {to_str(t[2])})"


def enumerate_pool(x, max_size):
    """All distinct formulas up to max_size nodes. Returns (trees, sizes, values matrix)."""
    x = np.asarray(x, float)
    seen = set()
    levels = {}

    def commit(size, trees, vals):
        ok = np.all(np.isfinite(vals), axis=1) & (np.abs(vals).max(axis=1) < 1e12)
        trees = [t for t, o in zip(trees, ok) if o]
        vals = vals[ok]
        if len(vals) == 0:
            levels[size] = ([], np.zeros((0, len(x))))
            return
        keys = np.round(vals, 9)
        _, first = np.unique(keys, axis=0, return_index=True)
        keep = []
        for i in sorted(first):
            kb = keys[i].tobytes()
            if kb not in seen:
                seen.add(kb)
                keep.append(i)
        levels[size] = ([trees[i] for i in keep], vals[keep])

    commit(1, [("x",), ("1",)], np.vstack([x, np.ones(len(x))]))
    for s in range(2, max_size + 1):
        trees, chunks = [], []
        prev_t, prev_v = levels[s - 1]
        with np.errstate(all="ignore"):
            for op, fn in UNARY.items():
                trees += [(op, t) for t in prev_t]
                chunks.append(fn(prev_v))
            for i in range(1, s - 1):
                j = s - 1 - i
                (ti, vi), (tj, vj) = levels[i], levels[j]
                if not ti or not tj:
                    continue
                for op, fn in BINARY.items():
                    if op in COMMUTATIVE and i > j:
                        continue
                    a_idx = np.repeat(np.arange(len(ti)), len(tj))
                    b_idx = np.tile(np.arange(len(tj)), len(ti))
                    trees += [(op, ti[a], tj[b]) for a, b in zip(a_idx, b_idx)]
                    chunks.append(fn(vi[a_idx], vj[b_idx]))
        commit(s, trees, np.vstack(chunks))
    all_t, all_s, all_v = [], [], []
    for s in range(1, max_size + 1):
        t, v = levels[s]
        all_t += t
        all_s += [s] * len(t)
        all_v.append(v)
    return all_t, np.array(all_s), np.vstack(all_v)


# %% [markdown]
# ## Step 3: fit constants exactly, for all formulas at once
# Every formula f is used in the form y = a f(x) + b. That is *linear* in a and b, so the
# best a and b come from a closed formula (no iteration):
#     a = cov(f, y) / var(f),   b = mean(y) - a mean(f).
# We do this for every formula with one matrix operation. Formulas that do not change with
# x (var = 0) are useless and get an infinite error.

# %%
_PREP = {}


def _prepare(vals):
    """Centre every formula once and remember it (the pool is reused for many datasets)."""
    key = id(vals)
    if key not in _PREP or _PREP[key][0] is not vals:
        fm = vals.mean(axis=1, keepdims=True)
        fc = vals - fm
        var = (fc ** 2).mean(axis=1)
        flat = var <= 1e-12 * (1.0 + (vals ** 2).mean(axis=1))
        if len(_PREP) > 40:
            _PREP.clear()
        _PREP[key] = (vals, fm, fc, var, flat)
    return _PREP[key][1:]


def fit_all(vals, y):
    """Least-squares a, b and mean squared error for y = a f + b, for each row f of vals."""
    y = np.asarray(y, float)
    fm, fc, var, flat = _prepare(vals)
    yc = y - y.mean()
    cov = fc @ yc / len(y)
    a = np.where(flat, 0.0, cov / np.where(flat, 1.0, var))
    b = y.mean() - a * fm[:, 0]
    mse = ((yc - a[:, None] * fc) ** 2).mean(axis=1)
    mse[flat] = np.inf
    return a, b, mse


def pareto_front(sizes, mse, floor=0.0):
    """Indices of the best formula at each size that beat every smaller size.
    Errors below `floor` (round-off level) count as equal, so a perfect formula ends the front."""
    front, best = [], np.inf
    for s in np.unique(sizes):
        idx = np.where(sizes == s)[0]
        i = idx[np.argmin(mse[idx])]
        e = max(mse[i], floor)
        if e < best * (1 - 1e-9):
            front.append(int(i))
            best = e
    return front


def bic_score(mse, size, n, floor):
    """Lower is better: n ln(error) + (size + 2) ln(n). The +2 counts the constants a and b."""
    return n * np.log(np.maximum(mse, floor)) + (size + 2) * np.log(n)


def search(trees, sizes, vals, y):
    """Run the whole search: returns the chosen formula and the front."""
    n = len(y)
    a, b, mse = fit_all(vals, y)
    floor = 1e-10 * np.var(y)
    front = pareto_front(sizes, mse, floor)
    scores = [bic_score(mse[i], sizes[i], n, floor) for i in front]
    best = front[int(np.argmin(scores))]
    return {"tree": trees[best], "size": int(sizes[best]), "a": float(a[best]), "b": float(b[best]),
            "mse": float(mse[best]), "front": front, "a_all": a, "b_all": b, "mse_all": mse}


# %% [markdown]
# ## Step 4: did we find the true law?
# "Found" must be strict. The chosen formula counts as recovered when, after refitting
# a and b on *noise-free* data over a wider range, it reproduces the true law
# almost exactly (relative error below 1e-6). So x*x and sq(x) are the same, but
# x*x + 0.1 x is not.

# %%
def recovered(tree, law, x_wide):
    f = eval_tree(tree, x_wide)
    y = law(x_wide)
    if not np.all(np.isfinite(f)) or np.ptp(f) == 0:
        return False
    a, b, mse = fit_all(f[None, :], y)
    return bool(np.sqrt(mse[0]) < 1e-6 * np.std(y))


MAX_SIZE = 7
_POOLS = {}
_CACHE = {}


def cached_pool(x, max_size):
    """enumerate_pool, remembered for repeated calls with the same x values."""
    key = (np.asarray(x, float).tobytes(), max_size)
    if key not in _CACHE:
        _CACHE[key] = enumerate_pool(x, max_size)
    return _CACHE[key]


def pool_for(name):
    if name not in _POOLS:
        _POOLS[name] = enumerate_pool(LAWS[name][1], MAX_SIZE)
    return _POOLS[name]


def recovery_rate(name, level, seeds):
    """Fraction of seeded noisy datasets where the search recovers the true law."""
    law, x = LAWS[name]
    trees, sizes, vals = pool_for(name)
    x_wide = np.linspace(x.min() * 0.5, x.max() * 1.5, 200)
    hits = 0
    for s in seeds:
        y = noisy(law(x), level, np.random.default_rng(1000 + s))
        res = search(trees, sizes, vals, y)
        hits += recovered(res["tree"], law, x_wide)
    return hits / len(seeds)


# %% [markdown]
# ## Step 5: two honest failures
# **Overfitting.** With only 8 noisy points, picking the formula with the lowest *training*
# error chooses a big, wiggly formula. We compare it with the penalised choice on points
# the search never saw.
# **Wrong search space.** If the true law is not buildable from our pieces, no formula fits
# to the noise level. We compare the best error to the noise to notice.

# %%
def overfit_trial(seed, level=0.10, n_train=8):
    """Held-out error of (lowest training error) versus (penalised choice)."""
    law, _ = LAWS["quadratic"]
    xt = np.linspace(0.5, 3.0, n_train)
    xh = np.linspace(0.5, 5.0, 100)
    rng = np.random.default_rng(2000 + seed)
    trees, sizes, vals = cached_pool(xt, MAX_SIZE)
    y = noisy(law(xt), level, rng)
    res = search(trees, sizes, vals, y)
    i_min = int(np.argmin(res["mse_all"]))
    out = {}
    for tag, tree, a, b in (("min_train", trees[i_min], res["a_all"][i_min], res["b_all"][i_min]),
                            ("penalised", res["tree"], res["a"], res["b"])):
        pred = a * eval_tree(tree, xh) + b
        out[tag] = (float(np.mean((pred - law(xh)) ** 2)), count_nodes(tree))
    return out


def sine_failure(level=0.02):
    """The law y = sin(3 x) is not in the grammar: relative error of the best formula."""
    x = np.linspace(0.0, 4.0, 40)
    y = noisy(np.sin(3 * x), level, np.random.default_rng(5))
    trees, sizes, vals = cached_pool(x, MAX_SIZE)
    res = search(trees, sizes, vals, y)
    xh = np.linspace(4.0, 6.0, 50)
    pred = res["a"] * eval_tree(res["tree"], xh) + res["b"]
    return {"rel_rmse": float(np.sqrt(res["mse"]) / np.std(y)), "noise": level,
            "extrap_rmse": float(np.sqrt(np.mean((pred - np.sin(3 * xh)) ** 2))), "tree": res["tree"]}


# %% [markdown]
# ## Step 6: units as a guide (power-law search with dimensional analysis)
# Suppose a pendulum period T (seconds) might depend on length L (metres), gravity g
# (m/s^2) and bob mass m (kg) as T = C L^p g^q m^r. We try every exponent triple from
# -2 to 2 in steps of 0.5. A formula for a time must have units of seconds, which means
# the exponent of kilograms is 0, of metres is 0, and of seconds is 1. That is a
# *unit-consistency filter* on the exponents.

# %%
EXPS = np.arange(-2.0, 2.01, 0.5)
# dimensions as exponents of (kg, m, s)
DIMS = {"L": np.array([0, 1, 0]), "g": np.array([0, 1, -2]), "m": np.array([1, 0, 0])}
TARGET_DIM = np.array([0, 0, 1])      # a time, in seconds


def confounded_pendulum_data(seed=0, level=0.02):
    """Synthetic experiments where the lab (by accident) used L = 0.5 g, with m varied freely."""
    rng = np.random.default_rng(seed)
    g = np.array([1.62, 3.71, 9.81, 24.8, 5.0, 15.0, 8.0, 12.0])
    L = 0.5 * g
    m = rng.uniform(0.1, 2.0, len(g))
    T = 2 * np.pi * np.sqrt(L / g) * (1 + level * rng.standard_normal(len(g)))
    return L, g, m, T


def power_law_fits(L, g, m, T):
    """Fit log T = log C + p log L + q log g + r log m for all exponent triples."""
    cols = np.log(np.vstack([L, g, m]))
    out = []
    for p in EXPS:
        for q in EXPS:
            for r in EXPS:
                resid = np.log(T) - (p * cols[0] + q * cols[1] + r * cols[2])
                c = resid.mean()
                out.append(((float(p), float(q), float(r)), float(np.mean((resid - c) ** 2)), float(np.exp(c))))
    return out


def units_ok(p, q, r):
    """True if L^p g^q m^r has the units of a time."""
    dim = p * DIMS["L"] + q * DIMS["g"] + r * DIMS["m"]
    return bool(np.allclose(dim, TARGET_DIM))


# %% [markdown]
# ## Step 7: the mini-project helper (a rate law from kinetics data)
# Reaction rates r = k c^n are measured at concentrations c. We search for the order n
# with the same machinery.

# %%
def kinetics_trial(n_points, seed, level=0.05, order=2.0, k=0.5):
    """Does the search recover r = k c^order from n_points noisy rate measurements?"""
    c = np.linspace(0.2, 2.0, n_points)
    r = k * c ** order
    rng = np.random.default_rng(3000 + seed)
    trees, sizes, vals = cached_pool(c, 5)
    res = search(trees, sizes, vals, noisy(r, level, rng))
    ok = recovered(res["tree"], lambda v: k * v ** order, np.linspace(0.1, 3.0, 100))
    return ok, res


# %% [markdown]
# ## Step 8: the mini front used by the app
# Eight hand-picked formulas, closed-form fits, the same noise pattern as in the browser app.

# %%
Z = np.array([0.8, -1.1, 0.3, 1.4, -0.6, -1.3, 0.9, 0.1, -0.4, 1.0])
XS = np.arange(1.0, 11.0)
MINI = [("x", 1), ("sqrt(x)", 2), ("log(x)", 2), ("sq(x)", 2), ("sq(x) + x", 4), ("sq(x) * x", 4), ("sq(sq(x))", 3), ("exp(x / 4)", 4)]
MINI_FN = [lambda x: x, np.sqrt, np.log, np.square, lambda x: x * x + x, lambda x: x ** 3, lambda x: x ** 4, lambda x: np.exp(x / 4)]


def mini_front(level, lam):
    """Mini search: y = 3 x^2 (1 + level z). Returns mse list, scores and chosen index."""
    y = 3.0 * XS ** 2 * (1.0 + level * Z)
    mses = []
    for fn in MINI_FN:
        _, _, m = fit_all(fn(XS)[None, :], y)
        mses.append(float(m[0]))
    floor = 1e-12 * np.var(y)
    scores = [np.log(max(m, floor)) + lam * MINI[i][1] for i, m in enumerate(mses)]
    return mses, scores, int(np.argmin(scores))


# %% [markdown]
# ## Step 9: see it
# Left: the Pareto front for the saturating law at 2 percent noise. Right: recovery rate
# against noise for the four laws.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    law, x = LAWS["saturating"]
    trees, sizes, vals = pool_for("saturating")
    y = noisy(law(x), 0.02, np.random.default_rng(1))
    res = search(trees, sizes, vals, y)
    print("pool size", len(trees), "| chosen", to_str(res["tree"]), "a=%.3f b=%.3f" % (res["a"], res["b"]))
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 4))
    ax[0].semilogy(sizes, res["mse_all"], ".", color="0.75", ms=2, label="all formulas")
    fs = [sizes[i] for i in res["front"]]
    fm = [res["mse_all"][i] for i in res["front"]]
    ax[0].semilogy(fs, fm, "o-", color="tab:blue", label="Pareto front")
    ax[0].semilogy([res["size"]], [res["mse"]], "s", color="tab:red", ms=10, label="chosen")
    ax[0].set_xlabel("complexity (nodes)")
    ax[0].set_ylabel("mean squared error (y units squared)")
    ax[0].set_title("Pareto front, saturating law, 2% noise")
    ax[0].legend()
    ax[0].grid(alpha=0.3)
    levels = [0.0, 0.02, 0.05, 0.10, 0.20]
    for name in LAWS:
        rates = [recovery_rate(name, lv, range(20)) for lv in levels]
        print(name, [f"{r:.2f}" for r in rates])
        ax[1].plot([100 * lv for lv in levels], rates, "o-", label=name)
    ax[1].set_xlabel("noise level (% of the spread of y)")
    ax[1].set_ylabel("fraction of 20 trials that recover the law")
    ax[1].set_title("Recovery rate versus noise")
    ax[1].set_ylim(-0.02, 1.05)
    ax[1].legend()
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "search_front.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
