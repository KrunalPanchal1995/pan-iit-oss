"""Session 2 (Level 2): the forward Abel transform of a radial profile, by integration and by rings.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: from a radial recipe to a photo (the forward Abel transform)
# **A. Real-world problem.** A flame is not a uniform ball: it glows strongly in some rings
# and weakly in others. We describe it by an emission profile eps(r), the light made per mm of
# path at distance r from the axis. The camera records I(y), the sum along each line of sight
# at offset y. Going from eps(r) to I(y) is the *forward Abel transform*. Today you compute it
# two ways (numerical integration, and a stack of rings) and then answer a design question:
# how many pixels across the flame do we need?

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_MM = 4.0      # outer radius of the region we model (mm); the flame is inside it


# %% [markdown]
# ## Step 1: two radial profiles
# * Gaussian: eps(r) = exp(-(r/a)^2), a bright core of width a (mm).
# * Ring: eps(r) = exp(-((r - r0)/w)^2), a hollow flame with the glow on a ring of radius r0.

# %%
def gauss_eps(r, a):
    return np.exp(-(np.asarray(r, dtype=float) / a) ** 2)


def ring_eps(r, r0, w):
    return np.exp(-((np.asarray(r, dtype=float) - r0) / w) ** 2)


# %% [markdown]
# ## Step 2: the forward Abel transform by integration
# A line of sight at offset y meets the axis-distance r = sqrt(y^2 + u^2) after walking a
# distance u from its closest point. Adding up both directions:
#
#     I(y) = 2 * integral from u = 0 to sqrt(R^2 - y^2) of  eps( sqrt(y^2 + u^2) ) du
#
# This is the same thing as the textbook form 2 * integral of eps(r) r dr / sqrt(r^2 - y^2),
# but written with u it has no division by zero, so the trapezoid rule works directly.
# Exact pair to test against (Gaussian goes to Gaussian, for a wide enough region):
#
#     eps = exp(-r^2/a^2)   gives   I(y) = sqrt(pi) * a * exp(-y^2/a^2)

# %%
def abel_forward(eps_fn, y, R=R_MM, n=2000):
    """Brightness I(y) (a.u.) for offsets y (mm, array or number); trapezoid rule in u with n steps."""
    y = np.atleast_1d(np.asarray(y, dtype=float))
    out = np.zeros_like(y)
    for k, yk in enumerate(np.abs(y)):
        if yk >= R:
            continue
        u = np.linspace(0.0, np.sqrt(R * R - yk * yk), n + 1)
        f = eps_fn(np.sqrt(yk * yk + u * u))
        out[k] = 2.0 * np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(u))
    return out


def gauss_abel_exact(y, a):
    return np.sqrt(np.pi) * a * np.exp(-(np.asarray(y, dtype=float) / a) ** 2)


# %% [markdown]
# ## Step 3: the forward transform with rings (the matrix W)
# A camera has pixels, so we cut the region into N rings of width dr = R/N: ring j spans
# r_j = j*dr to r_(j+1). We assume eps is constant in each ring (its value at the ring's middle).
# The line of sight at y_i = i*dr crosses ring j (for j >= i) along a path of length
#
#     W_ij = 2 * ( sqrt(r_(j+1)^2 - y_i^2) - sqrt(r_j^2 - y_i^2) )     (the second root is 0 if r_j < y_i)
#
# so  I_i = sum over j of W_ij * eps_j,  a matrix times a vector. W is zero below the diagonal.

# %%
def ring_matrix(N, R=R_MM):
    dr = R / N
    edges = dr * np.arange(N + 1)
    y = edges[:N]
    inner = np.sqrt(np.clip(edges[None, :-1] ** 2 - y[:, None] ** 2, 0.0, None))
    outer = np.sqrt(np.clip(edges[None, 1:] ** 2 - y[:, None] ** 2, 0.0, None))
    return 2.0 * (outer - inner)


def ring_forward(eps_fn, N, R=R_MM):
    """Offsets y_i (mm) and brightness I_i (a.u.) from the ring model, eps sampled at ring middles."""
    dr = R / N
    mid = dr * (np.arange(N) + 0.5)
    return dr * np.arange(N), ring_matrix(N, R) @ eps_fn(mid)


# %% [markdown]
# ## Step 4: design question, how many rings (pixels)?
# The ring model is only an approximation of the smooth integral. Its error, measured as the
# largest difference from the exact Gaussian transform divided by the peak brightness,
# falls as N grows. A flame image needs about 2N pixels across the region (both sides).

# %%
def ring_error(a, N, R=R_MM):
    """Largest |ring model - exact| as a fraction of the peak brightness, for a Gaussian of width a (mm)."""
    y, model = ring_forward(lambda r: gauss_eps(r, a), N, R)
    exact = gauss_abel_exact(y, a)
    return float(np.max(np.abs(model - exact)) / exact.max())


def smallest_rings(a, tol=0.01, R=R_MM, n_max=200):
    """Smallest number of rings whose error is below tol (fraction of the peak)."""
    for N in range(2, n_max + 1):
        if ring_error(a, N, R) < tol:
            return N
    return None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    y0 = 1.0
    print(f"worked example: Gaussian a=1 mm at y=1 mm: exact {gauss_abel_exact(y0, 1.0)[()]:.4f}, "
          f"integration {abel_forward(lambda r: gauss_eps(r, 1.0), y0)[0]:.4f}")
    for a in (0.5, 0.7, 1.0):
        print(f"a = {a} mm: rings needed for error < 1% of peak: {smallest_rings(a)}")
    for N in (5, 10, 20, 40):
        print(f"a = 1 mm, N = {N:2d} rings (dr = {R_MM / N:.2f} mm): error {100 * ring_error(1.0, N):.3f} % of peak")

    y = np.linspace(0, R_MM, 321)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ax = axes[0]
    r = np.linspace(0, R_MM, 321)
    ax.plot(r, gauss_eps(r, 1.0), label="Gaussian, a = 1 mm")
    ax.plot(r, ring_eps(r, 1.5, 0.4), label="ring, r0 = 1.5 mm, w = 0.4 mm")
    ax.set_xlabel("distance from the axis r (mm)")
    ax.set_ylabel("emission eps (a.u. per mm)")
    ax.set_title("Two emission profiles")
    ax.grid(alpha=0.3)
    ax.legend()
    ax = axes[1]
    ax.plot(y, gauss_abel_exact(y, 1.0), "k", lw=2, label="Gaussian: exact sqrt(pi) a exp(-y^2/a^2)")
    ax.plot(y, abel_forward(lambda q: gauss_eps(q, 1.0), y, n=500), "--", color="tab:orange", label="Gaussian: integration")
    ax.plot(y, abel_forward(lambda q: ring_eps(q, 1.5, 0.4), y, n=500), color="tab:green", label="ring: integration")
    yr, ir = ring_forward(lambda q: gauss_eps(q, 1.0), 10)
    ax.plot(yr, ir, "o", ms=5, color="tab:red", label="Gaussian: 10 rings")
    ax.set_xlabel("offset of the line of sight y (mm)")
    ax.set_ylabel("brightness I (a.u.)")
    ax.set_title("What the camera records")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "forward_profiles.png", dpi=110)

    Ns = np.arange(3, 61)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for a in (0.5, 0.7, 1.0):
        ax2.semilogy(Ns, [100 * ring_error(a, int(N)) for N in Ns], label=f"a = {a} mm")
    ax2.axhline(1.0, color="red", ls="--", label="1% limit")
    ax2.set_xlabel("number of rings N (pixels across the half-width)")
    ax2.set_ylabel("ring-model error (% of peak)")
    ax2.set_title("Design: more pixels, smaller error")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "rings_error.png", dpi=110)

# %% [markdown]
# ## Try it
# Change `a` or the ring radius and predict the number of rings you need. Then run the
# checkpoint. Next session runs the machine backwards: from the photo to the flame.
