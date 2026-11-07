"""Session 2 (Level 2): the 1-D viscous Burgers equation as a toy.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: Burgers, a toy that shows the key mechanism
# **A. Real-world problem.** Traffic on a road, a breaking wave on a beach and a sonic boom all
# show the same thing: a smooth profile steepens into an almost-jump. The 1-D Burgers equation
# is the simplest equation with that behaviour:
#
#     u_t + u u_x = nu u_xx        (u = speed, nu = viscosity, x on a periodic box of length 2 pi)
#
# **HONESTY NOTE.** Burgers is NOT Navier-Stokes. It is a toy. For Burgers we CAN prove that
# solutions stay smooth for every nu > 0, and we can even write the exact solution. The real
# 3-D Navier-Stokes smoothness question is open. Burgers is useful because it shows the two
# competing effects (steepening versus smoothing) that make the real problem hard.
#
# **Plan.** (1) the inviscid shock time, (2) an exact viscous solution (Cole-Hopf),
# (3) a pseudo-spectral solver checked against it, (4) the energy equation, (5) how the peak
# gradient grows as nu shrinks, (6) how many Fourier modes are needed.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: no viscosity (nu = 0): a shock forms at t* = 1 / max(-u0')
# Without viscosity each point keeps its speed, so the profile at time t is found by sliding
# every point sideways by u0 * t. A point at x moves with speed u0(x); where u0 decreases with
# x, points ahead are slower and the profile steepens. The slope along a moving point is
#
#     u_x = u0' / (1 + t u0')       which becomes infinite when 1 + t u0' = 0.
#
# The first time this happens is t* = 1 / max(-u0'(x)). For u0 = sin x, u0' = cos x, the most
# negative slope is -1 (at x = pi), so t* = 1.

# %%
def shock_time(u0_prime):
    """t* = 1 / max(-u0') from samples of the initial slope (needs some negative slope)."""
    m = float(np.max(-np.asarray(u0_prime)))
    return float("inf") if m <= 0 else 1.0 / m


def characteristic_profile(x, t, iters=60):
    """Inviscid solution with u0 = sin x, valid for t < 1 (Newton on x = X + t sin X)."""
    X = np.array(x, dtype=float)
    for _ in range(iters):
        X = X - (X + t * np.sin(X) - x) / (1.0 + t * np.cos(X))
    return np.sin(X)


def inviscid_slope_at_pi(t):
    """Exact slope u_x at x = pi: u0' = -1 there, so u_x = -1 / (1 - t)."""
    return -1.0 / (1.0 - t)


# %% [markdown]
# ## Step 2: with viscosity the solution is exact and smooth (Cole-Hopf)
# The substitution u = -2 nu (d/dx) ln(phi) turns Burgers into the heat equation
# phi_t = nu phi_xx, which is solved mode by mode. For u0 = sin x we have
# phi(x, 0) = exp(cos(x) / (2 nu)), and writing phi = sum_n c_n exp(-n^2 nu t) cos(n x) gives
#
#     u(x, t) = 2 nu * sum_n n c_n exp(-n^2 nu t) sin(n x) / sum_n c_n exp(-n^2 nu t) cos(n x).
#
# The denominator is a positive function (a heat-smoothed positive function stays positive), so
# u is smooth for all t and every nu > 0. Warning: for small nu the numbers inside are
# astronomically small at x = pi (about exp(-1/nu)) and cancel each other, so double precision
# fails: at nu = 0.02 this function already returns wrong values. Stay with nu >= 0.04.

# %%
def cole_hopf(x, t, nu, nmax=128, m=2048):
    """Exact viscous Burgers solution for u0 = sin x (use nu >= 0.04 in double precision)."""
    xs = 2 * np.pi * np.arange(m) / m
    phi0 = np.exp((np.cos(xs) - 1.0) / (2.0 * nu))     # constant factor cancels in u
    n = np.arange(nmax + 1)
    c = np.array([np.mean(phi0 * np.cos(k * xs)) for k in n])
    c[1:] *= 2.0
    d = c * np.exp(-(n ** 2) * nu * t)
    x = np.asarray(x, dtype=float)[..., None]
    return 2.0 * nu * np.sum(n * d * np.sin(n * x), axis=-1) / np.sum(d * np.cos(n * x), axis=-1)



def cole_hopf_slope_at_pi(t, nu, nmax=64, m=256):
    """Exact slope u_x at the shock centre x = pi (where sin(n x) = 0 and cos(n pi) = (-1)^n)."""
    xs = 2 * np.pi * np.arange(m) / m
    phi0 = np.exp((np.cos(xs) - 1.0) / (2.0 * nu))
    n = np.arange(nmax + 1)
    c = np.array([np.mean(phi0 * np.cos(k * xs)) for k in n])
    c[1:] *= 2.0
    d = c * np.exp(-(n ** 2) * nu * t) * (-1.0) ** n
    return 2.0 * nu * float(np.sum(n ** 2 * d) / np.sum(d))


# %% [markdown]
# ## Step 3: a pseudo-spectral solver
# We store u on N equally spaced points and work with its Fourier coefficients: the derivative
# d/dx becomes multiplication by i k. The product u*u is formed on the grid (that is the
# "pseudo" part), and the highest third of the wavenumbers is removed ("2/3 dealiasing") to
# stop products from folding energy back onto low modes. The viscous term is handled exactly
# by an integrating factor exp(-nu k^2 dt), and the rest by classical RK4.

# %%
def solve_burgers(nu, n, t_end, dt=0.004, dealias=True, u0=None):
    """Pseudo-spectral viscous Burgers on [0, 2 pi) with u0 = sin x unless u0 (array) is given.

    Returns a dict with the final field `u`, grid `x`, time list `t`, and time histories
    `peak` (max |u_x|), `energy` (mean of u^2 / 2) and `diss` (nu * mean of u_x^2).
    If the run overflows, the histories end with inf and `finite` is False.
    """
    x = 2 * np.pi * np.arange(n) / n
    k = np.fft.fftfreq(n, 1.0 / n)
    mask = (np.abs(k) < n / 3.0) if dealias else np.ones(n, dtype=bool)
    uh = np.fft.fft(np.sin(x) if u0 is None else u0)
    half = np.exp(-nu * k ** 2 * dt / 2.0)

    def nonlinear(vh):
        u = np.fft.ifft(vh).real
        return -0.5j * k * np.fft.fft(u * u) * mask

    def measures(vh):
        u = np.fft.ifft(vh).real
        ux = np.fft.ifft(1j * k * vh).real
        return float(np.max(np.abs(ux))), 0.5 * float(np.mean(u * u)), nu * float(np.mean(ux * ux))

    ts = [0.0]
    pk, en, ds = [[v] for v in measures(uh)]
    finite = True
    with np.errstate(all="ignore"):
        for i in range(int(round(t_end / dt))):
            a = nonlinear(uh)
            b = nonlinear(half * (uh + 0.5 * dt * a))
            c = nonlinear(half * uh + 0.5 * dt * b)
            d = nonlinear(half * half * uh + dt * half * c)
            uh = half * half * uh + dt / 6.0 * (half * half * a + 2 * half * (b + c) + d)
            ts.append((i + 1) * dt)
            if not np.all(np.isfinite(uh)) or np.max(np.abs(uh)) > 1e8:
                for h in (pk, en, ds):
                    h.append(float("inf"))
                finite = False
                break
            for h, v in zip((pk, en, ds), measures(uh)):
                h.append(v)
    return {"x": x, "u": np.fft.ifft(uh).real, "t": np.array(ts), "peak": np.array(pk),
            "energy": np.array(en), "diss": np.array(ds), "finite": finite}


def trapezoid(y, t):
    y, t = np.asarray(y), np.asarray(t)
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(t)))


