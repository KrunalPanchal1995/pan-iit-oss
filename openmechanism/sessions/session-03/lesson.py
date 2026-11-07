"""Session 3 (Level 3): calibrate a toy mechanism against noisy synthetic ignition delays.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: calibrate a toy mechanism against experiments
# **A. Real-world problem.** A kinetic mechanism is a list of reactions with rate constants
# that nobody knows exactly. Experiments (here: ignition delays at several temperatures)
# measure what the mechanism should predict. *Calibration* moves the rate constants until the
# simulation matches the experiments, and tells you how well the data pinned them down.
# Everything in this session is a **toy**: invented numbers, four made-up reactions, and a
# model far simpler than real combustion chemistry.
#
# **Plan.** (1) write a stable ODE solver, (2) validate it against a formula, (3) make noisy
# synthetic experiments from a known truth, (4) fit by least squares, (5) read the parameter
# uncertainty from the Jacobian, (6) check that the fit recovers the truth.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314462618                                # J / (mol K)
T_REF = 1000.0                                     # K, reference temperature
# Toy mechanism (invented numbers):  F -> R (k1), F + R -> 2 R (k2), R -> P (k3), F -> P (k4)
K_REF = np.array([2.0e-3, 30.0, 10.0, 1.0e-3])     # rate constants at 1000 K: 1/s, L/(mol s), 1/s, 1/s
E_ACT = np.array([120e3, 60e3, 20e3, 100e3])       # activation energies, J/mol
NAMES = ["k1  F -> R", "k2  F + R -> 2R", "k3  R -> P", "k4  F -> P"]
FIT = (0, 1)                                       # we calibrate scale factors of k1 and k2
SIGMA = 0.05                                       # noise on ln(tau): about 5 percent
TRUTH = np.array([np.log(0.5), np.log(1.25)])      # true ln(scale factors) used to make the data


# %% [markdown]
# ## Step 1: rate constants with temperature
# Each rate constant is `k_ref * s * exp(-(Ea / R) * (1/T - 1/T_ref))`, the Arrhenius form of
# Session 2 written around 1000 K. The number `s` is the **scale factor** we calibrate:
# `s = 1` is the nominal mechanism, `s = 2` doubles that rate constant at every temperature.

# %%
def rate_constants(T, s=(1.0, 1.0, 1.0, 1.0)):
    """The four rate constants at temperature(s) T (K) for scale factors s. Returns shape (4, ...)."""
    T = np.asarray(T, dtype=float)
    s = np.asarray(s, dtype=float)
    out = [K_REF[i] * s[i] * np.exp(-E_ACT[i] / R_GAS * (1.0 / T - 1.0 / T_REF)) for i in range(4)]
    return np.array(out)


# %% [markdown]
# ## Step 2: an implicit solver for the ODEs
# With F = fuel, R = radical, P = product (F + R + P = F0 is conserved):
#
#     dF/dt = -(k1 + k4) F - k2 F R
#     dR/dt =  k1 F + k2 F R - k3 R
#
# The radical grows exponentially while fuel is plentiful (the "induction" period) and then
# fuel runs out quickly: rates differ by large factors, which is what makes real mechanisms
# *stiff*. We use the **trapezoidal rule** (an implicit method): the new state y1 must satisfy
# `y1 = y0 + dt/2 * (f(y0) + f(y1))`, solved by Newton's method. It is second-order accurate
# and does not blow up when the step is too large for an explicit method.
#
# **Ignition delay** tau is defined here as the time when half of the fuel is gone (F = F0/2).
# All experiments are solved together as numpy arrays, each with its own time step.

# %%
def simulate_tau(T, F0, s=(1.0, 1.0, 1.0, 1.0), h=0.1, max_steps=2500):
    """Ignition delay (s) for arrays of temperature T (K) and starting fuel F0 (mol/L).

    Returns nan where F never falls to F0/2 within max_steps steps (no ignition)."""
    k1, k2, k3, k4 = rate_constants(T, s)
    k1, k2, k3, k4, F0 = np.broadcast_arrays(k1, k2, k3, k4, np.asarray(F0, dtype=float))
    dt = h / (k2 * F0 + k3 + k1 + k4)               # step set by the fastest rate in each experiment
    F, Rad, t = F0.copy(), np.zeros(F0.shape), np.zeros(F0.shape)
    tau = np.full(F0.shape, np.nan)
    for _ in range(max_steps):
        fF = -(k1 + k4) * F - k2 * F * Rad
        fR = k1 * F + k2 * F * Rad - k3 * Rad
        F1, R1 = F.copy(), Rad.copy()
        for _ in range(4):                          # Newton iterations on the 2x2 system
            gF = F1 - F - 0.5 * dt * (fF - (k1 + k4) * F1 - k2 * F1 * R1)
            gR = R1 - Rad - 0.5 * dt * (fR + k1 * F1 + k2 * F1 * R1 - k3 * R1)
            a = 1 + 0.5 * dt * (k1 + k4 + k2 * R1)
            b = 0.5 * dt * k2 * F1
            c = -0.5 * dt * (k1 + k2 * R1)
            d = 1 - 0.5 * dt * (k2 * F1 - k3)
            det = a * d - b * c
            F1 = F1 - (d * gF - b * gR) / det
            R1 = R1 - (-c * gF + a * gR) / det
        crossed = np.isnan(tau) & (F1 <= F0 / 2)
        if crossed.any():
            frac = (F - F0 / 2) / (F - F1)          # linear interpolation inside the step
            tau = np.where(crossed, t + frac * dt, tau)
        F, Rad, t = F1, R1, t + dt
        if not np.isnan(tau).any():
            break
    return tau


def tau_linearised(T, F0, s=(1.0, 1.0, 1.0, 1.0)):
    """The Session 2 formula ln(1 + g / (2 k1)) / g with g = k2 F0 - k3: a quick approximation to check against."""
    k1, k2, k3, _ = rate_constants(T, s)
    g = k2 * F0 - k3
    return np.log1p(g / (2 * k1)) / g


def rk4_fuel_after(k1, k2, k3, k4, F0, t_end, dt):
    """Explicit RK4 for one experiment: returns F(t_end). Used to show why explicit steps can fail."""
    def f(y):
        F, Rad = y
        return np.array([-(k1 + k4) * F - k2 * F * Rad, k1 * F + k2 * F * Rad - k3 * Rad])

    y = np.array([F0, 0.0])
    for _ in range(int(round(t_end / dt))):
        a = f(y)
        b = f(y + 0.5 * dt * a)
        c = f(y + 0.5 * dt * b)
        d = f(y + dt * c)
        y = y + dt / 6.0 * (a + 2 * b + 2 * c + d)
    return float(y[0])


# %% [markdown]
# ## Step 3: synthetic experiments with a known truth
# We pick a true mechanism (scale factors `TRUTH`), simulate it, and add random noise of about
# 5 percent to every ln(ignition delay). Because we know the truth, we can later check
# whether the calibration recovers it. Two datasets, like two experiment campaigns:
# dataset 0 has 8 temperatures at F0 = 1 mol/L, dataset 1 has 4 temperatures at F0 = 2 mol/L.

# %%
def make_dataset(seed=1, truth=TRUTH, sigma=SIGMA, bias_second=0.0):
    """Noisy synthetic data. `bias_second` adds a systematic error (in ln tau) to dataset 1."""
    T = np.concatenate([np.linspace(900.0, 1400.0, 8), [950.0, 1100.0, 1250.0, 1400.0]])
    F0 = np.concatenate([np.full(8, 1.0), np.full(4, 2.0)])
    group = np.concatenate([np.zeros(8, dtype=int), np.ones(4, dtype=int)])
    s = np.ones(4)
    s[list(FIT)] = np.exp(truth)
    clean = np.log(simulate_tau(T, F0, s))
    rng = np.random.default_rng(seed)
    noisy = clean + sigma * rng.standard_normal(T.size) + bias_second * (group == 1)
    return {"T": T, "F0": F0, "group": group, "ln_tau": noisy, "sigma": np.full(T.size, sigma), "clean": clean}


# %% [markdown]
# ## Step 4: residuals, Jacobian and a least-squares fit
# The unknowns are `theta = (ln s1, ln s2)`. For each experiment i the **residual** is
# `r_i = (ln tau_model - ln tau_observed) / sigma_i`: how many noise-widths the model is off.
# The **Jacobian** `J` holds the slopes `d r_i / d theta_j` (finite differences).
# Levenberg-Marquardt takes the step `(J^T J + lam D) delta = -J^T r`, which is
# Gauss-Newton for small `lam` and a cautious gradient step for large `lam`.

# %%
def scales_from(theta):
    s = np.ones(4)
    s[list(FIT)] = np.exp(theta)
    return s


def residuals_many(thetas, data):
    """Residuals for several parameter sets at once (one solver call). Shape (m, n_experiments)."""
    thetas = np.atleast_2d(thetas)
    m, n = thetas.shape[0], data["T"].size
    s = np.ones((4, m * n))
    for j, idx in enumerate(FIT):
        s[idx] = np.repeat(np.exp(thetas[:, j]), n)
    tau = simulate_tau(np.tile(data["T"], m), np.tile(data["F0"], m), s)
    r = (np.log(tau).reshape(m, n) - data["ln_tau"]) / data["sigma"]
    return np.where(np.isnan(r), 20.0, r)           # no ignition: a large, finite penalty


def residuals(theta, data):
    return residuals_many(np.asarray(theta, dtype=float), data)[0]


def jacobian(theta, data, eps=1e-3):
    """Forward finite differences of the residual vector with respect to each theta_j."""
    theta = np.asarray(theta, dtype=float)
    trials = np.vstack([theta] + [theta + eps * np.eye(theta.size)[j] for j in range(theta.size)])
    rr = residuals_many(trials, data)
    return ((rr[1:] - rr[0]) / eps).T


def weights_power_mean(r, group, p):
    """Row weights that turn the power-mean over datasets into a weighted least-squares problem.

    Objective: M_p = (mean over datasets of E_d^p)^(1/p), E_d = root-mean-square residual of
    dataset d. Minimising sum_d E_d^p is done by re-weighting each dataset by E_d^(p-2) / n_d."""
    w = np.ones(r.size)
    for g in np.unique(group):
        m = group == g
        e = np.sqrt(np.mean(r[m] ** 2)) + 1e-12
        w[m] = e ** (p - 2) / m.sum()
    return w / w.mean()


def calibrate(data, theta0, p=None, iters=30, verbose=False):
    """Levenberg-Marquardt. p=None: plain weighted least squares; p=number: power-mean over datasets."""
    theta = np.asarray(theta0, dtype=float).copy()
    lam = 1e-2
    path = [theta.copy()]
    w = np.ones(data["T"].size)
    for it in range(iters):
        r = residuals(theta, data)
        if p is not None:
            w = weights_power_mean(r, data["group"], p)
        J = jacobian(theta, data)
        sw = np.sqrt(w)
        Jw, rw = J * sw[:, None], r * sw
        c0 = 0.5 * float(rw @ rw)
        step = np.zeros_like(theta)
        for _ in range(12):
            A = Jw.T @ Jw
            trial = np.clip(np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), -Jw.T @ rw), -1.0, 1.0)
            r_new = residuals(theta + trial, data)
            if 0.5 * float(np.sum(w * r_new * r_new)) < c0:
                step = trial
                theta = theta + step
                lam = max(lam / 3.0, 1e-8)
                break
            lam *= 4.0
        path.append(theta.copy())
        if verbose:
            print(f"iter {it:2d}  cost {c0:10.3f}  theta {np.round(theta, 4)}")
        if np.linalg.norm(step) < 1e-6:
            break
    return theta, np.array(path)


# %% [markdown]
# ## Step 5: how well is each parameter pinned down?
# Near the best fit the model is almost linear, so the parameter covariance is
# `Cov = (J^T J)^-1` (J is built from residuals already divided by sigma, so no extra factor is
# needed). The square roots of its diagonal are the 1-sigma uncertainties of `ln s1` and
# `ln s2`; the off-diagonal term says how much the two are tied together. A 1-sigma ellipse is
# `delta^T Cov^-1 delta = 1`. A **reduced chi-square** `sum r^2 / (n - 2)` near 1 says the
# model is consistent with the noise level.

# %%
def covariance(theta, data):
    J = jacobian(theta, data)
    return np.linalg.inv(J.T @ J)


def reduced_chi2(theta, data):
    r = residuals(theta, data)
    return float(r @ r / (r.size - len(theta)))


def ellipse_points(centre, cov, n_sigma=1.0, n=100):
    """Points on the n-sigma ellipse of a 2x2 covariance."""
    vals, vecs = np.linalg.eigh(cov)
    ang = np.linspace(0, 2 * np.pi, n)
    unit = np.stack([np.cos(ang), np.sin(ang)])
    return (np.asarray(centre)[:, None] + vecs @ (n_sigma * np.sqrt(vals)[:, None] * unit)).T


# %%
if __name__ == "__main__":
    import time

    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t0 = time.time()

    # ---- validation 1: with only k1 on, F = F0 exp(-k1 t), so tau = ln 2 / k1
    k1 = float(rate_constants(1000.0)[0])
    s_only1 = np.array([1.0, 1e-12, 1e-12, 1e-12])
    tau_num = float(simulate_tau(1000.0, 1.0, s_only1, h=0.02))
    print(f"only k1 on: numerical tau {tau_num:.3f} s, formula ln2/k1 = {np.log(2) / k1:.3f} s")
    # ---- validation 2: halve the step and watch the answer settle (second-order accurate)
    prev = None
    for h in (0.2, 0.1, 0.05, 0.025):
        tau_h = float(simulate_tau(1000.0, 1.0, h=h, max_steps=20000))
        print(f"h = {h:5.3f}: tau(1000 K, F0 = 1) = {tau_h:.6f} s" + ("" if prev is None else f"   change {tau_h - prev:+.2e}"))
        prev = tau_h
    Tq = np.array([900.0, 1000.0, 1400.0])
    print("Session 2 formula / solver at 900, 1000, 1400 K:", np.round(tau_linearised(Tq, 1.0) / simulate_tau(Tq, 1.0), 3))
    # ---- why implicit: explicit RK4 with a big step on the hottest case
    kk = rate_constants(1400.0)
    ref = rk4_fuel_after(*kk, 2.0, 0.1, 1e-4)
    with np.errstate(all="ignore"):
        for dt in (0.0005, 0.005, 0.02):
            print(f"explicit RK4, dt = {dt}: F(0.1 s) = {rk4_fuel_after(*kk, 2.0, 0.1, dt):.4g}   (reference {ref:.4g})")

    # ---- calibration, uncertainty, truth check
    data = make_dataset(seed=1)
    theta, path = calibrate(data, [0.0, 0.0], verbose=True)
    cov = covariance(theta, data)
    sd = np.sqrt(np.diag(cov))
    print("truth  ln s :", np.round(TRUTH, 3), " scale factors", np.round(np.exp(TRUTH), 3))
    print("fitted ln s :", np.round(theta, 3), " scale factors", np.round(np.exp(theta), 3))
    print("1-sigma     :", np.round(sd, 3), " correlation", round(float(cov[0, 1] / (sd[0] * sd[1])), 3))
    print("reduced chi2:", round(reduced_chi2(theta, data), 3))

    # ---- sensitivity to the starting guess
    ends = [calibrate(data, [a, b])[0] for a, b in ((-0.7, 0.7), (0.7, -0.7))]
    print("fits from two different starts agree to", f"{float(np.ptp(np.array(ends + [theta]), axis=0).max()):.1e}", "in ln s")

    # ---- sensitivity to noise: repeat the experiment with 6 noise seeds
    fits = np.array([calibrate(make_dataset(sd_), [0.0, 0.0])[0] for sd_ in range(1, 7)])
    print("6 repeats: mean fit", np.round(fits.mean(0), 3), " scatter", np.round(fits.std(0, ddof=1), 3),
          " (predicted 1-sigma", np.round(sd, 3), ")")
    for sg in (0.02, 0.05, 0.10):
        d_sg = dict(data, sigma=np.full(data["T"].size, sg))
        print(f"noise sigma {sg:.2f}: predicted 1-sigma of (ln s1, ln s2) = {np.round(np.sqrt(np.diag(covariance(theta, d_sg))), 3)}")

    # ---- the power-mean objective, and a systematic error in dataset 1
    biased = make_dataset(seed=1, bias_second=0.2)
    for p in (None, 2):
        th, _ = calibrate(biased, [0.0, 0.0], p=p)
        print(f"dataset 1 biased by +0.2 in ln tau, objective p = {p}: fitted ln s {np.round(th, 3)}, error {np.round(th - TRUTH, 3)}")

    # ---- figures
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
    ax = axs[0]
    m0 = data["group"] == 0
    m1 = ~m0
    ax.errorbar(1000 / data["T"][m0], data["ln_tau"][m0], yerr=SIGMA, fmt="o", color="k", label="dataset 0 (F0 = 1)")
    ax.errorbar(1000 / data["T"][m1], data["ln_tau"][m1], yerr=SIGMA, fmt="s", color="gray", label="dataset 1 (F0 = 2)")
    Tg = np.linspace(880, 1420, 60)
    for th, style, lab in ((np.zeros(2), "--", "nominal mechanism (start)"), (theta, "-", "calibrated")):
        for F0v, col in ((1.0, "tab:blue"), (2.0, "tab:orange")):
            ax.plot(1000 / Tg, np.log(simulate_tau(Tg, F0v, scales_from(th))), style, color=col, label=f"{lab}, F0 = {F0v:.0f}")
    ax.set_xlabel("1000 / T  (1/K)")
    ax.set_ylabel("ln( ignition delay / s )")
    ax.set_title("Simulation moves onto the experiments")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    ax = axs[1]
    g1 = np.linspace(-2.0, 0.8, 41)
    g2 = np.linspace(-0.2, 0.6, 41)
    G1, G2 = np.meshgrid(g1, g2)
    pts = np.stack([G1.ravel(), G2.ravel()], axis=1)
    cost = 0.5 * np.sum(residuals_many(pts, data) ** 2, axis=1).reshape(G1.shape)
    cs = ax.contourf(G1, G2, np.minimum(cost, 60), levels=20, cmap="viridis_r")
    fig.colorbar(cs, ax=ax, label="cost 0.5 sum r^2 (capped at 60)")
    ax.plot(path[:, 0], path[:, 1], "w.-", lw=1)
    e = ellipse_points(theta, cov)
    ax.plot(e[:, 0], e[:, 1], "r-", label="1-sigma ellipse")
    ax.plot(*TRUTH, "k*", ms=12, label="truth")
    ax.plot(*theta, "wo", mec="k", label="fit")
    ax.set_xlim(g1[0], g1[-1])
    ax.set_ylim(g2[0], g2[-1])
    ax.set_xlabel("ln s1  (scale of k1)")
    ax.set_ylabel("ln s2  (scale of k2)")
    ax.set_title("Cost surface, path and uncertainty")
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "calibration.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(path[:, 0], path[:, 1], "o-")
    ax2.set_xlabel("ln s1")
    ax2.set_ylabel("ln s2")
    ax2.set_title("Levenberg-Marquardt iterates")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "lm_path.png", dpi=120)
    print("seconds:", round(time.time() - t0, 1))
