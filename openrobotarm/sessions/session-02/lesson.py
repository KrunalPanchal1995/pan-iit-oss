"""Session 2 (Level 2): the workspace of a 3-link arm, joint limits and redundancy.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: where can the gripper go? Workspace, joint limits and redundancy
# **A. Real-world problem.** Before you buy or build a pick-and-place arm you must ask: can
# it reach every spot on my work table? Which spots does it lose when the motors can only turn
# a limited angle? And a 3-link arm has one more joint than a point in the plane needs: what
# does that extra freedom do?
#
# **Plan.** (1) forward kinematics with cumulative angles (equations), (2) the reachable
# region by sampling a grid, (3) joint limits, (4) the family of solutions, (5) design.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
LINKS = np.array([0.30, 0.25, 0.15])      # metres


# %% [markdown]
# ## Step 1: forward kinematics for n links
# With cumulative angles c_k = q_1 + ... + q_k the gripper is
#     x = sum_k L_k cos(c_k),     y = sum_k L_k sin(c_k)

# %%
def fk(q, links=LINKS):
    """Gripper position (x, y) in metres for joint angles q in radians."""
    c = np.cumsum(np.asarray(q, dtype=float))
    links = np.asarray(links)
    return np.array([np.sum(links * np.cos(c)), np.sum(links * np.sin(c))])


def chain(q, links=LINKS):
    """Base, elbow, wrist, gripper points (4 x 2) for plotting."""
    c = np.cumsum(np.asarray(q, dtype=float))
    steps = np.asarray(links)[:, None] * np.stack([np.cos(c), np.sin(c)], axis=1)
    return np.vstack([[0.0, 0.0], np.cumsum(steps, axis=0)])


def wrap(a):
    """Wrap an angle (or array) into (-pi, pi]."""
    return np.pi - np.mod(np.pi - np.asarray(a, dtype=float), 2 * np.pi)


# %% [markdown]
# ## Step 2: the workspace of two links is a ring
# With links L1 and L2 the distance from the base ranges from |L1 - L2| to L1 + L2, so the
# reachable region is an annulus (ring) of area pi ((L1+L2)^2 - (L1-L2)^2) = 4 pi L1 L2.
# We can measure an area by sampling: lay a fine grid, count cells that are reachable, and
# multiply by the area of one cell.

# %%
def annulus_area(r_out, r_in=0.0):
    return float(np.pi * (r_out ** 2 - r_in ** 2))


def two_link_area_grid(l1, l2, cell=0.005):
    n = int(np.ceil(2 * (l1 + l2) / cell))
    xs = -(l1 + l2) + (np.arange(n) + 0.5) * cell
    gx, gy = np.meshgrid(xs, xs)
    r = np.hypot(gx, gy)
    return float(np.count_nonzero((r >= abs(l1 - l2)) & (r <= l1 + l2)) * cell * cell)


# %% [markdown]
# ## Step 3: a third link with the tool pointing in a chosen direction phi
# If the gripper must point along phi, the wrist (end of link 2) must sit at
# target - L3 (cos phi, sin phi); then the two-link ring rule applies to the wrist. For each
# phi and each of the two elbow choices, two angles q1, q2 follow, and q3 = phi - q1 - q2.
# Trying many phi values answers "can the gripper reach this point with ANY tool direction?".
# Joint limits |q_i| <= limit throw out some of these solutions.

# %%
def solutions_for_tool(target, phi, links=LINKS):
    """Both joint-angle solutions (q1, q2, q3) in radians that put the gripper on target pointing along phi."""
    l1, l2, l3 = links
    w = np.asarray(target, dtype=float) - l3 * np.array([np.cos(phi), np.sin(phi)])
    d2 = float(w @ w)
    cb = (d2 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2)
    if abs(cb) > 1 + 1e-12:
        return []
    b = float(np.arccos(np.clip(cb, -1, 1)))
    out = []
    for q2 in ([b] if abs(np.sin(b)) < 1e-5 else [b, -b]):  # fully stretched or folded: one solution
        q1 = np.arctan2(w[1], w[0]) - np.arctan2(l2 * np.sin(q2), l1 + l2 * np.cos(q2))
        q1 = float(wrap(q1))
        out.append((q1, float(q2), float(wrap(phi - q1 - q2))))
    return out


def reachable_mask(x, y, limit=np.pi, links=LINKS, dphi=np.radians(5)):
    """Boolean array: which points (x, y) can be reached with every |q_i| <= limit for SOME tool direction
    and elbow choice. Same maths as solutions_for_tool, done for all points and directions at once."""
    l1, l2, l3 = links
    x = np.asarray(x, dtype=float)[..., None]
    y = np.asarray(y, dtype=float)[..., None]
    phi = -np.pi + dphi * np.arange(int(round(2 * np.pi / dphi)))
    wx, wy = x - l3 * np.cos(phi), y - l3 * np.sin(phi)
    cb = (wx ** 2 + wy ** 2 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2)
    ok_ring = np.abs(cb) <= 1 + 1e-12
    b = np.arccos(np.clip(cb, -1, 1))
    good = np.zeros(np.broadcast(wx, phi).shape, dtype=bool)
    for q2 in (b, -b):
        q1 = wrap(np.arctan2(wy, wx) - np.arctan2(l2 * np.sin(q2), l1 + l2 * np.cos(q2)))
        q3 = wrap(phi - q1 - q2)
        good |= ok_ring & (np.abs(q1) <= limit + 1e-12) & (np.abs(q2) <= limit + 1e-12) & (np.abs(q3) <= limit + 1e-12)
    return good.any(axis=-1)


def reachable(target, limit=np.pi, links=LINKS, dphi=np.radians(5)):
    """True if some tool direction and elbow choice reaches target with every |q_i| <= limit."""
    return bool(reachable_mask(target[0], target[1], limit, links, dphi))


def reachable_fraction(limit_deg, links=LINKS, cell=0.02, dphi_deg=5):
    """Fraction of the full disk (radius = sum of links) that is reachable with |q_i| <= limit_deg."""
    r_max = float(np.sum(links))
    xs = -r_max + (np.arange(int(np.ceil(2 * r_max / cell))) + 0.5) * cell
    gx, gy = np.meshgrid(xs, xs)
    inside = np.hypot(gx, gy) <= r_max
    ok = reachable_mask(gx[inside], gy[inside], np.radians(limit_deg), links, np.radians(dphi_deg))
    return float(np.count_nonzero(ok) / np.count_nonzero(inside))


# %% [markdown]
# ## Step 4: redundancy, a whole family of solutions
# A point in the plane needs 2 numbers; three joints give 3. The spare one is the tool
# direction phi: every phi in the reachable range gives a different pair of arm shapes for
# the SAME gripper position.

# %%
def solution_family(target, links=LINKS, n=72, limit=np.pi):
    """List of (phi, q1, q2, q3) for the same target over n tool directions."""
    fam = []
    for phi in np.linspace(-np.pi, np.pi, n, endpoint=False):
        for q in solutions_for_tool(target, phi, links):
            if max(abs(v) for v in q) <= limit + 1e-12:
                fam.append((float(phi),) + q)
    return fam


# %% [markdown]
# ## Step 5: a design question
# The base sits 0.20 m in front of the short side of a 0.5 m x 0.3 m table, centred on it.
# Which total arm length reaches every table point? The farthest points are the far corners.

# %%
def table_points(step=0.025, near=0.20, length=0.5, width=0.3):
    xs = np.arange(near, near + length + 1e-9, step)
    ys = np.arange(-width / 2, width / 2 + 1e-9, step)
    return [(float(x), float(y)) for x in xs for y in ys]


def table_coverage(links, limit_deg=180, step=0.025):
    pts = table_points(step)
    return sum(reachable(p, np.radians(limit_deg), links) for p in pts) / len(pts)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("two-link annulus area, formula:", round(annulus_area(0.55, 0.05), 4),
          " grid:", round(two_link_area_grid(0.30, 0.25), 4))
    for lim in (180, 120, 90):
        print(f"limit +-{lim}: reachable fraction {reachable_fraction(lim):.3f}")
    r_max = float(np.sum(LINKS))
    cell = 0.02
    xs = -r_max + (np.arange(int(np.ceil(2 * r_max / cell))) + 0.5) * cell
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.7), sharey=True)
    for ax, lim in zip(axs, (180, 120, 60)):
        gx, gy = np.meshgrid(xs, xs)
        m = reachable_mask(gx, gy, np.radians(lim))
        ax.plot(gx[m], gy[m], "s", ms=2, color="tab:blue")
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.set_title(f"joint limit +-{lim} deg")
        ax.set_xlabel("x (m)")
    axs[0].set_ylabel("y (m)")
    fig.tight_layout()
    fig.savefig(OUT / "workspace_limits.png", dpi=110)

    fam = solution_family((0.45, 0.20))
    fig2, ax2 = plt.subplots(figsize=(5.8, 5.2))
    for k in range(0, len(fam), 4):
        _, a, b, c = fam[k]
        pp = chain((a, b, c))
        ax2.plot(pp[:, 0], pp[:, 1], "-", lw=1.5, alpha=0.7)
    ax2.plot(0.45, 0.20, "rs")
    ax2.set_aspect("equal")
    ax2.grid(alpha=0.3)
    ax2.set_xlabel("x (m)")
    ax2.set_ylabel("y (m)")
    ax2.set_title(f"{len(fam)} arm shapes, one gripper position (0.45, 0.20) m")
    fig2.tight_layout()
    fig2.savefig(OUT / "redundancy_family.png", dpi=120)
    for links in ([0.30, 0.25, 0.15], [0.30, 0.25, 0.17], [0.30, 0.25, 0.18]):
        print(links, "table coverage:", table_coverage(links), " with +-120:", table_coverage(links, 120))

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
