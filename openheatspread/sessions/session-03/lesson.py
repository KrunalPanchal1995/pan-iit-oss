"""Session 3 (Level 3): simulate heat spreading on a 2D board and validate the solver.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a 2D heat solver you can trust
# **A. Real-world problem.** A laptop board has a CPU and a GPU that each turn electrical power
# into a small, intense hot spot. Metal sheets spread that heat sideways, and air carries it away.
# Session 2 treated the heat path as a single line. Here the heat spreads in two dimensions and
# changes with time, so there is no simple formula for a whole board. We write a small numerical
# solver (explicit finite differences) and, before trusting it, check it against two cases
# that DO have exact answers: a steady 1D wall and a spreading Gaussian hot spot.
#
# Units in this session: lengths in mm, time in s, temperatures in K (a temperature *rise*
# above room temperature), and thermal diffusivity alpha in mm^2/s.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# aluminium sheet: k = 200 W/(m K), density 2700 kg/m^3, specific heat 900 J/(kg K)
RHO_C_AL = 2700.0 * 900.0                  # volumetric heat capacity, J/(m^3 K)
ALPHA_AL = 200.0 / RHO_C_AL * 1e6          # diffusivity alpha = k / (rho c), converted to mm^2/s


# %% [markdown]
# ## Step 1: the diffusion equation and its explicit update
# Heat conduction in a thin sheet obeys  dT/dt = alpha * (d2T/dx2 + d2T/dy2).
# Cut the sheet into square cells of size dx. The second derivative at a cell is estimated from its
# four neighbours, and the temperature is moved forward by one time step dt:
#
#     T_new = T + r * (T_left + T_right + T_up + T_down - 4 T),     r = alpha * dt / dx^2
#
# Each cell moves a fraction r of the way toward the average of its neighbours. If r is too
# large a cell overshoots and the numbers explode. In 2D the safe limit is  r <= 1/4,
# that is  dt <= dx^2 / (4 alpha).
# Cells at the edge copy themselves as the missing neighbour: no heat crosses the edge (insulated).

# %%
def stable_dt(alpha, dx):
    """Largest stable time step (s) for the explicit 2D scheme."""
    return dx ** 2 / (4.0 * alpha)


def step(T, r):
    """One explicit step on a 2D array T with insulated edges."""
    P = np.pad(T, 1, mode="edge")
    return T + r * (P[:-2, 1:-1] + P[2:, 1:-1] + P[1:-1, :-2] + P[1:-1, 2:] - 4.0 * T)


def evolve(T0, alpha, dx, t_end, r=0.2, fixed=None, source=None, loss=0.0):
    """Advance T0 to time t_end (s). Returns (T, time actually reached).

    fixed  : optional (mask, values); cells where mask is True are held at `values`
    source : optional array, temperature rise per second added to each cell (K/s)
    loss   : optional rate (1/s) at which every cell relaxes to zero rise
    """
    dt = r * dx ** 2 / alpha
    n = int(round(t_end / dt))
    T = T0.copy()
    for _ in range(n):
        T = step(T, r)
        if source is not None:
            T = T + dt * source
        if loss:
            T = T - dt * loss * T
        if fixed is not None:
            T = np.where(fixed[0], fixed[1], T)
    return T, n * dt


# %% [markdown]
# ## Step 2: reference 1, the steady 1D wall
# Hold the left edge at 80 and the right edge at 40, insulate top and bottom, and wait. Session 1
# says the steady profile is a straight line: T(x) = 80 - 40 * x / 20 on a 20 mm wall.
# The solver must find that line by itself.

# %%
def wall_test(nx=21, ny=5, dx=1.0, alpha=20.0, t_end=40.0, t_left=80.0, t_right=40.0):
    mask = np.zeros((ny, nx), dtype=bool)
    mask[:, 0] = mask[:, -1] = True
    vals = np.zeros((ny, nx))
    vals[:, 0], vals[:, -1] = t_left, t_right
    T0 = np.where(mask, vals, 0.5 * (t_left + t_right))
    T, _ = evolve(T0, alpha, dx, t_end, fixed=(mask, vals))
    x = np.arange(nx) * dx
    exact = t_left + (t_right - t_left) * x / ((nx - 1) * dx)
    return x, T[ny // 2], exact


# %% [markdown]
# ## Step 3: reference 2, a Gaussian hot spot that spreads
# Start with a hot spot shaped like a bell, peak rise A and width sigma0. In an unbounded sheet the
# exact solution stays a bell, only wider and lower:
#
#     T(r, t) = A * s0^2 / (s0^2 + 2 alpha t) * exp( - r^2 / (2 (s0^2 + 2 alpha t)) )
#
# The peak falls like 1 / (s0^2 + 2 alpha t). The sheet below is wide enough (80 mm) that the edges
# do not matter in the first second or so.

# %%
SIGMA0 = 3.0      # initial width of the hot spot, mm
AMP = 60.0        # initial peak temperature rise, K


def gaussian_exact(X, Y, t, alpha, sigma0=SIGMA0, amp=AMP):
    s2 = sigma0 ** 2 + 2.0 * alpha * t
    return amp * sigma0 ** 2 / s2 * np.exp(-(X ** 2 + Y ** 2) / (2.0 * s2))


def gaussian_run(dx, alpha=20.0, t=1.0, r=0.2, half=40.0):
    """Run the solver from the exact bell at t = 0. Returns (T, exact at reached time, X, Y)."""
    n = int(round(2 * half / dx)) + 1
    x = (np.arange(n) - n // 2) * dx
    X, Y = np.meshgrid(x, x)
    T, tr = evolve(gaussian_exact(X, Y, 0.0, alpha), alpha, dx, t, r=r)
    return T, gaussian_exact(X, Y, tr, alpha), X, Y


def max_error(dx, **kw):
    T, E, _, _ = gaussian_run(dx, **kw)
    return float(np.abs(T - E).max())


# %% [markdown]
# ## Step 4: what happens past the stability limit
# Seed a tiny checkerboard wiggle (amplitude 0.001 K) on an otherwise cold sheet and take 300 steps.
# A stable scheme damps the wiggle or at least keeps it; an unstable one multiplies it by
# |1 - 8 r| every step, so r = 0.30 grows it by 1.4 times per step.

# %%
def wiggle_growth(r, n_steps=300, n=31):
    checker = 1e-3 * (-1.0) ** (np.add.outer(np.arange(n), np.arange(n)))
    T = checker
    for _ in range(n_steps):
        T = step(T, r)
    return float(np.abs(T).max())


# %% [markdown]
# ## Step 5: a laptop board with two hot spots
# A 100 mm x 60 mm aluminium spreader sheet of thickness d sits behind the board. A CPU (8 mm
# square) and a GPU (8 mm square) heat it. Air flows over both faces with heat transfer
# coefficient h. Per unit volume the cell temperature rise obeys
#
#     dT/dt = alpha * laplacian(T) + P / (rho c V_spot) - (2 h / (rho c d)) * T
#
# The last term is cooling through both faces. At steady state, the power lost to the air must
# equal the power put in. That energy balance is our third check. This is an educational model: no
# heat pipes, no fan curve, no 3D effects and a single face-averaged h.

# %%
def board_run(p_cpu, p_gpu, d_mm, h, dx=2.0, nx=50, ny=30):
    """Steady temperature rise (K) of the board. Returns (T, X, Y, power lost to the air in W)."""
    beta = 2.0 * h / (RHO_C_AL * d_mm * 1e-3)            # 1/s
    xs = (np.arange(nx) + 0.5) * dx
    ys = (np.arange(ny) + 0.5) * dx
    X, Y = np.meshgrid(xs, ys)
    src = np.zeros((ny, nx))
    for cx, cy, power in ((28.0, 30.0, p_cpu), (72.0, 30.0, p_gpu)):
        m = (np.abs(X - cx) < 4.0) & (np.abs(Y - cy) < 4.0)
        volume = m.sum() * (dx * 1e-3) ** 2 * d_mm * 1e-3          # m^3
        src[m] = power / (RHO_C_AL * volume)                        # K/s
    T, _ = evolve(np.zeros((ny, nx)), ALPHA_AL, dx, 8.0 / beta, source=src, loss=beta)
    lost = 2.0 * h * (dx * 1e-3) ** 2 * float(T.sum())
    return T, X, Y, lost


def peak_rise(p_cpu, p_gpu, d_mm, h):
    return float(board_run(p_cpu, p_gpu, d_mm, h)[0].max())


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"aluminium alpha = {ALPHA_AL:.1f} mm^2/s")
    print(f"stable dt for alpha = 20 mm^2/s, dx = 1 mm: {stable_dt(20.0, 1.0):.4f} s")

    # --- validation 1 and 2
    x, num, ex = wall_test()
    print(f"1D wall: largest difference from the straight line = {np.abs(num - ex).max():.2e} K")
    dxs = [4.0, 2.0, 1.0, 0.5]
    errs = [max_error(dx) for dx in dxs]
    for dx, e in zip(dxs, errs):
        print(f"dx = {dx:3.1f} mm   largest error vs exact bell = {e:.4f} K")
    print("error ratio when dx is halved:", [round(errs[i] / errs[i + 1], 2) for i in range(3)])
    T, E, X, Y = gaussian_run(1.0)
    print(f"peak rise after 1 s: solver {T.max():.3f} K, exact {E.max():.3f} K")
    for a in (18.0, 20.0, 22.0):
        Ta, Ea, _, _ = gaussian_run(1.0, alpha=a)
        print(f"alpha = {a:4.1f}: peak rise after 1 s = {Ta.max():.2f} K")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(x, ex, "-", label="exact straight line")
    ax[0].plot(x, num, "o", ms=4, label="solver")
    ax[0].set_xlabel("position across the wall (mm)")
    ax[0].set_ylabel("temperature (C)")
    ax[0].set_title("Steady 1D wall: solver finds the line")
    ax[0].grid(alpha=0.3)
    ax[0].legend()
    ax[1].loglog(dxs, errs, "o-", label="solver error")
    ax[1].loglog(dxs, [errs[0] * (d / dxs[0]) ** 2 for d in dxs], "--", color="gray", label="slope 2")
    ax[1].set_xlabel("cell size dx (mm)")
    ax[1].set_ylabel("largest error (K)")
    ax[1].set_title("Grid convergence: error falls as dx squared")
    ax[1].grid(alpha=0.3, which="both")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "validation.png", dpi=120)

    fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
    ext = [X.min(), X.max(), Y.min(), Y.max()]
    for a_, f, name in ((ax[0], T, "solver"), (ax[1], E, "exact")):
        im = a_.imshow(f, extent=ext, origin="lower", cmap="inferno", vmin=0, vmax=12)
        a_.set_title(f"{name}: temperature rise (K)")
        a_.set_xlabel("x (mm)")
        a_.set_ylabel("y (mm)")
        a_.set_xlim(-30, 30)
        a_.set_ylim(-30, 30)
    fig.colorbar(im, ax=ax[:2], shrink=0.8)
    im2 = ax[2].imshow(T - E, extent=ext, origin="lower", cmap="coolwarm")
    ax[2].set_title("solver minus exact (K)")
    ax[2].set_xlabel("x (mm)")
    ax[2].set_xlim(-30, 30)
    ax[2].set_ylim(-30, 30)
    fig.colorbar(im2, ax=ax[2], shrink=0.8)
    fig.savefig(OUT / "gaussian_spreading.png", dpi=120)

    # --- stability
    rs = [0.10, 0.20, 0.25, 0.26, 0.30]
    growth = [wiggle_growth(r) for r in rs]
    for r, g in zip(rs, growth):
        print(f"r = {r:.2f}: seeded wiggle 0.001 K -> {g:.3g} K after 300 steps")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogy(rs, growth, "o-")
    ax.axvline(0.25, color="red", ls="--", label="limit r = 1/4")
    ax.set_xlabel("r = alpha dt / dx^2 (no unit)")
    ax.set_ylabel("size of seeded wiggle after 300 steps (K)")
    ax.set_title("Stability limit of the explicit scheme")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "stability.png", dpi=120)

    # --- the laptop board
    print("two hot spots, CPU 12 W + GPU 8 W, steady peak rise over room temperature:")
    for d in (0.3, 0.5, 1.0, 2.0):
        row = [peak_rise(12.0, 8.0, d, h) for h in (20.0, 40.0, 80.0)]
        print(f"  d = {d:3.1f} mm   h = 20, 40, 80: " + ", ".join(f"{v:5.1f} K" for v in row))
    Tb, Xb, Yb, lost = board_run(12.0, 8.0, 0.5, 40.0)
    print(f"d = 0.5 mm, h = 40: peak {Tb.max():.1f} K, power lost to air {lost:.2f} W of 20 W in")
    fig, a_ = plt.subplots(figsize=(6.5, 4))
    im = a_.imshow(Tb, extent=[0, 100, 0, 60], origin="lower", cmap="inferno")
    a_.contour(Xb, Yb, Tb, levels=[30, 60], colors="white", linewidths=0.8)
    a_.set_xlabel("x (mm)")
    a_.set_ylabel("y (mm)")
    a_.set_title("Steady rise, CPU 12 W + GPU 8 W, 0.5 mm sheet, h = 40")
    fig.colorbar(im, label="temperature rise (K)")
    fig.tight_layout()
    fig.savefig(OUT / "two_hot_spots.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# Real laptops have fans, heat pipes, 3D stacks and temperature-dependent materials. The solver
# above gets the trends and the order of magnitude right; it is not a design tool.