# %% [markdown]
# ## Step 4: the energy equation
# Multiply Burgers by u and average over the box. The transport term integrates to zero
# (it only moves energy around), leaving  dE/dt = -nu * mean(u_x^2)  with
# E = mean(u^2)/2. So energy only ever decreases, and it is lost where gradients are large.
# Integrating in time: E(0) - E(T) = integral of the dissipation.
#
# ## Step 5: peak gradient versus nu
# The profile near the shock has width of order nu and a jump of about 2 in u, so the largest
# slope is of order 1/nu. We measure it: peak gradient P(nu) = max over time of max |u_x|.

# %%
def peak_gradient(nu, n, t_end=3.0, dt=0.004):
    return float(solve_burgers(nu, n, t_end, dt)["peak"].max())


# %% [markdown]
# ## Step 6: how many modes are needed?
# If the grid spacing 2 pi / N is much larger than the shock width the solver cannot see the
# shock. We find by experiment the smallest power-of-two N whose peak gradient is within a
# tolerance of a very fine reference (N = 2048).

# %%
def convergence_table(nu, sizes=(16, 32, 64, 128, 256, 512, 1024), n_ref=2048):
    """List of (N, peak gradient, relative error against the N = n_ref run)."""
    ref = peak_gradient(nu, n_ref, dt=0.002)
    peaks = [peak_gradient(nu, n) for n in sizes]
    return [(n, pk, abs(pk - ref) / ref) for n, pk in zip(sizes, peaks)], ref


