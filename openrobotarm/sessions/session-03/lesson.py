"""Session 3 (Level 3): numerical inverse kinematics, singularities and a pick-and-place path.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: numerical inverse kinematics and a pick-and-place path
# **A. Real-world problem.** A pick-and-place robot must follow a path: lift the part from
# one spot, slide it to another. The path is a list of gripper positions; the motors need joint
# angles for every one of them. For a 3-joint arm in the plane there is no single formula (one
# spare joint), so we solve by iteration, like Newton's method. We also find out what goes
# wrong at a fully stretched arm and when a target cannot be reached.
#
# **Plan.** (1) the Jacobian, checked against finite differences, (2) damped least squares
# iteration, (3) singularities and manipulability, (4) a smooth straight-line path,
# (5) null-space joint-limit avoidance, (6) failure cases and sensitivity.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
LINKS = np.array([0.30, 0.25, 0.15])      # metres


# %% [markdown]
# ## Step 1: forward kinematics and the Jacobian
# x = sum L_k cos(c_k), y = sum L_k sin(c_k), with c_k = q_1 + ... + q_k. Joint i moves every
# link from i onwards, so a small turn dq_i moves the gripper by
#     d(x, y) = ( -sum_{k>=i} L_k sin(c_k),  sum_{k>=i} L_k cos(c_k) ) dq_i.
# Collect these columns in the 2 x 3 Jacobian J, so that  d(position) = J dq.

# %%
def fk(q, links=LINKS):
    c = np.cumsum(np.asarray(q, dtype=float))
    return np.array([np.sum(links * np.cos(c)), np.sum(links * np.sin(c))])


def jacobian(q, links=LINKS):
    c = np.cumsum(np.asarray(q, dtype=float))
    lx = np.asarray(links) * -np.sin(c)
    ly = np.asarray(links) * np.cos(c)
    # reverse cumulative sums: link k counts for every joint i <= k
    return np.array([np.cumsum(lx[::-1])[::-1], np.cumsum(ly[::-1])[::-1]])


def jacobian_fd(q, links=LINKS, h=1e-6):
    """The same matrix by finite differences (central), used only to check jacobian()."""
    q = np.asarray(q, dtype=float)
    cols = []
    for i in range(len(q)):
        dq = np.zeros(len(q))
        dq[i] = h
        cols.append((fk(q + dq, links) - fk(q - dq, links)) / (2 * h))
    return np.array(cols).T


# %% [markdown]
# ## Step 2: damped least squares (Newton-style) inverse kinematics
# If the gripper is off target by e = target - fk(q), we want dq with J dq = e. With 3 joints
# and 2 equations there are many dq; the one with the smallest size is the pseudoinverse
# J^T (J J^T)^-1 e. Near a singularity J J^T is almost not invertible, so we add lambda^2 I:
#     dq = J^T (J J^T + lambda^2 I)^-1 e
# Repeat until e is tiny. A step cap keeps the iteration from leaping far.

# %%
def dls_step(J, e, lam):
    return J.T @ np.linalg.solve(J @ J.T + lam ** 2 * np.eye(J.shape[0]), e)


def solve_ik(target, q0, links=LINKS, lam=0.01, limit=None, tol=1e-9, max_iter=300, max_step=0.1):
    """Iterate q <- q + dq. Returns (q, final error in metres, iterations used).
    limit: joint limit in radians (every |q_i| <= limit, applied by clipping) or None."""
    q = np.array(q0, dtype=float)
    target = np.asarray(target, dtype=float)
    for it in range(max_iter):
        e = target - fk(q, links)
        if np.linalg.norm(e) < tol:
            return q, float(np.linalg.norm(e)), it
        dq = dls_step(jacobian(q, links), e, lam)
        big = np.max(np.abs(dq))
        if big > max_step:
            dq *= max_step / big
        q = q + dq
        if limit is not None:
            q = np.clip(q, -limit, limit)
    return q, float(np.linalg.norm(target - fk(q, links))), max_iter


# %% [markdown]
# ## Step 3: singularities and manipulability
# The singular values s1 >= s2 of J say how easily the gripper moves in its two most and least
# movable directions. Their product w = s1 s2 = sqrt(det(J J^T)) is the manipulability. When
# the arm is fully stretched, J loses rank: s2 = 0, w = 0 and the gripper cannot move along
# the arm. A pure pseudoinverse then demands enormous joint speeds for any such motion.

# %%
def singular_values(q, links=LINKS):
    return np.linalg.svd(jacobian(q, links), compute_uv=False)


def manipulability(q, links=LINKS):
    s = singular_values(q, links)
    return float(s[0] * s[1])


def joint_speeds(q, v, links=LINKS, lam=None):
    """Joint speeds (rad/s) for a wanted gripper velocity v (m/s): pseudoinverse if lam is None, else damped."""
    J = jacobian(q, links)
    if lam is None:
        return np.linalg.pinv(J, rcond=1e-15) @ np.asarray(v, dtype=float)
    return dls_step(J, np.asarray(v, dtype=float), lam)


# %% [markdown]
# ## Step 4: a smooth straight-line path
# Move from A to B on a straight line, but not at constant speed (the robot would jerk at the
# start and stop). A quintic timing s(t) = 10 t^3 - 15 t^4 + 6 t^5, t in [0, 1], starts and
# ends with zero speed AND zero acceleration. Each point of the path is turned into joint
# angles by solve_ik, starting from the previous answer (a "warm start").

# %%
def quintic(t):
    t = np.asarray(t, dtype=float)
    return 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5


def cubic(t):
    t = np.asarray(t, dtype=float)
    return 3 * t ** 2 - 2 * t ** 3


def line_path(a, b, n=41, timing=quintic):
    s = timing(np.linspace(0.0, 1.0, n))[:, None]
    return np.asarray(a, dtype=float) + s * (np.asarray(b, dtype=float) - np.asarray(a, dtype=float))


def track_path(points, q0, links=LINKS, lam=0.01, limit=None, null_gain=0.0, q_pref=None, null_iters=20, tol=1e-10):
    """Joint angles for every path point (warm start from the previous point).
    null_gain > 0 adds null-space motion towards q_pref (default: all zeros): the arm changes shape
    but the gripper does not move, because N = I - J+ J removes everything that would move it."""
    q = np.array(q0, dtype=float)
    pref = np.zeros(len(q)) if q_pref is None else np.asarray(q_pref, dtype=float)
    out = []
    for p in points:
        p = np.asarray(p, dtype=float)
        for k in range(null_iters if null_gain > 0 else 1):
            if null_gain > 0:
                J = jacobian(q, links)
                Jp = J.T @ np.linalg.inv(J @ J.T + lam ** 2 * np.eye(2))
                q = q + (np.eye(len(q)) - Jp @ J) @ (null_gain * (pref - q))
            q, _, _ = solve_ik(p, q, links, lam=lam, limit=limit, tol=tol, max_iter=50)
        out.append(q.copy())
    return np.array(out)


def path_error(points, qs, links=LINKS):
    """Largest distance between the wanted points and forward kinematics of the joint angles (metres)."""
    return float(max(np.linalg.norm(np.asarray(p) - fk(q, links)) for p, q in zip(points, qs)))


# %% [markdown]
# ## Step 5: failure cases and sensitivity
# (a) an unreachable target: the iteration settles on the closest point it can get to;
# (b) joint limits can make a reachable point unreachable; (c) a link-length error moves the
# gripper by about the same amount.

# %%
def multi_start(target, links=LINKS, limit=None, starts=24, seed=0, lam=0.01, max_iter=300):
    """Best (smallest error) result over random starting poses."""
    rng = np.random.default_rng(seed)
    lim = np.pi if limit is None else limit
    best = None
    for _ in range(starts):
        q0 = rng.uniform(-lim, lim, len(links))
        q, err, _ = solve_ik(target, q0, links, lam=lam, limit=limit, max_iter=max_iter)
        if best is None or err < best[1]:
            best = (q, err)
    return best


def numeric_reach_map(limit, links=LINKS, cell=0.1, starts=5, tol=1e-6, max_iter=80):
    """Points of the disk whose multi-start numerical IK converges (error < tol); returns (xs, ys, mask)."""
    r_max = float(np.sum(links))
    xs = -r_max + (np.arange(int(np.ceil(2 * r_max / cell))) + 0.5) * cell
    mask = np.zeros((len(xs), len(xs)), dtype=bool)
    for i, y in enumerate(xs):
        for j, x in enumerate(xs):
            if np.hypot(x, y) <= r_max:
                mask[i, j] = multi_start((x, y), links, limit, starts, max_iter=max_iter)[1] < tol
    return xs, xs, mask


def link_error_effect(q, dl, links=LINKS):
    """Distance (m) the gripper moves when the link lengths are really links + dl instead of links."""
    return float(np.linalg.norm(fk(q, np.asarray(links) + np.asarray(dl)) - fk(q, links)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    q = np.radians([30, 40, -20])
    print("max |J - J_fd| =", np.abs(jacobian(q) - jacobian_fd(q)).max())
    a, b = np.array([0.25, -0.30]), np.array([0.25, 0.30])
    pts = line_path(a, b, 41)
    q_start = solve_ik(pts[0], [0.3, -0.3, 0.3])[0]
    plain = track_path(pts, q_start)
    nul = track_path(pts, q_start, null_gain=0.1)
    print("path error (m): plain", path_error(pts, plain), " null-space", path_error(pts, nul))
    print("largest joint angle (degrees): plain", np.degrees(np.abs(plain).max()).round(1),
          " null-space", np.degrees(np.abs(nul).max()).round(1))
    for eps in (0.1, 0.01, 0.001):
        qq = np.array([0.0, eps, 0.0])
        print(f"bend {eps}: s_min {singular_values(qq)[-1]:.5f}, pinv speed {np.linalg.norm(joint_speeds(qq, [0.1, 0])):.2f}, "
              f"damped speed {np.linalg.norm(joint_speeds(qq, [0.1, 0], lam=0.05)):.2f} rad/s")

    t = np.linspace(0, 1, 41)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, qs, name in ((axs[0], plain, "plain tracking"), (axs[1], nul, "with null-space motion")):
        for k in range(3):
            ax.plot(t, np.degrees(qs[:, k]), label=f"q{k + 1}")
        ax.axhline(120, color="gray", ls=":")
        ax.axhline(-120, color="gray", ls=":")
        ax.set_xlabel("path time t / T")
        ax.set_title(f"Joint angles, {name}")
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("joint angle (degrees); dotted: +-120 limits")
    axs[0].legend()
    fig.tight_layout()
    fig.savefig(OUT / "path_joints.png", dpi=110)

    eps = np.logspace(-4, -0.5, 40)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.loglog(eps, [np.linalg.norm(joint_speeds([0, e, 0], [0.1, 0])) for e in eps], label="pseudoinverse")
    ax2.loglog(eps, [np.linalg.norm(joint_speeds([0, e, 0], [0.1, 0], lam=0.05)) for e in eps], label="damped, lambda 0.05")
    ax2.set_xlabel("elbow bend away from straight (rad)")
    ax2.set_ylabel("joint speed norm (rad/s) for 0.1 m/s along the arm")
    ax2.set_title("Speeds blow up near the stretched singularity")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "singularity_speeds.png", dpi=120)
    q_far, err_far, _ = solve_ik((0.9, 0.0), [0.3, 0.3, 0.3])
    print("unreachable target (0.9, 0): gripper", fk(q_far).round(4), "error", round(err_far, 4))
    _, e120 = multi_start((-0.50, 0.0), limit=np.radians(120))
    _, e180 = multi_start((-0.50, 0.0))
    print("target (-0.50, 0.0): error with +-120 limit", round(e120, 4), " without limits", e180)

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
