"""Session 4 (Level 3): the response-spectrum shortcut for the base shear of a ten-storey frame.

Educational model only. Never use it for real seismic design.
Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: the response-spectrum shortcut
# **A. Real-world problem.** In Session 3 you found the peak base shear of the ten-storey frame by
# stepping through 2401 time steps of a ground record. A design office cannot do that for every
# building and every record. The usual shortcut skips the time history: for each mode, read the
# peak of a one-degree-of-freedom oscillator from the **response spectrum** of the record, turn it
# into a modal base shear, and combine the modes with the **square root of the sum of squares**
# (SRSS). How close does that get to the full run, and when does it fail?
#
# **Plan.** (1) the response spectrum of the record, (2) the base shear of one mode, (3) combine
# the modes (SRSS, sum of absolute values, CQC), (4) check against the time history, (5) the
# storey shears up the building, (6) a screening test: for which stiffnesses can the shortcut be
# trusted?
#
# *Educational model: a synthetic record, a linear shear building. Never use it for real design.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
N_FLOORS = 10
M_FLOOR = 2.0e5          # kg per floor (200 tonnes)
K_STOREY = 3.5e8         # N/m per storey (all columns of one storey together)
ZETA = 0.05              # damping ratio in every mode
STOREY_HEIGHT = 3.5      # m


# %% [markdown]
# ## Step 0: the building and the record from Session 3
# These functions are copied unchanged from Session 3 so that this file runs on its own:
# `shear_building` (M and K), `modes` (periods and mode shapes), `participation` (Gamma and the
# effective mass), `synthetic_ground` (the seeded record, peak 2 m/s^2), `sdof_response` (exact
# one-degree-of-freedom response), `damping_matrix` and `newmark` (the full time history) and
# `base_shear`.

# %%
def shear_building(n=N_FLOORS, m=M_FLOOR, k=K_STOREY):
    """Mass matrix M (diagonal) and stiffness matrix K (tridiagonal). m and k can be scalars or arrays of length n.
    k[j] is the stiffness of storey j+1 (between floor j and floor j+1; floor 0 is the ground)."""
    m = np.broadcast_to(np.asarray(m, float), (n,)).copy()
    k = np.broadcast_to(np.asarray(k, float), (n,)).copy()
    K = np.zeros((n, n))
    for j in range(n):
        K[j, j] += k[j]
        if j + 1 < n:
            K[j, j] += k[j + 1]
            K[j, j + 1] = K[j + 1, j] = -k[j + 1]
    return np.diag(m), K


# %%
def modes(M, K):
    """Return (w, phi): angular frequencies (rad/s, ascending) and mass-normalised mode shapes (columns)."""
    s = 1.0 / np.sqrt(np.diag(M))
    A = (s[:, None] * K) * s[None, :]
    w2, v = np.linalg.eigh(A)
    phi = s[:, None] * v
    phi = phi * np.where(phi[-1, :] < 0, -1.0, 1.0)
    return np.sqrt(w2), phi


# %%
def periods(w):
    return 2 * np.pi / w


# %%
def participation(M, phi):
    r = np.ones(M.shape[0])
    gamma = phi.T @ M @ r
    return gamma, gamma ** 2


# %%
def synthetic_ground(seed=7, t_dom=1.0, dur=24.0, dt=0.01, pga=2.0):
    """Return (t, a_g): ground acceleration in m/s^2, scaled so max |a_g| = pga."""
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, dur + 0.5 * dt, dt)
    f = np.linspace(0.15, 12.0, 120)
    amp = np.exp(-0.5 * (np.log(f * t_dom) / 0.45) ** 2)
    ph = rng.uniform(0, 2 * np.pi, f.size)
    a = (amp[None, :] * np.sin(2 * np.pi * f[None, :] * t[:, None] + ph[None, :])).sum(axis=1)
    env = np.clip(t / 3.0, 0, 1) * np.clip((dur - t) / 6.0, 0, 1)
    a = a * env
    return t, a * (pga / np.abs(a).max())


# %%
def damping_matrix(M, phi, w, zeta=ZETA):
    return M @ phi @ np.diag(2 * zeta * w) @ phi.T @ M


# %%
def sdof_response(w, zeta, a_g, dt):
    """Relative displacement and velocity of q'' + 2 zeta w q' + w^2 q = -a_g(t); exact for piecewise-linear a_g."""
    wd = w * np.sqrt(1 - zeta ** 2)
    # state z = (q, q'). Homogeneous part: z' = A z. Forcing f = (0, -a_g) is linear in each step.
    A = np.array([[0.0, 1.0], [-w * w, -2 * zeta * w]])
    # matrix exponential of A*dt via the closed form for the underdamped 2x2 case
    e, c, s = np.exp(-zeta * w * dt), np.cos(wd * dt), np.sin(wd * dt)
    Phi = e * (c * np.eye(2) + (s / wd) * (A + zeta * w * np.eye(2)))
    Ainv = np.linalg.inv(A)
    I2 = np.eye(2)
    # z' = A z + b0 + b1 tau, b0 = (0, -a_i), b1 = (0, -(a_{i+1}-a_i)/dt)
    G0 = Ainv @ (Phi - I2)                       # integral of exp(A (dt - s)) ds
    G1 = Ainv @ G0 - dt * Ainv                   # integral of exp(A (dt - s)) s ds (integration by parts)
    n = a_g.size
    q = np.zeros(n)
    v = np.zeros(n)
    z = np.zeros(2)
    for i in range(n - 1):
        b0 = np.array([0.0, -a_g[i]])
        b1 = np.array([0.0, -(a_g[i + 1] - a_g[i]) / dt])
        z = Phi @ z + G0 @ b0 + G1 @ b1
        q[i + 1], v[i + 1] = z
    return q, v


