"""Session 3 (Level 3): local motion, growth and decay, numerical diffusion, uncertainty, failure cases.

Educational only. This is NOT a weather warning system: always follow official forecasts.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: when one shift is not enough
# **A. Real-world problem.** Real rain does not move as one rigid sheet. One storm may move east
# while another, 60 km away, moves north-west; cells grow and fade; and we are never sure of the
# wind. Today you build a nowcast with local motion vectors, measure how its skill falls with
# lead time, see where advection fails, and give a probability instead of a single answer.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
N = 100               # grid size (pixels); 1 pixel = 1 km
DT_MIN = 5.0          # minutes per frame
THR = 10.0            # rain-rate threshold (mm/h) for yes/no scores in this session


# %% [markdown]
# ## Step 1: scenes with known truth
# A scene is a list of cells (cx, cy, sigma, peak, u, v, g): start position (pixels), width (pixels),
# centre rain rate (mm/h), velocity (pixels per frame) and growth rate g per frame. After t frames
# a cell is at (cx + u t, cy + v t) and has peak * (1 + g)^t. Growth g = 0 means pure translation.

# %%
def scene_field(scene, t=0.0, n=N):
    y, x = np.mgrid[0:n, 0:n]
    f = np.zeros((n, n))
    for cx, cy, s, p, u, v, g in scene:
        f += p * (1 + g) ** t * np.exp(-((x - cx - u * t) ** 2 + (y - cy - v * t) ** 2) / (2 * s * s))
    return f


# west cells move east, east cells move north-west: two regions, two motions
TWO_REGION = [(12, 25, 5.0, 30.0, 2.0, 0.5, 0.0), (18, 70, 6.0, 25.0, 2.0, 0.5, 0.0),
              (82, 30, 5.0, 35.0, -1.5, 1.5, 0.0), (78, 75, 6.0, 30.0, -1.5, 1.5, 0.0)]
# the same motions, but cells grow (+8 % per frame) or fade (-10 % per frame)
GROWTH = [(12, 25, 5.0, 22.0, 2.0, 0.5, 0.08), (18, 70, 6.0, 30.0, 2.0, 0.5, -0.10),
          (82, 30, 5.0, 22.0, -1.5, 1.5, 0.08), (78, 75, 6.0, 30.0, -1.5, 1.5, -0.10)]
ONE_REGION = [(12, 25, 5.0, 30.0, 2.0, 0.5, 0.0), (18, 70, 6.0, 25.0, 2.0, 0.5, 0.0)]


def without_growth(scene):
    """The same cells and motions with growth switched off: what pure advection can at best reproduce."""
    return [(cx, cy, s, p, u, v, 0.0) for cx, cy, s, p, u, v, g in scene]


# %% [markdown]
# ## Step 2: sampling a field at any position
# Everything below needs "the value of the field at a non-integer position". We use bilinear
# interpolation (Session 2). Outside the picture the rain is zero.

# %%
def sample(field, sx, sy):
    """Bilinear value of `field` at positions (sx, sy) given as arrays of pixels; zero outside."""
    ny, nx = field.shape
    x0, y0 = np.floor(sx).astype(int), np.floor(sy).astype(int)
    fx, fy = sx - x0, sy - y0
    pad = np.pad(field, 1)

    def at(yy, xx):
        ok = (yy >= -1) & (yy <= ny) & (xx >= -1) & (xx <= nx)
        return np.where(ok, pad[np.clip(yy + 1, 0, ny + 1), np.clip(xx + 1, 0, nx + 1)], 0.0)

    return ((1 - fx) * (1 - fy) * at(y0, x0) + fx * (1 - fy) * at(y0, x0 + 1)
            + (1 - fx) * fy * at(y0 + 1, x0) + fx * fy * at(y0 + 1, x0 + 1))


def shift_field(field, dx, dy):
    y, x = np.mgrid[0:field.shape[0], 0:field.shape[1]].astype(float)
    return sample(field, x - dx, y - dy)


def rmse(f, o):
    return float(np.sqrt(np.mean((f - o) ** 2)))


def csi(f, o, thr=THR):
    a, b = f >= thr, o >= thr
    d = int((a & b).sum() + (~a & b).sum() + (a & ~b).sum())
    return float("nan") if d == 0 else float((a & b).sum() / d)


# %% [markdown]
# ## Step 3: local motion by block matching
# Cut the picture into overlapping blocks. For each block that contains rain, find the shift of
# the old picture that best matches the new one *inside that block only*. Then spread the block
# vectors over every pixel (empty blocks borrow the nearest block that has a vector).

# %%
def match_block(f0, f1, y, x, size, search=6):
    """Best shift (u, v) in pixels/frame for the block f1[y:y+size, x:x+size] (whole pixels, then a parabola fit)."""
    yy, xx = np.mgrid[y:y + size, x:x + size].astype(float)
    tgt = f1[y:y + size, x:x + size]

    def err(du, dv):
        return float(((sample(f0, xx - du, yy - dv) - tgt) ** 2).sum())

    best = min(((err(du, dv), du, dv) for dv in range(-search, search + 1) for du in range(-search, search + 1)))
    _, u, v = best
    u, v = float(u), float(v)
    h = 0.5
    for _ in range(3):
        for axis in (0, 1):
            d = np.array([h, 0.0]) if axis == 0 else np.array([0.0, h])
            em, e0, ep = err(*(np.array([u, v]) - d)), err(u, v), err(*(np.array([u, v]) + d))
            curv = em - 2 * e0 + ep
            if curv > 1e-12:
                step = float(np.clip(h * (em - ep) / (2 * curv), -h, h))
                u, v = (u + step, v) if axis == 0 else (u, v + step)
        h /= 2
    return u, v


def global_motion(f0, f1, search=8):
    """One vector for the whole picture."""
    return match_block(f0, f1, 0, 0, f0.shape[0], search)


def local_vectors(f0, f1, size=32, stride=16, min_rain=THR / 2):
    """Block-centre coordinates and vectors; NaN where a block has no rain."""
    ys = list(range(0, f1.shape[0] - size + 1, stride))
    xs = list(range(0, f1.shape[1] - size + 1, stride))
    U = np.full((len(ys), len(xs)), np.nan)
    V = U.copy()
    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            if f1[y:y + size, x:x + size].max() >= min_rain:
                U[i, j], V[i, j] = match_block(f0, f1, y, x, size)
    return np.array(xs) + (size - 1) / 2.0, np.array(ys) + (size - 1) / 2.0, U, V


def vector_field(xc, yc, U, V, shape=(N, N)):
    """Fill empty blocks with the nearest vector, then interpolate to every pixel. Returns (Upix, Vpix)."""
    U, V = U.copy(), V.copy()
    ok = ~np.isnan(U)
    if not ok.any():                      # no rain anywhere: no motion information, assume still air
        U[:], V[:] = 0.0, 0.0
        ok = np.ones_like(ok)
    idx = np.argwhere(ok)
    for i in range(U.shape[0]):
        for j in range(U.shape[1]):
            if not ok[i, j]:
                k = idx[np.argmin(((idx - [i, j]) ** 2).sum(axis=1))]
                U[i, j], V[i, j] = U[k[0], k[1]], V[k[0], k[1]]

    def up(A):
        rows = np.array([np.interp(np.arange(shape[1]), xc, r) for r in A])
        return np.array([np.interp(np.arange(shape[0]), yc, rows[:, k]) for k in range(shape[1])]).T

    return up(U), up(V)


# %% [markdown]
# ## Step 4: advect with a vector field (semi-Lagrangian)
# For each target pixel, look *backwards* along the motion to where its rain came from, and copy
# the value from there (interpolated). Because the vector should be the one at the *departure*
# point, we repeat the look-back a few times. One look-back covers the whole lead time.

# %%
def advect(field, U, V, frames, iters=3):
    """Single-step semi-Lagrangian advection over `frames` frames. U, V: arrays or scalars (pixels/frame)."""
    ny, nx = field.shape
    y, x = np.mgrid[0:ny, 0:nx].astype(float)
    U = np.broadcast_to(np.asarray(U, dtype=float), field.shape)
    V = np.broadcast_to(np.asarray(V, dtype=float), field.shape)
    dx, dy = frames * U, frames * V
    for _ in range(iters):
        sx, sy = np.clip(x - dx, 0, nx - 1), np.clip(y - dy, 0, ny - 1)
        dx, dy = frames * sample(np.array(U), sx, sy), frames * sample(np.array(V), sx, sy)
    return sample(field, x - dx, y - dy)


def advect_repeated(field, u, v, steps):
    """The same total motion done as `steps` separate one-frame shifts (each one interpolates and blurs)."""
    out = field
    for _ in range(steps):
        out = shift_field(out, u, v)
    return out


def second_moment_x(field):
    x = np.arange(field.shape[1])
    col = field.sum(axis=0)
    m = (col * x).sum() / col.sum()
    return float((col * (x - m) ** 2).sum() / col.sum())


# %% [markdown]
# ## Step 5: skill against lead time
# Observe two frames (t = -1 and 0), estimate motion, forecast 1..12 frames ahead, score against the truth.

# %%
def nowcast_curves(scene, thr=THR, leads=range(1, 13)):
    f0, f1 = scene_field(scene, -1), scene_field(scene, 0)
    gu, gv = global_motion(f0, f1)
    U, V = vector_field(*local_vectors(f0, f1))
    out = {"persistence": [], "global": [], "local": []}
    for k in leads:
        ob = scene_field(scene, k)
        out["persistence"].append(csi(f1, ob, thr))
        out["global"].append(csi(advect(f1, gu, gv, k), ob, thr))
        out["local"].append(csi(advect(f1, U, V, k), ob, thr))
    return out


def first_below(curve, level=0.5, leads=range(1, 13)):
    """First lead time in minutes at which the curve is below `level`, or None if it never is."""
    for k, c in zip(leads, curve):
        if c < level:
            return int(k * DT_MIN)
    return None


# %% [markdown]
# ## Step 6: uncertainty, as a probability
# The wind estimate is uncertain. Make an ensemble: many copies of the wind, each with a small random
# error, advect once per member, and count the fraction of members that put rain >= threshold on a pixel.

# %%
def exceedance_probability(field, u, v, frames, sigma_v, members, rng, thr=THR):
    acc = np.zeros(field.shape)
    for _ in range(members):
        du, dv = rng.normal(0, sigma_v, 2)
        acc += shift_field(field, (u + du) * frames, (v + dv) * frames) >= thr
    return acc / members


def brier(p, o):
    return float(np.mean((p - o) ** 2))


def reliability(p, o, edges=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0001)):
    """Per probability bin: (mean forecast probability, observed frequency, count)."""
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi)
        rows.append((float(p[m].mean()) if m.any() else float("nan"), float(o[m].mean()) if m.any() else float("nan"), int(m.sum())))
    return rows


# %% [markdown]
# ## Step 7: failure cases
# Advection moves rain that exists. It cannot create a new storm, and a straight-line shift cannot
# follow a rotating pattern.

# %%
def rotating_scene_fields(frames, centre=(50.0, 50.0), radius=22.0, deg_per_frame=5.0):
    """Four cells on a ring turning counter-clockwise; returns the field after `frames` frames."""
    f = np.zeros((N, N))
    y, x = np.mgrid[0:N, 0:N]
    for k in range(4):
        a = np.radians(90 * k + deg_per_frame * frames)
        cx, cy = centre[0] + radius * np.cos(a), centre[1] + radius * np.sin(a)
        f += 30.0 * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * 5.0 ** 2))
    return f


NEW_CELL = (55.0, 10.0, 5.0, 35.0)       # a storm that does not exist yet at t = 0


def with_new_storm(field, start_frame, t):
    """Add the new storm, growing linearly from 0 at start_frame to its full peak 3 frames later."""
    amp = float(np.clip((t - start_frame) / 3.0, 0.0, 1.0))
    return field + scene_field([(NEW_CELL[0], NEW_CELL[1], NEW_CELL[2], NEW_CELL[3] * amp, 0.0, 0.0, 0.0)], 0)


# %%
def disc_overlap_csi(r_fc, r_ob, d):
    """CSI of two discs with radii r_fc (forecast) and r_ob (truth) and centres d apart (km)."""
    a1, a2 = np.pi * r_fc ** 2, np.pi * r_ob ** 2
    if a1 == 0 or a2 == 0:
        return 0.0
    if d >= r_fc + r_ob:
        ov = 0.0
    elif d <= abs(r_fc - r_ob):
        ov = min(a1, a2)
    else:
        c1 = (d * d + r_fc ** 2 - r_ob ** 2) / (2 * d * r_fc)
        c2 = (d * d + r_ob ** 2 - r_fc ** 2) / (2 * d * r_ob)
        ov = (r_fc ** 2 * np.arccos(c1) + r_ob ** 2 * np.arccos(c2)
              - 0.5 * np.sqrt((-d + r_fc + r_ob) * (d + r_fc - r_ob) * (d - r_fc + r_ob) * (d + r_fc + r_ob)))
    return float(ov / (a1 + a2 - ov))


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f0, f1 = scene_field(TWO_REGION, -1), scene_field(TWO_REGION, 0)
    gu, gv = global_motion(f0, f1)
    xc, yc, U, V = local_vectors(f0, f1)
    print(f"global vector ({gu:.2f}, {gv:.2f}) px/frame; local vectors from {int((~np.isnan(U)).sum())} blocks with rain")

    fig, ax = plt.subplots(figsize=(5.5, 5.2))
    ax.imshow(f1, origin="lower", cmap="Blues", vmin=0, vmax=40)
    ax.quiver(xc[None, :].repeat(len(yc), 0), yc[:, None].repeat(len(xc), 1), U, V, color="red", angles="xy", scale_units="xy", scale=0.5)
    ax.quiver([50], [50], [gu], [gv], color="black", angles="xy", scale_units="xy", scale=0.5)
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")
    ax.set_title("Local vectors (red) and the one global vector (black)")
    fig.tight_layout()
    fig.savefig(OUT / "motion_vectors.png", dpi=110)

    leads = np.arange(1, 13) * DT_MIN
    cases = {"one region": ONE_REGION, "two regions": TWO_REGION, "two regions + growth/decay": GROWTH}
    fig2, axs = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, (name, sc) in zip(axs, cases.items()):
        cv = nowcast_curves(sc)
        for key, st in (("persistence", "o-"), ("global", "s-"), ("local", "^-")):
            ax.plot(leads, cv[key], st, label=key)
            print(f"{name:28s} {key:11s} CSI at 30 min {cv[key][5]:.2f}, at 60 min {cv[key][11]:.2f}")
        ax.axhline(0.5, color="gray", ls=":")
        ax.set_title(name)
        ax.set_xlabel("lead time (min)")
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("CSI at 10 mm/h")
    axs[0].legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "skill_curves.png", dpi=110)

    cell = scene_field([(20, 50, 2.5, 30.0, 0, 0, 0)])
    rep = advect_repeated(cell, 0.7, 0.0, 12)
    one = shift_field(cell, 8.4, 0.0)
    print(f"peak: start {cell.max():.2f}, 12 small steps {rep.max():.2f}, one 60-min shift {one.max():.2f}")

    rng = np.random.default_rng(1)
    fg = scene_field(ONE_REGION, 0)
    P, Pn, O = [], [], []
    for _ in range(40):
        du, dv = rng.normal(0, 0.35, 2)
        o = shift_field(fg, (2.0 + du) * 12, (0.5 + dv) * 12) >= THR
        P.append(exceedance_probability(fg, 2.0, 0.5, 12, 0.35, 30, rng))
        Pn.append(exceedance_probability(fg, 2.0, 0.5, 12, 0.05, 30, rng))
        O.append(o)
    P, Pn, O = np.array(P), np.array(Pn), np.array(O, dtype=float)
    m = (P > 0) | (Pn > 0) | (O > 0)
    print(f"Brier: calibrated ensemble {brier(P[m], O[m]):.3f}, over-confident {brier(Pn[m], O[m]):.3f}")
    rel = reliability(P[m], O[m])
    fig3, ax3 = plt.subplots(figsize=(4.8, 4.4))
    ax3.plot([0, 1], [0, 1], "k:")
    ax3.plot([r[0] for r in rel], [r[1] for r in rel], "o-", label="calibrated ensemble")
    reln = reliability(Pn[m], O[m])
    ax3.plot([r[0] for r in reln], [r[1] for r in reln], "s-", label="over-confident ensemble")
    ax3.set_xlabel("forecast probability")
    ax3.set_ylabel("observed frequency")
    ax3.legend()
    ax3.grid(alpha=0.3)
    ax3.set_title("Reliability of exceedance probabilities")
    fig3.tight_layout()
    fig3.savefig(OUT / "reliability.png", dpi=110)

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
