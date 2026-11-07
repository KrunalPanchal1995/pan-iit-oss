"""Session 3 (Level 3): an N-storey shear building shaken by a synthetic ground-motion record.

Educational model only. Never use it for real seismic design.
Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: many floors, many mode shapes
# **A. Real-world problem.** A ten-storey frame does not sway as one lump. Each floor is a mass,
# each storey of columns is a spring, and the whole stack can bend in ten different patterns
# (*modes*), each with its own period. We shake it with a synthetic earthquake record, solve
# it two independent ways (modal superposition and direct Newmark-beta integration), check
# energy, and then watch a weak ("soft") storey ruin the drift.
#
# **Plan.** (1) build M and K, (2) solve K phi = w^2 M phi and check against the analytic
# uniform-building formula, (3) modal participation and effective mass, (4) a seeded synthetic
# ground record, (5) two time-domain solvers that must agree, (6) drift and base shear.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
N_FLOORS = 10
M_FLOOR = 2.0e5          # kg per floor (200 tonnes)
K_STOREY = 3.5e8         # N/m per storey (all columns of one storey together)
ZETA = 0.05              # damping ratio in every mode


# %% [markdown]
# ## Step 1: the matrices
# Floor j has displacement u_j (relative to the ground). Storey j connects floor j-1 to floor j
# (floor 0 is the fixed ground). The equations of motion are  M u'' + C u' + K u = -M r a_g(t),
# where r is the vector of ones (the ground pushes every floor the same way) and a_g is the
# ground acceleration. K is *tridiagonal*: each floor only feels its two neighbours.

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


# %% [markdown]
# ## Step 2: natural frequencies and mode shapes
# Free vibration u = phi cos(w t) gives the generalised eigenproblem  K phi = w^2 M phi.
# M is diagonal, so M^(-1/2) exists. Put phi = M^(-1/2) v: then  (M^(-1/2) K M^(-1/2)) v = w^2 v,
# an ordinary symmetric eigenproblem that np.linalg.eigh solves. We scale each phi so that
# phi^T M phi = 1 (mass-normalised) and flip its sign so the roof moves positive.

# %%
def modes(M, K):
    """Return (w, phi): angular frequencies (rad/s, ascending) and mass-normalised mode shapes (columns)."""
    s = 1.0 / np.sqrt(np.diag(M))
    A = (s[:, None] * K) * s[None, :]
    w2, v = np.linalg.eigh(A)
    phi = s[:, None] * v
    phi = phi * np.where(phi[-1, :] < 0, -1.0, 1.0)
    return np.sqrt(w2), phi


def uniform_analytic(n, m, k):
    """Standard result for equal masses m and equal storey stiffness k, fixed base, free top:
    w_i = 2 sqrt(k/m) sin((2i-1) pi / (2 (2n+1))),  shape_j = sin((2i-1) j pi / (2n+1)), j = 1..n.
    Returns (w, shapes) with the shapes scaled to a roof value of 1 (columns)."""
    i = np.arange(1, n + 1)
    w = 2.0 * np.sqrt(k / m) * np.sin((2 * i - 1) * np.pi / (2 * (2 * n + 1)))
    j = np.arange(1, n + 1)
    sh = np.sin(np.outer(j, (2 * i - 1)) * np.pi / (2 * n + 1))
    return w, sh / sh[-1, :]


def periods(w):
    return 2 * np.pi / w


# %% [markdown]
# ## Step 3: how much of the building each mode moves
# Participation factor  Gamma_i = phi_i^T M r  (mass-normalised shapes). Effective modal mass
# M*_i = Gamma_i^2. Together the effective masses add up to the total mass, and the first
# mode carries most of it.

# %%
def participation(M, phi):
    r = np.ones(M.shape[0])
    gamma = phi.T @ M @ r
    return gamma, gamma ** 2


# %% [markdown]
# ## Step 4: a synthetic ground-motion record
# **This is not a real earthquake.** It is a sum of 120 sine waves with random (seeded) phases,
# amplitudes peaked around a dominant period, and a rise-hold-fade envelope. Real records
# differ; the point is to have a repeatable, rich shaking that is centred near 1 s.

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


# %% [markdown]
# ## Step 5: two independent solvers
# **Modal superposition.** Each mode is a one-degree-of-freedom oscillator
# q'' + 2 zeta w q' + w^2 q = -Gamma a_g(t), solved *exactly* for a ground record that is
# piecewise linear between samples (the Nigam-Jennings recurrence, done here by the exact
# 2x2 state transition). Then u = sum_i phi_i q_i.
#
# **Direct Newmark-beta.** Step the full matrix equation with the *average acceleration*
# method, beta = 1/4 and gamma = 1/2: unconditionally stable, and no numerical damping.
# The damping matrix C = M Phi diag(2 zeta w) Phi^T M gives exactly zeta in every mode.
#
# **Rayleigh damping.** Many programs do not know the modes in advance and build
# C = a0 M + a1 K instead. Mode i then gets zeta_i = a0 / (2 w_i) + a1 w_i / 2: the mass part
# damps low modes most, the stiffness part damps high modes most, so zeta is high at both ends
# and lowest in between. Choose two modes, set zeta there (5 percent), and solve for a0 and a1.

# %%
def damping_matrix(M, phi, w, zeta=ZETA):
    return M @ phi @ np.diag(2 * zeta * w) @ phi.T @ M


def rayleigh_coefficients(w_a, w_b, zeta_a=ZETA, zeta_b=ZETA):
    """a0, a1 of C = a0 M + a1 K that give damping ratio zeta_a at w_a and zeta_b at w_b (rad/s).

    A mode with frequency w gets zeta(w) = a0 / (2 w) + a1 w / 2, so two chosen modes give two
    linear equations for a0 and a1."""
    A = np.array([[1 / (2 * w_a), w_a / 2], [1 / (2 * w_b), w_b / 2]])
    return tuple(np.linalg.solve(A, [zeta_a, zeta_b]))


def rayleigh_damping(M, K, w, modes=(0, 2), zeta=ZETA):
    """Rayleigh damping matrix C = a0 M + a1 K with `zeta` at the two chosen modes (0-based indices).

    Returns C, a0, a1. Unlike damping_matrix (the same zeta in every mode), the other modes get
    whatever the formula gives: see rayleigh_ratio."""
    a0, a1 = rayleigh_coefficients(w[modes[0]], w[modes[1]], zeta, zeta)
    return a0 * M + a1 * K, a0, a1


def rayleigh_ratio(w, a0, a1):
    """Damping ratio the Rayleigh matrix gives to a mode of frequency w (scalar or array)."""
    w = np.asarray(w, dtype=float)
    return a0 / (2 * w) + a1 * w / 2


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


def modal_response(M, K, a_g, dt, zeta=ZETA, nmodes=None):
    """Floor displacements (n_steps, n) by modal superposition with the first `nmodes` modes (default all)."""
    w, phi = modes(M, K)
    gamma, _ = participation(M, phi)
    nm = len(w) if nmodes is None else nmodes
    u = np.zeros((a_g.size, len(w)))
    for i in range(nm):
        q, _ = sdof_response(w[i], zeta, gamma[i] * a_g, dt)
        u += np.outer(q, phi[:, i])
    return u


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


# %% [markdown]
# ## Step 6: what engineers read off
# * **Inter-storey drift** = u_j - u_(j-1), the bending of one storey (drift ratio = drift / storey height).
# * **Base shear** = the force in the lowest storey = k_1 u_1 (what the foundation must resist).
# * **Energy balance**: input energy = kinetic + strain + damping dissipated.

# %%
def storey_drift(u):
    return np.diff(np.hstack([np.zeros((u.shape[0], 1)), u]), axis=1)


def base_shear(u, k1):
    return k1 * u[:, 0]


def energy_balance(M, C, K, u, v, a_g, dt):
    """Return (input, kinetic + strain + damped) at the final step, in joules (J)."""
    r = np.ones(M.shape[0])
    f_in = -(v @ (M @ r)) * a_g                       # power put in by the ground (W)
    e_in = np.concatenate([[0.0], np.cumsum(0.5 * (f_in[1:] + f_in[:-1]) * dt)])
    p_damp = np.einsum("ti,ij,tj->t", v, C, v)
    e_damp = np.concatenate([[0.0], np.cumsum(0.5 * (p_damp[1:] + p_damp[:-1]) * dt)])
    e_kin = 0.5 * np.einsum("ti,ij,tj->t", v, M, v)
    e_strain = 0.5 * np.einsum("ti,ij,tj->t", u, K, u)
    return e_in, e_kin + e_strain + e_damp


def sdof_peak(period, zeta, a_g, dt):
    """Peak |relative displacement| (m) of a one-degree-of-freedom oscillator: one point of the response spectrum."""
    q, _ = sdof_response(2 * np.pi / period, zeta, a_g, dt)
    return float(np.abs(q).max())


STOREY_HEIGHT = 3.5      # m, used to turn drift into a drift ratio


def peaks(k=K_STOREY, zeta=ZETA, seed=7, t_dom=1.0, pga=2.0, n=N_FLOORS, m=M_FLOOR):
    """Run the whole chain (Newmark) and return peak roof displacement (m), peak drift (m), peak base shear (N), first period (s)."""
    t, ag = synthetic_ground(seed=seed, t_dom=t_dom, pga=pga)
    dt = t[1] - t[0]
    M, K = shear_building(n, m, k)
    w, phi = modes(M, K)
    C = damping_matrix(M, phi, w, zeta)
    u, _, _ = newmark(M, C, K, ag, dt)
    k1 = np.broadcast_to(np.asarray(k, float), (n,))[0]
    return {"roof": float(np.abs(u[:, -1]).max()), "drift": float(np.abs(storey_drift(u)).max()),
            "shear": float(np.abs(base_shear(u, k1)).max()), "T1": float(2 * np.pi / w[0])}


def with_damper(M, K, w1, mass_ratio=0.02, zeta_d=0.10):
    """Stretch idea: a tuned mass damper on the roof. Adds one more mass (mass_ratio * total mass) joined to the roof
    by a spring tuned to the first mode and a dashpot. Returns (M2, C2, K2) for the building plus damper."""
    n = M.shape[0]
    md = mass_ratio * np.trace(M)
    kd = md * w1 ** 2
    cd = 2 * zeta_d * md * w1
    w, phi = modes(M, K)
    C = damping_matrix(M, phi, w)
    M2 = np.zeros((n + 1, n + 1)); K2 = np.zeros((n + 1, n + 1)); C2 = np.zeros((n + 1, n + 1))
    M2[:n, :n] = M; K2[:n, :n] = K; C2[:n, :n] = C
    M2[n, n] = md
    for A, c in ((K2, kd), (C2, cd)):
        A[n - 1, n - 1] += c; A[n, n] += c; A[n - 1, n] -= c; A[n, n - 1] -= c
    return M2, C2, K2


def resonant_ground(w, dur=24.0, dt=0.01, a0=2.0):
    """A pure sine at angular frequency w (rad/s) with a 3 s fade-in: the worst case for a building with that frequency."""
    t = np.arange(0.0, dur + 0.5 * dt, dt)
    return t, a0 * np.sin(w * t) * np.clip(t / 3.0, 0, 1)


def soft_storey_stiffness(n=N_FLOORS, k=K_STOREY, which=0, factor=0.35):
    ks = np.full(n, k)
    ks[which] = factor * k
    return ks


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    M, K = shear_building()
    w, phi = modes(M, K)
    wa, sa = uniform_analytic(N_FLOORS, M_FLOOR, K_STOREY)
    print("periods (s):", np.round(periods(w)[:4], 4), " analytic:", np.round(periods(wa)[:4], 4))
    gamma, meff = participation(M, phi)
    print("effective mass fractions:", np.round(meff[:3] / meff.sum(), 3), " sum =", round(meff.sum() / np.trace(M), 6))

    t, ag = synthetic_ground()
    dt = t[1] - t[0]
    C = damping_matrix(M, phi, w)
    un, vn, an = newmark(M, C, K, ag, dt)
    um = modal_response(M, K, ag, dt)
    print("max |modal - Newmark| / peak:", np.abs(um - un).max() / np.abs(un).max())
    ein, estored = energy_balance(M, C, K, un, vn, ag, dt)
    print("energy in, accounted:", ein[-1], estored[-1])
    d = storey_drift(un)
    print("peak drift per storey (mm):", np.round(1e3 * np.abs(d).max(axis=0), 1))
    print("peak base shear (MN):", base_shear(un, K_STOREY).__abs__().max() / 1e6)

    fig, ax = plt.subplots(1, 3, figsize=(11, 3.8))
    y = np.arange(0, N_FLOORS + 1)
    for i in range(3):
        ax[0].plot(np.r_[0, phi[:, i] / phi[-1, i]], y, "o-", label=f"mode {i + 1}, T = {periods(w)[i]:.3f} s")
        ax[0].plot(np.r_[0, sa[:, i]], y, "k.", ms=3)
    ax[0].set_xlabel("mode shape (roof = 1)")
    ax[0].set_ylabel("floor number")
    ax[0].set_title("Mode shapes (dots: analytic)")
    ax[0].legend(fontsize=7)
    ax[0].grid(alpha=0.3)
    ax[1].plot(t, 1e3 * un[:, -1], label="Newmark, roof")
    ax[1].plot(t, 1e3 * um[:, -1], "--", label="modal, roof")
    ax[1].set_xlabel("time (s)")
    ax[1].set_ylabel("roof displacement (mm)")
    ax[1].set_title("Two solvers, one answer")
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3)
    ax[2].plot(t, ag, lw=0.7)
    ax[2].set_xlabel("time (s)")
    ax[2].set_ylabel("ground acceleration (m/s^2)")
    ax[2].set_title("Synthetic record (not a real quake)")
    ax[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "modes_and_response.png", dpi=120)

    Ks = shear_building(k=soft_storey_stiffness())[1]
    ws, ps = modes(M, Ks)
    Cs = damping_matrix(M, ps, ws)
    us, _, _ = newmark(M, Cs, Ks, ag, dt)
    ds = np.abs(storey_drift(us)).max(axis=0)
    fig2, ax2 = plt.subplots(figsize=(5, 4.2))
    ax2.barh(np.arange(1, 11) - 0.2, 1e3 * np.abs(d).max(axis=0), 0.4, label="uniform")
    ax2.barh(np.arange(1, 11) + 0.2, 1e3 * ds, 0.4, label="soft storey 1 (35% stiffness)")
    ax2.set_xlabel("peak inter-storey drift (mm)")
    ax2.set_ylabel("storey")
    ax2.set_title("A weak storey collects the drift")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "soft_storey.png", dpi=120)
    print("soft storey 1 peak drift (mm):", 1e3 * ds[0], " uniform:", 1e3 * np.abs(d).max(axis=0)[0])

    periods_grid = np.linspace(0.1, 3.0, 59)
    sd = [sdof_peak(T, ZETA, ag, dt) for T in periods_grid]
    fig3, ax3 = plt.subplots(figsize=(5.5, 4))
    ax3.plot(periods_grid, 1e3 * np.array(sd))
    ax3.set_xlabel("oscillator period (s)")
    ax3.set_ylabel("peak displacement (mm)")
    ax3.set_title("Displacement response spectrum, 5% damping")
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "response_spectrum.png", dpi=120)

    # Rayleigh damping: damping ratio against mode number for two choices of anchor modes
    modes_n = np.arange(1, N_FLOORS + 1)
    fig4, ax4 = plt.subplots(figsize=(5.8, 4))
    ax4.axhline(100 * ZETA, color="0.5", ls=":", label="modal damping: 5% in every mode")
    for pair, col, mk in (((0, 2), "#003f7f", "o"), ((0, 9), "#c86a00", "s")):
        Cr, a0r, a1r = rayleigh_damping(M, K, w, pair)
        ax4.plot(modes_n, 100 * rayleigh_ratio(w, a0r, a1r), mk + "-", color=col,
                 label=f"Rayleigh, 5% at modes {pair[0] + 1} and {pair[1] + 1}")
        ax4.plot([pair[0] + 1, pair[1] + 1], [5, 5], mk, ms=11, mfc="none", color=col)
    ax4.set_xlabel("mode number")
    ax4.set_ylabel("damping ratio (percent of critical)")
    ax4.set_title("Rayleigh damping is not the same in every mode")
    ax4.set_ylim(0, 14)
    ax4.legend(fontsize=7.5)
    ax4.grid(alpha=0.3)
    fig4.tight_layout()
    fig4.savefig(OUT / "rayleigh_damping.png", dpi=120)
    Cr, a0r, a1r = rayleigh_damping(M, K, w, (0, 2))
    ur, _, _ = newmark(M, Cr, K, ag, dt)
    print("Rayleigh (modes 1 and 3): a0 =", round(a0r, 4), "a1 =", round(a1r, 5),
          " roof peak (mm):", round(1e3 * np.abs(ur[:, -1]).max(), 2), " vs modal damping:", round(1e3 * np.abs(un[:, -1]).max(), 2))

# %% [markdown]
# ## Where this stops
# Real buildings yield, crack and twist, and real earthquakes are not one synthetic record. This
# model is linear, planar and fixed at the base: use it to build intuition, never to design.