# %%
def newmark(M, C, K, a_g, dt, beta=0.25, gamma=0.5):
    """Direct integration of M u'' + C u' + K u = -M r a_g. Average acceleration: beta = 1/4, gamma = 1/2.
    Returns u, v, a (relative to the ground), each of shape (n_steps, n)."""
    n = M.shape[0]
    r = np.ones(n)
    nt = a_g.size
    u = np.zeros((nt, n))
    v = np.zeros((nt, n))
    a = np.zeros((nt, n))
    a[0] = np.linalg.solve(M, -M @ r * a_g[0] - C @ v[0] - K @ u[0])
    Keff = K + gamma / (beta * dt) * C + M / (beta * dt ** 2)
    Kinv = np.linalg.inv(Keff)
    for i in range(nt - 1):
        p = -M @ r * a_g[i + 1]
        rhs = (p + M @ (u[i] / (beta * dt ** 2) + v[i] / (beta * dt) + (0.5 / beta - 1) * a[i])
               + C @ (gamma / (beta * dt) * u[i] + (gamma / beta - 1) * v[i] + dt * (0.5 * gamma / beta - 1) * a[i]))
        u[i + 1] = Kinv @ rhs
        a[i + 1] = (u[i + 1] - u[i]) / (beta * dt ** 2) - v[i] / (beta * dt) - (0.5 / beta - 1) * a[i]
        v[i + 1] = v[i] + dt * ((1 - gamma) * a[i] + gamma * a[i + 1])
    return u, v, a


# %%
def storey_drift(u):
    return np.diff(np.hstack([np.zeros((u.shape[0], 1)), u]), axis=1)


# %%
def base_shear(u, k1):
    return k1 * u[:, 0]


# %%
def sdof_peak(period, zeta, a_g, dt):
    """Peak |relative displacement| (m) of a one-degree-of-freedom oscillator: one point of the response spectrum."""
    q, _ = sdof_response(2 * np.pi / period, zeta, a_g, dt)
    return float(np.abs(q).max())


# %% [markdown]
# ## Step 1: the response spectrum
# Take a one-degree-of-freedom oscillator with period T and 5 percent damping, shake it with the
# record, and write down the largest displacement it reaches: that is S_d(T). Repeat for many
# periods and you have the **displacement response spectrum** (the lesson of Session 3, Figure 3).
# Engineers usually plot the **pseudo-acceleration** S_a(T) = (2 pi / T)^2 S_d(T) instead, because
# S_a times a mass is the force that mass feels at its peak. Divide by the peak ground
# acceleration (2 m/s^2) and S_a / PGA says how many times the shaking is amplified at that period.
# The record is synthetic and rich around 1 s, so the amplification peaks between 0.5 and 1 s.

