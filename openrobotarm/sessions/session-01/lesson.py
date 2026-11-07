"""Session 1 (Level 1): a robot arm is a chain of links and joints.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a robot arm is a chain of links and joints
# **A. Real-world problem.** A pick-and-place robot lifts a block from one spot and sets it
# down on another. Its motors only turn joints. Nobody tells the gripper "go to x, y": we
# have to work out which joint angles put it there. Today: the forward half of that question.
#
# **Plan.** (1) describe a 3-link arm by its link lengths and joint angles, (2) add angles
# down the chain, (3) find the gripper, (4) find the longest reach and test a block.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
LINKS = np.array([0.30, 0.25, 0.15])      # link lengths in metres: shoulder-elbow, elbow-wrist, wrist-gripper
BLOCK = np.array([0.40, 0.30])            # the block we want to pick up (metres)


# %% [markdown]
# ## Step 1: the angle of each link in the room
# Each joint angle is measured *relative to the link before it*. So link 2 points in the
# direction q1 + q2 and link 3 in the direction q1 + q2 + q3: angles add up down the chain.
# These running totals are called the cumulative angles.

# %%
def cumulative_angles(q):
    """Direction of every link measured from the x axis, in radians."""
    return np.cumsum(np.asarray(q, dtype=float))


# %% [markdown]
# ## Step 2: walk along the chain
# Start at the base (0, 0). Each link adds length * (cos angle, sin angle). The last point is
# the gripper. The tool angle (which way the gripper points) is the sum of all joint angles.

# %%
def link_points(q, links=LINKS):
    """Base, elbow, wrist, gripper as four (x, y) points in metres. Angles in radians."""
    c = cumulative_angles(q)
    steps = np.asarray(links)[:, None] * np.stack([np.cos(c), np.sin(c)], axis=1)
    return np.vstack([[0.0, 0.0], np.cumsum(steps, axis=0)])


def gripper(q, links=LINKS):
    return link_points(q, links)[-1]


def tool_angle(q):
    return float(np.sum(q))


# %% [markdown]
# ## Step 3: how far can the arm reach, and can it touch the block?
# The gripper can never be farther from the base than the sum of the link lengths (arm
# straight). We can test a block by comparing distances.

# %%
def max_reach(links=LINKS):
    return float(np.sum(links))


def touches(q, target, tol=0.02, links=LINKS):
    """True if the gripper is within tol metres of the target."""
    return bool(np.linalg.norm(gripper(q, links) - np.asarray(target)) <= tol)


def find_pose(target, tol=0.02, step_deg=5, links=LINKS):
    """Brute force: try joint angles q1, q2 in steps and q3 free; return the first pose that touches.
    (Slow and clumsy: Sessions 2 and 3 replace it with maths.)"""
    grid = np.radians(np.arange(-180, 180, step_deg))
    for a in grid:
        for b in grid:
            for c in grid:
                q = np.array([a, b, c])
                if touches(q, target, tol, links):
                    return q
    return None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(5.8, 5.2))
    for q_d, col in [((0, 0, 0), "tab:gray"), ((30, 40, -20), "tab:blue"), ((70, -60, -30), "tab:green")]:
        q = np.radians(q_d)
        p = link_points(q)
        ax.plot(p[:, 0], p[:, 1], "o-", lw=4, color=col, label=f"q = {q_d} deg")
        print(f"q = {q_d} deg -> gripper {p[-1].round(3)} m, tool angle {np.degrees(tool_angle(q)):.0f} deg")
    ax.add_patch(plt.Circle((0, 0), max_reach(), fill=False, ls="--", color="gray"))
    ax.plot(*BLOCK, "s", ms=12, color="tab:red", label="block (0.40, 0.30) m")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("A 3-link arm in three poses; dashed: longest reach 0.70 m")
    fig.savefig(OUT / "arm_poses.png", dpi=120)

    q1 = np.radians(np.linspace(-180, 180, 361))
    xy = np.array([gripper([a, np.radians(40), np.radians(-20)]) for a in q1])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(np.degrees(q1), xy[:, 0], label="gripper x")
    ax2.plot(np.degrees(q1), xy[:, 1], label="gripper y")
    ax2.set_xlabel("shoulder angle q1 (degrees), q2 = 40, q3 = -20")
    ax2.set_ylabel("gripper coordinate (m)")
    ax2.set_title("Turning only the shoulder swings the gripper round a circle")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "gripper_vs_q1.png", dpi=120)
    pose = find_pose(BLOCK, step_deg=10)
    print("brute-force pose for the block (degrees):", None if pose is None else np.degrees(pose).round(0))

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
