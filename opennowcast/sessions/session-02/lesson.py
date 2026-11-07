"""Session 2 (Level 2): a radar field as a grid - shift it, estimate the shift, score the forecast.

Educational only. This is NOT a weather warning system: always follow official forecasts.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: translate a field, estimate the motion, score the forecast
# **A. Real-world problem.** A radar picture is a 100 x 100 grid of rain rates. To nowcast, we
# (1) estimate how the whole picture moved between two frames, (2) slide the latest frame
# along that motion, and (3) score the result against what really happened. The motion is
# rarely a whole number of pixels, so we must also shift by fractions of a pixel, and that has a cost.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
N = 100               # grid size (pixels); 1 pixel = 1 km
DT_MIN = 5.0          # minutes between frames
THR = 5.0             # rain-rate threshold (mm/h) used for yes/no scores


# %% [markdown]
# ## Step 1: a synthetic radar field
# A few Gaussian rain cells: each is (cx, cy, sigma, peak) with the centre in pixels, width in
# pixels and centre rain rate in mm/h. The field is the sum of its cells.

# %%
def make_field(cells, n=N):
    y, x = np.mgrid[0:n, 0:n]
    f = np.zeros((n, n))
    for cx, cy, sigma, peak in cells:
        f += peak * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sigma ** 2))
    return f


def moved_cells(cells, u, v, frames):
    """The same cells after `frames` frames, moving (u, v) pixels per frame."""
    return [(cx + u * frames, cy + v * frames, s, p) for cx, cy, s, p in cells]


# %% [markdown]
# ## Step 2: translate a field
# *Integer shift*: copy the array to a new place and fill the gap with zero rain (rain that
# leaves the picture is lost). *Sub-pixel shift*: the new value at pixel x is read at x - dx.
# When x - dx falls between pixels, take a weighted average of the 4 neighbours (bilinear
# interpolation). The weights add up to 1, so rain is not created or destroyed, but the
# averaging blurs the field.

# %%
def shift_int(field, dx, dy):
    """Integer shift: dx pixels east, dy pixels north. Rain pushed off the edge is lost."""
    ny, nx = field.shape
    out = np.zeros_like(field)
    xs, xe = max(0, dx), min(nx, nx + dx)
    ys, ye = max(0, dy), min(ny, ny + dy)
    if xe > xs and ye > ys:
        out[ys:ye, xs:xe] = field[ys - dy:ye - dy, xs - dx:xe - dx]
    return out


def shift_bilinear(field, dx, dy):
    """Shift by any real dx, dy (pixels) using bilinear interpolation; zero rain outside the picture."""
    ny, nx = field.shape
    y, x = np.mgrid[0:ny, 0:nx].astype(float)
    sx, sy = x - dx, y - dy
    x0, y0 = np.floor(sx).astype(int), np.floor(sy).astype(int)
    fx, fy = sx - x0, sy - y0
    pad = np.pad(field, 1)

    def at(yy, xx):
        ok = (yy >= -1) & (yy <= ny) & (xx >= -1) & (xx <= nx)
        return np.where(ok, pad[np.clip(yy + 1, 0, ny + 1), np.clip(xx + 1, 0, nx + 1)], 0.0)

    return ((1 - fx) * (1 - fy) * at(y0, x0) + fx * (1 - fy) * at(y0, x0 + 1)
            + (1 - fx) * fy * at(y0 + 1, x0) + fx * fy * at(y0 + 1, x0 + 1))


def x_variance(field):
    """Spread of the rain along x, in pixels squared (rain-weighted variance of the column index)."""
    x = np.arange(field.shape[1])
    col = field.sum(axis=0)
    m = (col * x).sum() / col.sum()
    return float((col * (x - m) ** 2).sum() / col.sum())


# %% [markdown]
# ## Step 3: estimate the motion between two frames
# Try every whole-pixel shift of the old frame and keep the one whose squared difference from the
# new frame is smallest (brute-force search; it is the same idea as finding the peak of the
# cross-correlation). Then refine to fractions of a pixel by searching a finer grid around it.

# %%
def sse_for_shift(f0, f1, dx, dy):
    return float(((shift_bilinear(f0, dx, dy) - f1) ** 2).sum())


def estimate_shift(f0, f1, max_shift=8, step=0.1):
    """Return (dx, dy) in pixels per frame that best moves f0 onto f1."""
    best = None
    for dy in range(-max_shift, max_shift + 1):
        for dx in range(-max_shift, max_shift + 1):
            e = sse_for_shift(f0, f1, dx, dy)
            if best is None or e < best[0]:
                best = (e, dx, dy)
    _, bx, by = best
    offs = np.arange(-1.0, 1.0 + 1e-9, step)
    best = None
    for oy in offs:
        for ox in offs:
            e = sse_for_shift(f0, f1, bx + ox, by + oy)
            if best is None or e < best[0]:
                best = (e, bx + ox, by + oy)
    return float(best[1]), float(best[2])


def xcorr_peak(f0, f1):
    """Whole-pixel shift (dx, dy) at the peak of the circular cross-correlation (via FFT)."""
    c = np.fft.ifft2(np.conj(np.fft.fft2(f0)) * np.fft.fft2(f1)).real
    iy, ix = np.unravel_index(np.argmax(c), c.shape)
    ny, nx = c.shape
    return int(ix if ix <= nx // 2 else ix - nx), int(iy if iy <= ny // 2 else iy - ny)


# %% [markdown]
# ## Step 4: forecasts and scores
# *Persistence*: say nothing changes. *Advection*: move the latest frame by (shift per frame) x
# (lead in frames). Scores compare forecast f with observation o:
# * RMSE: square root of the mean squared difference (mm/h); 0 is perfect.
# * CSI (critical success index): count pixels at or above a threshold. hits / (hits + misses + false alarms); 1 is perfect.
# * FSS (fractions skill score): compare the *fraction* of rainy pixels in n x n windows. It
#   forgives small position errors; the larger n, the more forgiving.

# %%
def advect_forecast(latest, u, v, lead_frames):
    return shift_bilinear(latest, u * lead_frames, v * lead_frames)


def rmse(f, o):
    return float(np.sqrt(np.mean((f - o) ** 2)))


def csi_counts(hits, misses, false_alarms):
    d = hits + misses + false_alarms
    return float("nan") if d == 0 else hits / d


def csi(f, o, thr=THR):
    a, b = f >= thr, o >= thr
    return csi_counts(int((a & b).sum()), int((~a & b).sum()), int((a & ~b).sum()))


def box_mean(a, n):
    """Mean of a over n x n windows (n odd), zero outside the picture."""
    r = n // 2
    p = np.pad(a.astype(float), r + 1)
    c = p.cumsum(0).cumsum(1)
    ny, nx = a.shape
    s = c[n:n + ny, n:n + nx] - c[0:ny, n:n + nx] - c[n:n + ny, 0:nx] + c[0:ny, 0:nx]
    return s / (n * n)


def fss(f, o, thr=THR, n=1):
    pf, po = box_mean(f >= thr, n), box_mean(o >= thr, n)
    den = (pf ** 2).mean() + (po ** 2).mean()
    return float("nan") if den == 0 else float(1 - ((pf - po) ** 2).mean() / den)


# %% [markdown]
# ## Step 5: a clean model for skill: two discs
# Where the field is above the threshold, a Gaussian cell is a disc of radius
# r = sigma * sqrt(2 ln(peak/threshold)). If the forecast disc is displaced from the true disc by
# d, the CSI is (overlap area) / (union area). This explains why skill falls with lead time:
# the displacement d grows like (wind error) x (lead time).

# %%
def disc_csi(r, d):
    """CSI of two discs of radius r (km) whose centres are d (km) apart."""
    if d >= 2 * r:
        return 0.0
    ov = 2 * r * r * np.arccos(d / (2 * r)) - 0.5 * d * np.sqrt(4 * r * r - d * d)
    return float(ov / (2 * np.pi * r * r - ov))


def edge_radius(sigma, peak, thr=THR):
    return 0.0 if peak <= thr else float(sigma * np.sqrt(2 * np.log(peak / thr)))


# %%
CELLS = [(15, 20, 5.0, 30.0), (25, 55, 7.0, 20.0), (40, 30, 4.0, 40.0)]
TRUE_SHIFT = (2.4, 1.3)        # pixels per frame (east, north)

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f0 = make_field(moved_cells(CELLS, *TRUE_SHIFT, -1))
    f1 = make_field(CELLS)
    obs60 = make_field(moved_cells(CELLS, *TRUE_SHIFT, 12))
    ex, ey = estimate_shift(f0, f1)
    print(f"estimated shift ({ex:.2f}, {ey:.2f}) px/frame, true {TRUE_SHIFT}")
    pers = f1
    adv = advect_forecast(f1, ex, ey, 12)
    print(f"60 min: persistence RMSE {rmse(pers, obs60):.2f} CSI {csi(pers, obs60):.3f} | "
          f"advection RMSE {rmse(adv, obs60):.2f} CSI {csi(adv, obs60):.3f}")
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.2))
    for ax, fld, ttl in zip(axs, (f1, obs60, pers, adv), ("now", "actual at +60 min", "persistence", "advection")):
        ax.imshow(fld, origin="lower", cmap="Blues", vmin=0, vmax=40)
        ax.contour(obs60, levels=[THR], colors="r", linewidths=1)
        ax.set_title(ttl)
        ax.set_xlabel("x (km)")
    axs[0].set_ylabel("y (km)")
    fig.suptitle("Red line: where rain is at least 5 mm/h at +60 min")
    fig.tight_layout()
    fig.savefig(OUT / "forecast_panels.png", dpi=110)

    leads = np.arange(1, 13)
    cp, ca, rp, ra = [], [], [], []
    for k in leads:
        ob = make_field(moved_cells(CELLS, *TRUE_SHIFT, k))
        a = advect_forecast(f1, ex, ey, k)
        cp.append(csi(f1, ob))
        ca.append(csi(a, ob))
        rp.append(rmse(f1, ob))
        ra.append(rmse(a, ob))
    fig2, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    a1.plot(leads * DT_MIN, cp, "o-", label="persistence")
    a1.plot(leads * DT_MIN, ca, "s-", label="advection")
    a1.set_xlabel("lead time (min)")
    a1.set_ylabel("CSI at 5 mm/h")
    a1.legend()
    a1.grid(alpha=0.3)
    a2.plot(leads * DT_MIN, rp, "o-", label="persistence")
    a2.plot(leads * DT_MIN, ra, "s-", label="advection")
    a2.set_xlabel("lead time (min)")
    a2.set_ylabel("RMSE (mm/h)")
    a2.legend()
    a2.grid(alpha=0.3)
    fig2.suptitle("Skill against lead time for a translating field")
    fig2.tight_layout()
    fig2.savefig(OUT / "skill_vs_lead.png", dpi=110)

    one = make_field([(50, 50, 3.0, 30.0)])
    fr = np.linspace(0, 1, 21)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(fr, [shift_bilinear(one, f, 0).max() / one.max() for f in fr])
    ax3.set_xlabel("fractional shift (pixels)")
    ax3.set_ylabel("peak after shift / peak before")
    ax3.set_title("Bilinear interpolation blurs most at half a pixel")
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "interpolation_blur.png", dpi=110)
    print(f"half-pixel shift keeps {shift_bilinear(one, 0.5, 0).max() / one.max():.3f} of the peak")

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