# %%
def response_spectrum(periods, a_g, dt, zeta=ZETA):
    """Displacement S_d (m) and pseudo-acceleration S_a = w^2 S_d (m/s^2) for each oscillator period (s)."""
    periods = np.atleast_1d(np.asarray(periods, float))
    sd = np.array([sdof_peak(T, zeta, a_g, dt) for T in periods])
    return sd, (2 * np.pi / periods) ** 2 * sd


def spectrum_function(a_g, dt, zeta=ZETA):
    """A function sd(T) that runs the oscillator for the requested period (the 'spectrum' of this record)."""
    return lambda T: sdof_peak(T, zeta, a_g, dt)


# %% [markdown]
# ## Step 2: the base shear of one mode
# If only mode i moved, the floors would reach u_i,max = Gamma_i phi_i S_d(T_i) at the peak: the mode
# shape times its participation times the spectrum. The floor forces that hold that shape are
# F_j = m_j Gamma_i phi_j,i w_i^2 S_d. Their sum is the base shear
#
#     V_i = w_i^2 Gamma_i * (phi_i^T M r) * S_d = M*_i S_a(T_i),
#
# the **effective modal mass times the pseudo-acceleration**. It is also k_1 u_1,max (the force in
# the lowest storey), and the code checks that the two agree. The first mode carries 85 percent of
# the mass, so V_1 is nearly the whole answer.

# %%
def modal_data(M, K):
    """Periods (s), angular frequencies (rad/s), participation factors and effective masses (kg) of all modes."""
    w, phi = modes(M, K)
    gamma, meff = participation(M, phi)
    return periods(w), w, phi, gamma, meff


def _count(nmodes, n):
    """Number of modes to use: all n by default, otherwise an integer from 1 to n."""
    if nmodes is None:
        return n
    if int(nmodes) != nmodes or not 1 <= nmodes <= n:
        raise ValueError(f"the number of modes must be a whole number from 1 to {n}")
    return int(nmodes)


def modal_base_shears(M, K, sd, nmodes=None):
    """Peak base shear of each mode (N): V_i = M*_i w_i^2 S_d(T_i). `sd` is a function sd(T) -> displacement (m)."""
    T, w, phi, gamma, meff = modal_data(M, K)
    nm = _count(nmodes, len(w))
    return np.array([meff[i] * w[i] ** 2 * sd(T[i]) for i in range(nm)])


def modal_base_shears_check(M, K, sd, k1):
    """Same numbers from the lowest storey: k_1 * Gamma_i * phi_1,i * S_d(T_i). Must equal modal_base_shears."""
    T, w, phi, gamma, meff = modal_data(M, K)
    return np.array([k1 * gamma[i] * phi[0, i] * sd(T[i]) for i in range(len(w))])


# %% [markdown]
# ## Step 3: combine the modes
# The modes do not all peak at the same moment, so adding the V_i would overestimate (it is an upper bound).
# The usual rule is **SRSS**: V = sqrt(sum V_i^2). It assumes the peaks are independent, which is
# reasonable when the periods are well apart. When two periods are close (ratio w_j / w_i near 1)
# the modes peak together and SRSS can be too small; the **CQC** rule fixes this with a
# correlation rho_ij between modes (for equal damping zeta and r = w_j / w_i):
#
#     rho_ij = 8 zeta^2 (1 + r) r^1.5 / ((1 - r^2)^2 + 4 zeta^2 r (1 + r)^2),   V^2 = sum_i sum_j rho_ij V_i V_j.
#
# rho = 1 for i = j and for r = 1, so CQC reduces to the plain sum for identical periods and to SRSS
# when the periods are far apart. In a shear building the periods are far apart (T_1 / T_2 = 3), so
# CQC and SRSS agree to within a fraction of a percent here.

