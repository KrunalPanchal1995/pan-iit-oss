"""Session 2 (Level 2): bones rotate about joints and the joints chain.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: bones rotate about joints, and joints chain
# **A. Real-world problem.** When you wave, your hand travels because the forearm rides on
# the elbow, which rides on the shoulder. A character rig is exactly that chain. Today you
# build a two-bone arm in metres and answer: where is the hand, and can it reach a target?

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
L1, L2 = 0.30, 0.25          # upper arm and forearm lengths in metres


# %% [markdown]
# ## Step 1: rotate about a joint, not about the origin
# Session 1 turned points about (0, 0). A joint is somewhere else. To turn about a pivot `c`:
# move the pivot to the origin, turn, move back:  new = R (x - c) + c.

# %%
def rot(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])


def rotate_about(points, theta, pivot):
    pivot = np.asarray(pivot, dtype=float)
    return (np.asarray(points, dtype=float) - pivot) @ rot(theta).T + pivot


# %% [markdown]
# ## Step 2: chain two bones
# The upper arm points at angle `a` from the shoulder. The forearm points at `a + b`, because
# the elbow angle `b` is measured *relative to* the upper arm. Angles add down the chain:
#
#     elbow = L1 (cos a, sin a)
#     hand  = elbow + L2 (cos(a+b), sin(a+b))

# %%
def arm_joints(a, b, l1=L1, l2=L2):
    """Shoulder, elbow, hand as three (x, y) points in metres. Angles in radians."""
    shoulder = np.array([0.0, 0.0])
    elbow = l1 * np.array([np.cos(a), np.sin(a)])
    hand = elbow + l2 * np.array([np.cos(a + b), np.sin(a + b)])
    return np.array([shoulder, elbow, hand])


# %% [markdown]
# ## Step 3: how far can the hand reach?
# The distance from the shoulder to the hand depends only on the elbow angle (law of cosines):
#     |hand|^2 = L1^2 + L2^2 + 2 L1 L2 cos b
# Straight arm (b = 0) is the longest reach L1 + L2; folded back (b = 180 degrees) is the
# shortest, |L1 - L2|.

# %%
def reach(b, l1=L1, l2=L2):
    return np.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * np.cos(b))


# %% [markdown]
# ## Step 4: run it backwards (design)
# Given a target, which angles put the hand there? From the reach formula get `b`, then `a`.
# There are two answers: "elbow up" and "elbow down".

# %%
def solve_reach(x, y, l1=L1, l2=L2):
    """Return the two (a, b) solutions in radians, or [] if the target cannot be reached."""
    d2 = x * x + y * y
    cb = (d2 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2)
    if abs(cb) > 1 + 1e-9:            # small tolerance so exact boundary targets are accepted
        return []
    b0 = float(np.arccos(min(1.0, max(-1.0, cb))))
    bs = [b0] if abs(np.sin(b0)) < 1e-9 else [b0, -b0]   # fully stretched or folded: only one solution
    return [(float(np.arctan2(y, x) - np.arctan2(l2 * np.sin(b), l1 + l2 * np.cos(b))), b) for b in bs]


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    for a_d, b_d in [(0, 0), (40, 50), (90, -90)]:
        j = arm_joints(np.radians(a_d), np.radians(b_d))
        ax.plot(j[:, 0], j[:, 1], "o-", lw=4, label=f"a={a_d}, b={b_d} deg")
        print(f"a={a_d:3d} deg, b={b_d:4d} deg -> hand {j[2].round(3)} m, reach {reach(np.radians(b_d)):.3f} m")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend()
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Two bones, two angles")
    fig.savefig(OUT / "two_bones.png", dpi=120)

    b_deg = np.linspace(0, 180, 181)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(b_deg, reach(np.radians(b_deg)))
    ax2.axhline(L1 + L2, color="gray", ls=":")
    ax2.axhline(abs(L1 - L2), color="gray", ls=":")
    ax2.set_xlabel("elbow angle b (degrees)")
    ax2.set_ylabel("shoulder-to-hand distance (m)")
    ax2.set_title("Reach: 0.55 m when straight, 0.05 m when folded")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "reach_vs_elbow.png", dpi=120)
    for a, b in solve_reach(0.35, 0.20):
        print(f"target (0.35, 0.20) m: a={np.degrees(a):.2f} deg, b={np.degrees(b):.2f} deg")

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