def smallest_resolved(nu, tol=0.01, **kw):
    table, _ = convergence_table(nu, **kw)
    for n, _, err in table:
        if err < tol:
            return n
    return None


# %% [markdown]
# ## Step 7: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    x = np.linspace(0, 2 * np.pi, 600)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.8))
    for t in (0.0, 0.5, 0.9, 0.99):
        a1.plot(x, characteristic_profile(x, t), label=f"inviscid t = {t}")
    a1.set_xlabel("position x (radians)")
    a1.set_ylabel("speed u (arbitrary units)")
    a1.set_title("nu = 0: the slope at x = pi tends to -infinity at t = 1")
    a1.grid(alpha=0.3)
    a1.legend(fontsize=7)
    for nu, col in ((0.1, "tab:blue"), (0.04, "tab:orange")):
        r = solve_burgers(nu, 256, 1.5)
        a2.plot(r["x"], r["u"], color=col, label=f"viscous nu = {nu}, t = 1.5")
        a2.plot(x, cole_hopf(x, 1.5, nu), "k:", lw=1)
    a2.set_xlabel("position x (radians)")
    a2.set_ylabel("speed u (arbitrary units)")
    a2.set_title("nu > 0: smooth, matches exact (dotted)")
    a2.grid(alpha=0.3)
    a2.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "burgers_profiles.png", dpi=120)

    nus = [0.08, 0.04, 0.02, 0.01]
    peaks = [peak_gradient(v, 1024) for v in nus]
    for v, pkv in zip(nus, peaks):
        print(f"nu = {v}: peak |u_x| = {pkv:.2f}, nu * peak = {v * pkv:.3f}")
    fig2, (b1, b2) = plt.subplots(1, 2, figsize=(9.5, 3.8))
    b1.loglog(nus, peaks, "o-", label="measured peak |u_x|")
    b1.loglog(nus, [0.5 / v for v in nus], "k--", label="0.5 / nu")
    b1.set_xlabel("viscosity nu (arbitrary units)")
    b1.set_ylabel("peak |u_x| (1 / time)")
    b1.set_title("The peak gradient grows like 1 / nu")
    b1.grid(alpha=0.3, which="both")
    b1.legend()
    for v in (0.04, 0.02, 0.01):
        table, _ = convergence_table(v)
        b2.loglog([r[0] for r in table], [max(r[2], 1e-7) for r in table], "o-", label=f"nu = {v}")
        first = next(r[0] for r in table if r[2] < 0.01)
        print(f"nu = {v}: smallest N with error < 1% is {first}")
    b2.axhline(0.01, color="gray", ls=":")
    b2.set_xlabel("number of grid points N")
    b2.set_ylabel("relative error of peak gradient")
    b2.set_title("Resolution needed grows as nu shrinks")
    b2.grid(alpha=0.3, which="both")
    b2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "peak_gradient_scaling.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Burgers always stays smooth when nu > 0; whether 3-D Navier-Stokes does is open.