# %%
def srss(v):
    return float(np.sqrt(np.sum(np.asarray(v, float) ** 2)))


def abs_sum(v):
    return float(np.sum(np.abs(v)))


def cqc_correlation(w_i, w_j, zeta=ZETA):
    """Correlation of two modes with equal damping (1 when w_i == w_j, near 0 when far apart)."""
    r = w_j / w_i
    return 8 * zeta ** 2 * (1 + r) * r ** 1.5 / ((1 - r ** 2) ** 2 + 4 * zeta ** 2 * r * (1 + r) ** 2)


def cqc(v, w, zeta=ZETA):
    v = np.asarray(v, float)
    tot = 0.0
    for i in range(len(v)):
        for j in range(len(v)):
            tot += cqc_correlation(w[i], w[j], zeta) * v[i] * v[j]
    return float(np.sqrt(tot))


# %% [markdown]
# ## Step 4: the shortcut against the full time history
# `shortcut_base_shear` returns the SRSS (or CQC, or sum) estimate from the spectrum of a record.
# `time_history_base_shear` is the Session 3 answer: Newmark integration of all ten modes and the
# peak of |k_1 u_1|. `modes_needed` counts how many modes make up a chosen share of the mass
# (codes ask for 90 percent). The roadmap checkpoint for this session: the first three modes
# combined by SRSS must be within 5 percent of the full time-history run for the ten-storey frame.

# %%
def shortcut_base_shear(M, K, a_g, dt, nmodes=3, rule="srss", zeta=ZETA):
    """Estimated peak base shear (N) from the response spectrum of a_g and the first `nmodes` modes."""
    sd = spectrum_function(a_g, dt, zeta)
    v = modal_base_shears(M, K, sd, nmodes)
    if rule == "srss":
        return srss(v)
    if rule == "sum":
        return abs_sum(v)
    if rule == "cqc":
        return cqc(v, modes(M, K)[0][:nmodes], zeta)
    raise ValueError("rule must be 'srss', 'sum' or 'cqc'")


def time_history_base_shear(M, K, k1, a_g, dt, zeta=ZETA):
    """Peak |base shear| (N) from the full Newmark run with 5 percent damping in every mode."""
    w, phi = modes(M, K)
    u, _, _ = newmark(M, damping_matrix(M, phi, w, zeta), K, a_g, dt)
    return float(np.abs(base_shear(u, k1)).max())


def modal_base_shear_histories(M, K, k1, a_g, dt, zeta=ZETA):
    """Base shear of every mode against time, array (n_steps, n_modes) in N. Their sum over the modes is the full
    base-shear history; the peak of each column is the V_i of the shortcut."""
    T, w, phi, gamma, meff = modal_data(M, K)
    cols = []
    for i in range(len(w)):
        q, _ = sdof_response(w[i], zeta, gamma[i] * a_g, dt)
        cols.append(k1 * phi[0, i] * q)
    return np.array(cols).T


def modes_needed(meff, share=0.90):
    """Smallest number of modes whose effective masses add up to at least `share` of the total mass."""
    cum = np.cumsum(meff) / np.sum(meff)
    return int(np.searchsorted(cum, share - 1e-12) + 1)


def shortcut_error(M, K, k1, a_g, dt, nmodes=3, rule="srss", zeta=ZETA):
    """Relative error (estimate - time history) / time history; positive means the shortcut is on the safe (high) side."""
    th = time_history_base_shear(M, K, k1, a_g, dt, zeta)
    return shortcut_base_shear(M, K, a_g, dt, nmodes, rule, zeta) / th - 1.0


# %% [markdown]
# ## Step 5: shears up the building
# Each mode also gives a **storey shear** at every level: add up the floor forces F_j above the storey
# (a floor force at the top is carried down through all the storeys below it). Combine the modes
# storey by storey with SRSS and compare with the largest shear k_j (u_j - u_(j-1)) of the time history. The base
# is the special case of the lowest storey.

