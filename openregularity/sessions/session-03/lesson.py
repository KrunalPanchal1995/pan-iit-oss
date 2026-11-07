"""Session 3 (Level 3): 2-D Navier-Stokes, vortex stretching in 3-D, and numerical blow-up.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: why 2-D is understood, what is different in 3-D, and how to avoid fooling yourself
# **A. Real-world problem.** A weather map is close to a 2-D flow; a turbulent pipe is 3-D. For
# 2-D incompressible Navier-Stokes we know that smooth solutions exist for all time. For 3-D we
# do not know (a Clay Millennium Prize problem, stated by Fefferman).
#
# **HONESTY NOTE.** Nothing in this session proves or hints at a 3-D answer. We (1) solve the
# 2-D equations with a spectral method and check them against an exact solution, (2) see
# numerically that the 2-D enstrophy cannot grow, (3) compute the 3-D vortex stretching term on
# one given field, and (4) show that a numerical solver can blow up without any real singularity.
#
# **Plan.** vorticity form -> solver -> checks -> stretching term -> failure case -> mini-project.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: 2-D Navier-Stokes in vorticity form
# In 2-D the velocity is (u, v) and the vorticity is the single number w = v_x - u_y (how fast a
# little paddle would spin). With a stream function psi (u = psi_y, v = -psi_x) we get
# Laplacian(psi) = -w, and Navier-Stokes becomes
#
#     w_t + u w_x + v w_y = nu * Laplacian(w).
#
# There is NO term that stretches w: vorticity is only carried along and diffused. In Fourier
# space, psi_hat = w_hat / k^2, so the Poisson solve is one division. We use a periodic box
# [0, 2 pi)^2, the 2/3 rule (drop wavenumbers with |kx| or |ky| >= N/3) and RK4 with the
# viscous term done exactly (integrating factor).

# %%
def make_grid(n):
    x = 2 * np.pi * np.arange(n) / n
    X, Y = np.meshgrid(x, x, indexing="ij")
    k = np.fft.fftfreq(n, 1.0 / n)
    KX, KY = np.meshgrid(k, k, indexing="ij")
    return X, Y, KX, KY


def taylor_green_vorticity(n, k=1):
    """w0 = 2 k sin(kx) sin(ky), from u = sin kx cos ky, v = -cos kx sin ky (k = whole number)."""
    X, Y, _, _ = make_grid(n)
    return 2.0 * k * np.sin(k * X) * np.sin(k * Y)


def random_vorticity(n, seed=1, kmax=6, max_w=3.0):
    """Reproducible random vorticity with wavenumbers up to kmax, scaled so max |w| = max_w."""
    rng = np.random.default_rng(seed)
    _, _, KX, KY = make_grid(n)
    kk = np.sqrt(KX ** 2 + KY ** 2)
    wh = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) * ((kk > 0) & (kk <= kmax)) / np.maximum(kk, 1.0)
    w = np.fft.ifft2(wh).real
    return w * (max_w / np.max(np.abs(w)))


def run_ns2d(w0, nu, t_end, dt=0.005, dealias=True):
    """Evolve the vorticity w0 on a periodic box.

    Returns (t, energy, enstrophy, max|w|, final w, palinstrophy) with
    energy = mean(u^2 + v^2)/2, enstrophy = mean(w^2)/2, palinstrophy = mean(|grad w|^2)/2.
    """
    n = w0.shape[0]
    _, _, KX, KY = make_grid(n)
    k2 = KX ** 2 + KY ** 2
    inv = np.where(k2 > 0, 1.0 / np.where(k2 > 0, k2, 1.0), 0.0)
    mask = ((np.abs(KX) < n / 3.0) & (np.abs(KY) < n / 3.0)) if dealias else 1.0
    half = np.exp(-nu * k2 * dt / 2.0)

    def velocity(wh):
        psi = wh * inv
        return np.fft.ifft2(1j * KY * psi).real, np.fft.ifft2(-1j * KX * psi).real

    def rhs(wh):
        u, v = velocity(wh)
        wx = np.fft.ifft2(1j * KX * wh).real
        wy = np.fft.ifft2(1j * KY * wh).real
        return -np.fft.fft2(u * wx + v * wy) * mask

    def diagnostics(wh):
        u, v = velocity(wh)
        w = np.fft.ifft2(wh).real
        wx = np.fft.ifft2(1j * KX * wh).real
        wy = np.fft.ifft2(1j * KY * wh).real
        return (0.5 * np.mean(u * u + v * v), 0.5 * np.mean(w * w), float(np.max(np.abs(w))),
                0.5 * np.mean(wx * wx + wy * wy))

    wh = np.fft.fft2(w0) * mask
    rec = [(0.0,) + diagnostics(wh)]
    for i in range(int(round(t_end / dt))):
        a = rhs(wh)
        b = rhs(half * (wh + 0.5 * dt * a))
        c = rhs(half * wh + 0.5 * dt * b)
        d = rhs(half * half * wh + dt * half * c)
        wh = half * half * wh + dt / 6.0 * (half * half * a + 2 * half * (b + c) + d)
        rec.append(((i + 1) * dt,) + diagnostics(wh))
    r = np.array(rec)
    return r[:, 0], r[:, 1], r[:, 2], r[:, 3], np.fft.ifft2(wh).real, r[:, 4]


def trapezoid(y, t):
    y, t = np.asarray(y), np.asarray(t)
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(t)))


# %% [markdown]
# ## Step 2: checks in 2-D
# * Taylor-Green: w0 = 2 sin x sin y is an exact solution that only decays,
#   w(t) = w0 * exp(-2 nu t). The nonlinear term vanishes identically for it.
# * Energy: dE/dt = -2 nu Z, where Z = mean(w^2)/2 is the enstrophy.
# * Enstrophy: dZ/dt = -2 nu P, where P = mean(|grad w|^2)/2 >= 0. With no stretching term the
#   enstrophy cannot grow: Z(t) <= Z(0) for nu > 0.
# * Beale-Kato-Majda (BKM) criterion, in words: a smooth 3-D solution can be continued past a
#   time T as long as the time integral of the maximum vorticity up to T is finite. In our 2-D
#   runs that integral is trivially finite, since max|w| never exceeds its initial value.

# %%
def bkm_integral(t, max_w):
    """Time integral of max |w| (the quantity in the Beale-Kato-Majda criterion)."""
    return trapezoid(max_w, t)


# %% [markdown]
# ## Step 3: the 3-D vortex stretching term
# In 3-D the vorticity is a vector w = curl(u) and its equation contains (w . grad) u. Writing
# the velocity gradient as strain S (symmetric part) plus rotation, (w . grad) u = S w. The
# number w . S w is positive where vortex lines are being stretched (spin increases) and
# negative where they are compressed. This term has no 2-D counterpart and is the usual
# suspect in discussions of possible 3-D blow-up. IT IS NOT KNOWN WHETHER IT CAN WIN: the
# problem is open. We only evaluate the term on a given field: the 3-D Taylor-Green flow
# u = sin x cos y cos z, v = -cos x sin y cos z, w = 0 (spectral derivatives, N^3 points).

# %%
def spectral_gradient(f):
    n = f.shape[0]
    k = np.fft.fftfreq(n, 1.0 / n)
    K = np.meshgrid(k, k, k, indexing="ij")
    fh = np.fft.fftn(f)
    return np.array([np.fft.ifftn(1j * K[d] * fh).real for d in range(3)])


def taylor_green_3d(n=16, with_z=True):
    """3-D Taylor-Green velocity (3, n, n, n); with_z=False gives the 2-D flow extended in z."""
    x = 2 * np.pi * np.arange(n) / n
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    cz = np.cos(Z) if with_z else 1.0
    return np.array([np.sin(X) * np.cos(Y) * cz, -np.cos(X) * np.sin(Y) * cz, np.zeros_like(X)])


def stretching_fields(u):
    """Return (vorticity, (w.grad)u, w.S.w) for a velocity field u of shape (3, n, n, n)."""
    G = np.array([spectral_gradient(u[i]) for i in range(3)])      # G[i, j] = d_j u_i
    S = 0.5 * (G + G.transpose(1, 0, 2, 3, 4))
    w = np.array([G[2, 1] - G[1, 2], G[0, 2] - G[2, 0], G[1, 0] - G[0, 1]])
    stretch_vec = np.einsum("ij...,j...->i...", G, w)
    wSw = np.einsum("i...,ij...,j...->...", w, S, w)
    return w, stretch_vec, wSw


# %% [markdown]
# ## Step 4: a failure case, numerical blow-up is not a singularity
# Back to 1-D Burgers with a small viscosity. If the grid is too coarse and nothing removes
# aliasing, the computed solution can explode (overflow to infinity) although the true solution
# is smooth for every nu > 0. Adding resolution removes the "blow-up". The lesson: a solver
# going to infinity is a warning about the solver, not evidence about the equation. Claims of
# real singularities need resolution studies, error bounds, or computer-assisted proofs.

# %%
def burgers_run(nu, n, t_end=3.0, dt=0.004, dealias=True):
    """Viscous Burgers (u0 = sin x). Returns (peak of max|u_x| over time, max energy, finite flag)."""
    x = 2 * np.pi * np.arange(n) / n
    k = np.fft.fftfreq(n, 1.0 / n)
    keep = (np.abs(k) < n / 3.0) if dealias else np.ones(n, dtype=bool)
    e = np.exp(-nu * k ** 2 * dt / 2.0)
    f = lambda vh: -0.5j * k * np.fft.fft(np.fft.ifft(vh).real ** 2) * keep
    vh = np.fft.fft(np.sin(x))
    peak, emax = 1.0, 0.25
    with np.errstate(all="ignore"):
        for _ in range(int(round(t_end / dt))):
            a = f(vh)
            b = f(e * (vh + 0.5 * dt * a))
            c = f(e * vh + 0.5 * dt * b)
            d = f(e * e * vh + dt * e * c)
            vh = e * e * vh + dt / 6.0 * (e * e * a + 2 * e * (b + c) + d)
            if not np.all(np.isfinite(vh)) or np.max(np.abs(vh)) > 1e8:
                return float("inf"), float("inf"), False
            u = np.fft.ifft(vh).real
            peak = max(peak, float(np.max(np.abs(np.fft.ifft(1j * k * vh).real))))
            emax = max(emax, 0.5 * float(np.mean(u * u)))
    return peak, emax, True


# %% [markdown]
# ## Step 5: mini-project helper
# Run `burgers_run` for a chosen nu on N = 16, 32, ..., 2048 and call the result converged at
# the first N whose peak gradient differs from the next size up (2N) by less than 1 percent.

# %%
def convergence_report(nu, sizes=(32, 64, 128, 256, 512, 1024, 2048), tol=0.01):
    """Return (rows, converged N) where each row is (N, peak, change relative to the next size)."""
    peaks = [burgers_run(nu, n)[0] for n in sizes]
    rows = [(n, peaks[i], abs(peaks[i + 1] - peaks[i]) / peaks[i + 1]) for i, n in enumerate(sizes[:-1])]
    first = next((r[0] for r in rows if r[2] < tol), None)
    return rows, first


# %% [markdown]
# ## Step 6: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    nu = 0.05
    t, E, Z, W, wend, P = run_ns2d(taylor_green_vorticity(32), nu, 2.0, dt=0.01)
    exact = taylor_green_vorticity(32) * np.exp(-2 * nu * 2.0)
    print(f"Taylor-Green: max |w - exact| at t = 2 is {np.max(np.abs(wend - exact)):.2e}")

    w0 = random_vorticity(64)
    nu2 = 0.01
    t2, E2, Z2, W2, wend2, P2 = run_ns2d(w0, nu2, 3.0)
    print(f"random 2-D run: enstrophy {Z2[0]:.3f} -> {Z2[-1]:.3f}, max enstrophy {Z2.max():.3f}")
    print(f"energy lost {E2[0] - E2[-1]:.5f}, 2 nu * integral of Z = {2 * nu2 * trapezoid(Z2, t2):.5f}")
    print(f"BKM integral of max|w| over [0, 3] = {bkm_integral(t2, W2):.3f} (bound 3 * max|w0| = {3 * W2[0]:.3f})")

    fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
    im = ax[0].imshow(w0.T, origin="lower", extent=[0, 2 * np.pi, 0, 2 * np.pi], cmap="RdBu_r")
    ax[0].set_title("vorticity at t = 0")
    ax[0].set_xlabel("x (radians)")
    ax[0].set_ylabel("y (radians)")
    fig.colorbar(im, ax=ax[0], label="w (1/time)", fraction=0.046)
    im = ax[1].imshow(wend2.T, origin="lower", extent=[0, 2 * np.pi, 0, 2 * np.pi], cmap="RdBu_r")
    ax[1].set_title("vorticity at t = 3, nu = 0.01")
    ax[1].set_xlabel("x (radians)")
    ax[1].set_ylabel("y (radians)")
    fig.colorbar(im, ax=ax[1], label="w (1/time)", fraction=0.046)
    ax[2].plot(t2, Z2 / Z2[0], label="enstrophy Z / Z(0)")
    ax[2].plot(t2, E2 / E2[0], label="energy E / E(0)")
    ax[2].plot(t2, W2 / W2[0], label="max |w| / max |w0|")
    ax[2].set_xlabel("time t (arbitrary units)")
    ax[2].set_ylabel("ratio to initial value")
    ax[2].set_title("2-D: nothing grows")
    ax[2].grid(alpha=0.3)
    ax[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "vorticity_2d.png", dpi=120)

    u3 = taylor_green_3d(16)
    w3, adv3, wSw = stretching_fields(u3)
    print(f"3-D Taylor-Green: w.S.w ranges from {wSw.min():.3f} to {wSw.max():.3f}, mean {wSw.mean():.1e}, "
          f"stretching at {100 * np.mean(wSw > 0):.1f}% of the points")
    _, _, wSw2 = stretching_fields(taylor_green_3d(16, with_z=False))
    print(f"2-D flow extended in z: largest |w.S.w| = {np.max(np.abs(wSw2)):.1e}")

    fig2, (b1, b2) = plt.subplots(1, 2, figsize=(9.5, 3.8))
    n = 16
    im = b1.imshow(wSw[:, :, 0].T, origin="lower", extent=[0, 2 * np.pi, 0, 2 * np.pi], cmap="PiYG")
    b1.set_title("3-D Taylor-Green: w.S.w on the plane z = 0")
    b1.set_xlabel("x (radians)")
    b1.set_ylabel("y (radians)")
    fig2.colorbar(im, ax=b1, label="w.S.w (1/time^3)", fraction=0.046)
    sizes = (16, 32, 64, 128, 256, 512)
    runs = [burgers_run(0.01, s, dealias=False)[0] for s in sizes]
    good = burgers_run(0.01, 1024)[0]
    plot_runs = [min(r, 200.0) for r in runs]
    b2.bar([str(s) for s in sizes], plot_runs, color=["tab:red" if not np.isfinite(r) else "tab:blue" for r in runs])
    b2.axhline(good, color="k", ls="--", label=f"converged ({good:.1f})")
    b2.set_xlabel("grid points N (no dealiasing)")
    b2.set_ylabel("peak |u_x| (1/time); red bar = overflow")
    b2.set_title("Numerical blow-up disappears with resolution")
    b2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "stretching_and_artifact.png", dpi=120)
    print("no-dealiasing peaks:", ["inf" if not np.isfinite(r) else round(r, 2) for r in runs], "converged:", round(good, 2))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then do the
# mini-project and run the checkpoint. The 3-D question itself remains open.