# %%
def modal_storey_shears(M, K, sd, nmodes=None):
    """Peak storey shear of each mode, array (nmodes, n): row i, column j is the shear in storey j+1 (N)."""
    T, w, phi, gamma, meff = modal_data(M, K)
    nm = _count(nmodes, len(w))
    m = np.diag(M)
    out = np.zeros((nm, len(m)))
    for i in range(nm):
        f = m * gamma[i] * phi[:, i] * w[i] ** 2 * sd(T[i])        # floor forces (N)
        out[i] = np.cumsum(f[::-1])[::-1]                           # shear in storey j = sum of forces on floors j..n
    return out


def srss_storey_shears(M, K, a_g, dt, nmodes=3, zeta=ZETA):
    return np.sqrt((modal_storey_shears(M, K, spectrum_function(a_g, dt, zeta), nmodes) ** 2).sum(axis=0))


def time_history_storey_shears(M, K, k, a_g, dt, zeta=ZETA):
    """Peak |k_j drift_j| of every storey from the full time history (N)."""
    w, phi = modes(M, K)
    u, _, _ = newmark(M, damping_matrix(M, phi, w, zeta), K, a_g, dt)
    kk = np.broadcast_to(np.asarray(k, float), (M.shape[0],))
    return np.abs(storey_drift(u)).max(axis=0) * kk


# %% [markdown]
# ## Step 6: when can you trust it? A screening test
# The test below runs the whole chain for storey stiffnesses from 100 to 1500 MN/m (first periods
# from 1.9 s to 0.5 s) with the same record, and reports the error of the 3-mode SRSS estimate. A
# shortcut for *screening* is useful only if its error is small over the range where you will use
# it, so we count how many stiffnesses stay within 5 percent.

# %%
STIFFNESSES_MN = tuple(range(100, 1501, 100))


def error_vs_stiffness(a_g, dt, stiffnesses_mn=STIFFNESSES_MN, nmodes=3, n=N_FLOORS, m=M_FLOOR):
    """List of (k in MN/m, first period s, time history MN, estimate MN, error)."""
    rows = []
    for kmn in stiffnesses_mn:
        k = kmn * 1e6
        M, K = shear_building(n, m, k)
        th = time_history_base_shear(M, K, k, a_g, dt)
        est = shortcut_base_shear(M, K, a_g, dt, nmodes)
        rows.append((float(kmn), float(periods(modes(M, K)[0])[0]), th / 1e6, est / 1e6, est / th - 1.0))
    return rows


def passing(rows, limit=0.05):
    return [r[0] for r in rows if abs(r[4]) <= limit]


# %% [markdown]
# ## See it
# Figure 1: the spectrum of the record with the first three modes marked. Figure 2: the modal
# base shears, the combinations and the time history; and the storey shears up the building. Figure 3:
# the error of the shortcut against the storey stiffness.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA = "#0072b2", "#c86a00", "#d81b60"
    M, K = shear_building()
    t, ag = synthetic_ground()
    dt = t[1] - t[0]
    T, w, phi, gamma, meff = modal_data(M, K)
    sd = spectrum_function(ag, dt)
    v = modal_base_shears(M, K, sd)
    th = time_history_base_shear(M, K, K_STOREY, ag, dt)
    print("periods (s):", np.round(T[:4], 3), " effective mass shares:", np.round(meff[:4] / meff.sum(), 3))
    print("modal base shears (MN):", np.round(v[:4] / 1e6, 3), " check:", np.round(modal_base_shears_check(M, K, sd, K_STOREY)[:4] / 1e6, 3))
    for nm in (1, 2, 3, 5, 10):
        vv = v[:nm]
        print(f"{nm:2d} modes: SRSS {srss(vv) / 1e6:6.3f} MN ({100 * (srss(vv) / th - 1):+5.1f} %)   sum {abs_sum(vv) / 1e6:6.3f} MN ({100 * (abs_sum(vv) / th - 1):+5.1f} %)")
    print(f"time history {th / 1e6:.3f} MN;  CQC (3 modes) {cqc(v[:3], w[:3]) / 1e6:.3f} MN;  modes for 90 percent of the mass: {modes_needed(meff)}")

    grid = np.linspace(0.1, 3.0, 146)
    sdg, sag = response_spectrum(grid, ag, dt)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(grid, sag / 2.0, color=BLUE, lw=1.6, label="record, 5% damping")
    for i, col in zip(range(3), (ORANGE, MAGENTA, "#444444")):
        sa_i = (2 * np.pi / T[i]) ** 2 * sd(T[i]) / 2.0
        ax.plot([T[i], T[i]], [0, sa_i], ":", color=col)
        ax.plot(T[i], sa_i, "o", color=col, label=f"mode {i + 1}: T = {T[i]:.2f} s, {meff[i] / meff.sum() * 100:.0f}% of the mass")
    ax.set_xlabel("oscillator period T (s)")
    ax.set_ylabel("pseudo-acceleration / peak ground acceleration")
    ax.set_title("Response spectrum of the record, with the first modes", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "spectrum_modes.png", dpi=120)

    fig2, axs = plt.subplots(1, 2, figsize=(10.2, 4.2))
    labels = ["mode 1", "mode 2", "mode 3", "SRSS\n(3 modes)", "sum\n(3 modes)", "time\nhistory"]
    vals = [v[0], v[1], v[2], srss(v[:3]), abs_sum(v[:3]), th]
    cols = [BLUE, BLUE, BLUE, ORANGE, "#999999", MAGENTA]
    axs[0].bar(labels, np.array(vals) / 1e6, color=cols)
    axs[0].set_ylabel("peak base shear (MN)")
    axs[0].set_title("Modal shears, their combinations and the full run", fontsize=10)
    axs[0].grid(alpha=0.3, axis="y")
    for x, val in enumerate(vals):
        axs[0].text(x, val / 1e6 + 0.1, f"{val / 1e6:.2f}", ha="center", fontsize=8)
    ssh = srss_storey_shears(M, K, ag, dt)
    tsh = time_history_storey_shears(M, K, K_STOREY, ag, dt)
    st = np.arange(1, N_FLOORS + 1)
    axs[1].plot(tsh / 1e6, st, "o-", color=MAGENTA, label="time history")
    axs[1].plot(ssh / 1e6, st, "s--", color=ORANGE, label="spectrum + SRSS (3 modes)")
    axs[1].set_xlabel("peak storey shear (MN)")
    axs[1].set_ylabel("storey")
    axs[1].set_title("Shear up the building", fontsize=10)
    axs[1].legend(fontsize=8)
    axs[1].grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "storey_shear.png", dpi=120)
    print("storey shears at the base: SRSS", round(ssh[0] / 1e6, 3), " time history", round(tsh[0] / 1e6, 3), " top storey:", round(ssh[-1] / 1e6, 3), round(tsh[-1] / 1e6, 3))

    rows = error_vs_stiffness(ag, dt)
    ok = passing(rows)
    print("stiffness (MN/m), T1 (s), time history, estimate (MN), error:")
    for r in rows:
        print(f"  {r[0]:6.0f} {r[1]:6.3f} {r[2]:7.2f} {r[3]:7.2f} {100 * r[4]:+6.1f} %")
    print("within 5 percent:", len(ok), "of", len(rows), "->", [int(x) for x in ok])
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.0))
    ks = [r[0] for r in rows]
    errs = [100 * r[4] for r in rows]
    ax3.axhspan(-5, 5, color=BLUE, alpha=0.12, label="within 5 percent")
    ax3.plot(ks, errs, "o-", color=BLUE)
    for kx, ex in zip(ks, errs):
        if abs(ex) > 5:
            ax3.plot(kx, ex, "o", color=MAGENTA, ms=9)
    ax3.axhline(0, color="black", lw=0.8)
    ax3.set_xlabel("storey stiffness (MN/m)")
    ax3.set_ylabel("shortcut error (percent)")
    ax3.set_title("3-mode SRSS against the time history", fontsize=10)
    ax3.legend(fontsize=8)
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "error_vs_stiffness.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# One synthetic record, a linear shear building and a rough spectrum: the shortcut is a screening
# tool whose error you have now measured on a toy. Real codes use smooth design spectra built
# from many records, and real buildings yield. Never use this for design.
