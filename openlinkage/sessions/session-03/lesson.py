"""Session 3 (Level 3): simulate a walking leg, validate it, and tune its stance path.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a four-bar walking leg
# **A. Real-world problem.** Theo Jansen's beach walkers and many walking toys move on legs that
# are nothing but a four-bar linkage with a long coupler. The foot is a point on the coupler.
# For a smooth walk the foot must move along an almost straight line while it is on the ground
# (the stance), so the body glides forward without bobbing, and then lift off and swing back.
# Today you simulate one full crank turn, validate it twice, measure how straight the stance is,
# see how fragile that straightness is, and tune a leg.
#
# **Our leg.** A four-bar with ground : crank : coupler : rocker = 4.4 : 1 : 3.5 : 2.25 and the
# foot P on the extension of the coupler beyond B:  P = A + k (B - A) with k = 1.6. The crank is
# the shortest bar, so the crank turns fully. A leg must be flat while it is on the ground AND
# keep its foot clear of the ground while it swings back: Step 5 shows that these two wishes
# fight each other, and why the textbook straight-line linkages are not legs.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
LEG = dict(a=4.4, b=1.0, c=3.5, d=2.25)     # ground, crank, coupler, rocker (crank length = 1 unit)
K_FOOT = 1.6                                # foot P = A + K_FOOT * (B - A): beyond the pin B
HOEKEN = dict(a=2.0, b=1.0, c=2.5, d=2.5)   # Hoeken-type straight-line proportions, foot at k = 2
LAMBDA = dict(a=4.0, b=1.0, c=2.0, d=5.0)   # commonly quoted Chebyshev lambda proportions, foot at k = 1.25


# %% [markdown]
# ## Step 1: simulate a full turn
# For an array of crank angles we place A, then B by two circles (Session 1). `branch=-1`
# picks the assembly where the foot hangs below the frame. Validation 1: the loop closes
# (error below 1e-12) and the four bar lengths stay constant.

# %%
def joints(theta, a, b, c, d, branch=-1):
    """Pins A and B for an array of crank angles (radians). Raises ValueError if unreachable."""
    theta = np.atleast_1d(np.asarray(theta, float))
    pa = np.stack([b * np.cos(theta), b * np.sin(theta)], axis=1)
    v = np.array([a, 0.0]) - pa
    dist = np.hypot(v[:, 0], v[:, 1])
    if np.any(dist == 0.0):
        raise ValueError("crank tip sits on the rocker pivot")
    x = (c * c - d * d + dist * dist) / (2 * dist)
    h2 = c * c - x * x
    if np.any(h2 < -1e-12 * c * c):
        raise ValueError("the circles do not meet: the linkage cannot reach this crank angle")
    e = v / dist[:, None]
    n = np.stack([-e[:, 1], e[:, 0]], axis=1)
    pb = pa + x[:, None] * e + branch * np.sqrt(np.maximum(h2, 0.0))[:, None] * n
    return pa, pb


def foot_path(theta, a=4.4, b=1.0, c=3.5, d=2.25, k=K_FOOT, branch=-1):
    pa, pb = joints(theta, a, b, c, d, branch)
    return pa + k * (pb - pa)


def loop_closure_error(theta, a, b, c, d, branch=-1):
    """Largest loop-closure residual, and largest change of any bar length, over the angles."""
    theta = np.atleast_1d(np.asarray(theta, float))
    pa, pb = joints(theta, a, b, c, d, branch)
    t3 = np.arctan2(pb[:, 1] - pa[:, 1], pb[:, 0] - pa[:, 0])
    t4 = np.arctan2(pb[:, 1], pb[:, 0] - a)
    res = np.stack([b * np.cos(theta) + c * np.cos(t3) - d * np.cos(t4) - a,
                    b * np.sin(theta) + c * np.sin(t3) - d * np.sin(t4)])
    lens = np.stack([np.hypot(pa[:, 0], pa[:, 1]), np.hypot(*(pb - pa).T), np.hypot(pb[:, 0] - a, pb[:, 1])])
    drift = np.abs(lens - np.array([b, c, d])[:, None]).max()
    return float(np.abs(res).max()), float(drift)


# %% [markdown]
# ## Step 2: velocity two ways
# **Finite differences:** move the crank by a tiny step either side and divide.
# **Analytic (Jacobian):** differentiate the loop equation. With crank speed w2 = 1 rad/s
# the coupler and rocker speeds w3, w4 solve a 2x2 linear system, and the foot velocity is
# v_P = w2 z x A + w3 z x (P - A)  (z x r = (-ry, rx) turns a vector by 90 degrees).
# **Instant centre:** the coupler line AB meets the ground line at I24; both the crank and the
# rocker see I24 move at the same speed, so w4 / w2 = x_I / (x_I - a).

# %%
def analytic_velocity(theta, a, b, c, d, k=K_FOOT, branch=-1):
    """(foot velocity, w3, w4) for crank speed 1 rad/s, from the Jacobian of the loop equation."""
    theta = np.atleast_1d(np.asarray(theta, float))
    pa, pb = joints(theta, a, b, c, d, branch)
    t3 = np.arctan2(pb[:, 1] - pa[:, 1], pb[:, 0] - pa[:, 0])
    t4 = np.arctan2(pb[:, 1], pb[:, 0] - a)
    m11, m12 = -c * np.sin(t3), d * np.sin(t4)
    m21, m22 = c * np.cos(t3), -d * np.cos(t4)
    r1, r2 = b * np.sin(theta), -b * np.cos(theta)
    det = m11 * m22 - m12 * m21
    w3 = (r1 * m22 - m12 * r2) / det
    w4 = (m11 * r2 - m21 * r1) / det
    arm = k * (pb - pa)                       # from A to the foot: (P - A) = k (B - A)
    vel = np.stack([-pa[:, 1], pa[:, 0]], axis=1) + w3[:, None] * np.stack([-arm[:, 1], arm[:, 0]], axis=1)
    return vel, w3, w4


def finite_difference_velocity(theta, a, b, c, d, k=K_FOOT, branch=-1, h=1e-5):
    theta = np.atleast_1d(np.asarray(theta, float))
    return (foot_path(theta + h, a, b, c, d, k, branch) - foot_path(theta - h, a, b, c, d, k, branch)) / (2 * h)


def rocker_speed_instant_centre(theta, a, b, c, d, branch=-1):
    """w4 / w2 from the instant centre I24 where the coupler line crosses the ground line."""
    pa, pb = joints(theta, a, b, c, d, branch)
    s = -pa[:, 1] / (pb[:, 1] - pa[:, 1])
    xi = pa[:, 0] + s * (pb[:, 0] - pa[:, 0])
    return xi / (xi - a)


# %% [markdown]
# ## Step 3: mechanical advantage and power balance
# An ideal (frictionless, massless) linkage loses no power: torque_in * w_in = torque_out * w_out.
# So the torque multiplication is  MA = torque_out / torque_in = w2 / w4. We check it with
# statics, which does not use speeds at all: the coupler is a two-force bar, so it pushes along
# AB with a force F, and each torque is F times a distance. The ratio of the two torques must
# equal the speed ratio.

# %%
def torque_ratio_statics(theta, a, b, c, d, branch=-1):
    """|torque on rocker| / |torque on crank| when the coupler pushes with force F along AB."""
    pa, pb = joints(theta, a, b, c, d, branch)
    u = (pb - pa) / np.hypot(*(pb - pa).T)[:, None]
    cross = lambda r, w: r[:, 0] * w[:, 1] - r[:, 1] * w[:, 0]
    return np.abs(cross(pb - np.array([a, 0.0]), u) / cross(pa, u))


# %% [markdown]
# ## Step 4: how straight is the stance, and does the swing stay clear of the ground?
# Sample the foot at every degree of crank angle. A *stance* is a run of consecutive crank
# angles (`span` degrees, so the duty factor is span / 360). Deviation = the largest distance of
# the foot from the best straight line through its stance points (least squares, perpendicular
# distances). We slide the window round the cycle and keep the straightest one. Stride = the
# straight distance between the first and last stance point. Then look at the rest of the cycle
# (the swing) measured as height above the stance line, positive towards the body:
# lift = the highest the foot gets, dig = how far the foot goes BELOW the line (it would have to
# dig into the ground). A usable leg has a small deviation, a decent lift and no dig. One more
# check for a leg you could really build: `pin_low`, the height of the lowest pin of the whole
# linkage over the turn (negative means a pin would be under the ground when the leg is mounted
# with its stance line level).

# %%
def window_deviations(path, span):
    """Deviation from the best-fit line for every circular window of span+1 consecutive points."""
    n = len(path)
    idx = (np.arange(n)[:, None] + np.arange(span + 1)[None, :]) % n
    w = path[idx]                                           # (n windows, span+1 points, 2)
    mean = w.mean(axis=1, keepdims=True)
    cen = w - mean
    cov = np.einsum("nki,nkj->nij", cen, cen)
    vals, vecs = np.linalg.eigh(cov)
    normal = vecs[:, :, 0]                                  # direction of least spread
    return np.abs(np.einsum("nki,ni->nk", cen, normal)).max(axis=1)


def stance_report(a, b, c, d, k=K_FOOT, span=180, branch=-1, n=360):
    """Straightest stance of the leg: start angle, deviation, stride, lift, dig and line tilt."""
    theta = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    path = foot_path(theta, a, b, c, d, k, branch)
    dev = window_deviations(path, span)
    s = int(np.argmin(dev))
    idx = (s + np.arange(span + 1)) % n
    seg = path[idx]
    chord = seg[-1] - seg[0]
    stride = float(np.hypot(*chord))
    direction = chord / stride
    normal = np.array([-direction[1], direction[0]])
    if (np.array([a / 2.0, 0.0]) - seg.mean(axis=0)) @ normal < 0:
        normal = -normal                                    # make the normal point towards the body
    swing_idx = np.setdiff1d(np.arange(n), idx)
    height = (path[swing_idx] - seg.mean(axis=0)) @ normal
    tilt = float(np.degrees(np.arctan2(abs(chord[1]), abs(chord[0]))))
    pa, pb = joints(theta, a, b, c, d, branch)
    pins = np.vstack([pa, pb, [[0.0, 0.0]], [[a, 0.0]]])        # every pin of the linkage over the whole turn
    pin_low = float(((pins - seg.mean(axis=0)) @ normal).min())
    return dict(start_deg=360.0 * s / n, deviation=float(dev[s]), stride=stride, lift=float(height.max()),
                dig=float(max(0.0, -height.min())), duty=span / 360.0, tilt_deg=tilt, pin_low=pin_low)


def min_transmission_angle(a, b, c, d, n=720):
    """Smallest angle (degrees) between coupler and rocker over a full crank turn."""
    theta = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    pa, pb = joints(theta, a, b, c, d)
    u, w = pa - pb, np.array([a, 0.0]) - pb
    cosmu = (u * w).sum(axis=1) / (np.hypot(*u.T) * np.hypot(*w.T))
    return float(np.degrees(np.arccos(np.clip(cosmu, -1.0, 1.0))).min())


def stance_speed_spread(a, b, c, d, k=K_FOOT, span=180, branch=-1):
    """(fastest - slowest) / mean speed of the foot ALONG the stance line, crank turning steadily."""
    rep = stance_report(a, b, c, d, k, span, branch)
    deg = np.arange(360.0)
    vel, _, _ = analytic_velocity(np.radians(deg), a, b, c, d, k, branch)
    path = foot_path(np.radians(deg), a, b, c, d, k, branch)
    idx = (int(rep["start_deg"]) + np.arange(span + 1)) % 360
    chord = path[idx[-1]] - path[idx[0]]
    along = vel[idx] @ (chord / np.hypot(*chord))
    return float((along.max() - along.min()) / along.mean())


# %% [markdown]
# ## Step 5: flat OR clear? sensitivity, and a failure case
# Compare three linkages with the same measurements. The textbook straight-line proportions are
# almost perfectly flat, but the rest of their path lies on the WRONG side of the stance line: a
# foot standing on the ground would have to dig into it during the swing (large `dig`). Our leg is
# less flat but keeps the swing on the body side (lift, no dig). The side flips abruptly when one
# bar changes: make the ground bar 4.0 instead of 4.4 and the same leg digs. Then change ONE bar
# by 1 percent. Finally the failure: if the rocker is much too short, Grashof's rule fails, the
# crank cannot go round, and the linkage locks at a dead centre where the coupler and the rocker
# lie on one line (transmission angle 0 or 180 degrees: no push can turn the rocker).

# %%
def sensitivity(base, k=K_FOOT, span=180, change=0.01):
    """Stance report after making each bar (and the foot extension k) 1 percent longer."""
    out = {}
    for name in ("a", "b", "c", "d", "k"):
        p = dict(base, k=k)
        p[name] = p[name] * (1.0 + change)
        out[name] = stance_report(span=span, **p)
    return out


def crank_limits(a, b, c, d, step_deg=0.05):
    """Where the crank gets stuck: (last reachable angle, first reachable angle after the gap), in
    degrees, refined by bisection; None if the crank can turn a full circle."""
    def ok(t):
        try:
            joints(t, a, b, c, d)
            return True
        except ValueError:
            return False
    grid = np.radians(np.arange(0.0, 360.0, step_deg))
    flags = np.array([ok(t) for t in grid])
    if flags.all():
        return None
    shift = int(np.argmax(flags))                           # first reachable index: start the walk there
    flags = np.roll(flags, -shift)
    n, step = len(grid), np.radians(step_deg)
    i = int(np.argmin(flags))                               # first unreachable index after the start
    lo = grid[(shift + i - 1) % n]
    hi = lo + step
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    stuck = lo
    j = i + int(np.argmax(flags[i:])) if flags[i:].any() else n   # first reachable index after the gap (may wrap)
    hi2 = grid[(shift + j) % n]
    lo2 = hi2 - step
    for _ in range(60):
        mid = 0.5 * (lo2 + hi2)
        lo2, hi2 = (lo2, mid) if ok(mid) else (mid, hi2)
    return float(np.degrees(stuck) % 360.0), float(np.degrees(hi2) % 360.0)


def transmission_angle_at(theta, a, b, c, d, branch=-1):
    pa, pb = joints(theta, a, b, c, d, branch)
    u, w = pa[0] - pb[0], np.array([a, 0.0]) - pb[0]
    return float(np.degrees(np.arccos(np.clip(u @ w / (np.hypot(*u) * np.hypot(*w)), -1.0, 1.0))))


# %% [markdown]
# ## Step 6: mini-project, tune the leg
# Keep the crank 1, the coupler 3.5 and the rocker 2.25. You choose the ground bar a (3.6 to 5.2,
# step 0.1) and the foot position k (1.0 to 2.0, step 0.05). A leg is acceptable if the foot
# digs at most 0.5 percent of the stride below the stance line, lifts at least 15 percent of the
# stride during the swing, and keeps the smallest transmission angle at or above 40 degrees (the
# common guideline). Among acceptable legs pick the one with the smallest stance deviation (as a
# percentage of the stride, 180 degree stance).

# %%
def tune_leg(max_dig=0.005, min_lift=0.15, min_mu=40.0, span=180):
    """Grid search over ground a and foot k (crank 1, coupler 3.5, rocker 2.25). Returns the
    acceptable legs, flattest first, as (deviation % of stride, a, k, lift %, dig %, stride, smallest mu)."""
    out = []
    for a in np.arange(3.6, 5.2001, 0.1):
        for k in np.arange(1.0, 2.0001, 0.05):
            try:
                r = stance_report(a, 1.0, 3.5, 2.25, k, span)
                mu = min_transmission_angle(a, 1.0, 3.5, 2.25)
            except ValueError:
                continue
            s = r["stride"]
            if r["dig"] <= max_dig * s and r["lift"] >= min_lift * s and mu >= min_mu:
                out.append((100 * r["deviation"] / s, round(float(a), 2), round(float(k), 2),
                            100 * r["lift"] / s, 100 * r["dig"] / s, s, mu))
    return sorted(out)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    theta = np.radians(np.arange(0.0, 360.0, 1.0))
    err, drift = loop_closure_error(theta, **LEG)
    print(f"loop-closure error {err:.2e}, largest bar-length change {drift:.2e}")
    vel, w3, w4 = analytic_velocity(theta, **LEG)
    fd = finite_difference_velocity(theta, **LEG)
    print(f"foot velocity: analytic vs finite difference, largest difference {np.abs(vel - fd).max():.2e}")
    pa, pb = joints(theta, **LEG)
    ok = np.abs(pb[:, 1] - pa[:, 1]) > 1e-3
    print("w4/w2: Jacobian vs instant centre, largest difference "
          f"{np.abs(w4[ok] - rocker_speed_instant_centre(theta, **LEG)[ok]).max():.2e}")
    ma_stat = torque_ratio_statics(theta, **LEG)
    good = np.abs(w4) > 0.2
    print("torque ratio: statics vs |w2/w4|, largest relative difference "
          f"{(np.abs(ma_stat - np.abs(1.0 / w4))[good] / np.abs(1.0 / w4)[good]).max():.2e}")

    for name, bars, kk in (("our leg", LEG, K_FOOT), ("Hoeken-type", HOEKEN, 2.0), ("lambda", LAMBDA, 1.25)):
        r = stance_report(span=180, k=kk, **bars)
        srt = sorted(bars.values())
        print(f"{name:12s} s+l = {srt[0] + srt[3]:.2f}, p+q = {srt[1] + srt[2]:.2f}; deviation {r['deviation']:.4f} "
              f"({100 * r['deviation'] / r['stride']:.3f} % of stride), stride {r['stride']:.3f}, lift {r['lift']:.3f}, "
              f"dig {r['dig']:.3f}, line tilt {r['tilt_deg']:.1f} deg, smallest mu {min_transmission_angle(**bars):.1f} deg")
    base = stance_report(span=180, k=K_FOOT, **LEG)
    flip = stance_report(span=180, k=K_FOOT, **dict(LEG, a=4.0))
    print(f"ground bar 4.0 instead of 4.4: deviation {100 * flip['deviation'] / flip['stride']:.2f} %, "
          f"lift {flip['lift']:.3f}, dig {flip['dig']:.3f} ({100 * flip['dig'] / flip['stride']:.1f} % of stride)")
    print(f"foot speed along the stance line varies by {100 * stance_speed_spread(**LEG):.0f} % of its mean")
    print("1 percent longer bar -> deviation / stride / lift / dig:")
    for key, r in sensitivity(LEG).items():
        print(f"   {key}: {r['deviation']:.4f} / {r['stride']:.3f} / {r['lift']:.3f} / {r['dig']:.4f}")
    fail = dict(a=4.4, b=1.0, c=3.5, d=1.5)
    lim = crank_limits(**fail)
    print(f"short rocker (d = 1.5): crank stuck at {lim[0]:.2f} degrees, transmission angle there "
          f"{transmission_angle_at(np.radians(lim[0]), **fail):.3f} degrees")
    top = tune_leg()
    print(f"{len(top)} acceptable legs; best: deviation {top[0][0]:.3f} %, a = {top[0][1]}, k = {top[0][2]}, "
          f"lift {top[0][3]:.1f} %, dig {top[0][4]:.2f} %, stride {top[0][5]:.3f}, mu {top[0][6]:.1f}")

    ths = np.radians(np.arange(0.0, 361.0, 1.0))
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for k, col in ((1.0, "tab:purple"), (1.3, "tab:orange"), (1.6, "tab:blue"), (1.9, "tab:green")):
        p = foot_path(ths, **LEG, k=k)
        ax.plot(p[:, 0], p[:, 1], color=col, lw=2 if k == 1.6 else 1, label=f"k = {k}")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_xlabel("x (crank lengths)")
    ax.set_ylabel("y (crank lengths)")
    ax.set_title("Coupler-point paths for four foot positions")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "coupler_paths.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for name, bars, kk, col in (("our leg (a = 4.4)", LEG, K_FOOT, "tab:blue"),
                                ("ground bar 4.0: digs", dict(LEG, a=4.0), K_FOOT, "tab:red"),
                                ("Hoeken-type: flat but digs", HOEKEN, 2.0, "tab:orange")):
        rep = stance_report(span=180, k=kk, **bars)
        pth = foot_path(ths, **bars, k=kk)
        s0 = int(rep["start_deg"])
        stance = np.arange(s0, s0 + 181) % 360
        pts = pth[stance]
        ax2.plot(pth[:, 0] - pts[:, 0].mean(), pth[:, 1] - pts[:, 1].mean(), color=col, lw=1, label=name)
        ax2.plot(pts[:, 0] - pts[:, 0].mean(), pts[:, 1] - pts[:, 1].mean(), color=col, lw=3.5)
    ax2.set_aspect("equal")
    ax2.grid(alpha=0.3)
    ax2.set_xlabel("x relative to the stance centre (crank lengths)")
    ax2.set_ylabel("y relative to the stance centre (crank lengths)")
    ax2.set_title("Thick: stance. The body is above the paths.", fontsize=10)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "foot_stance.png", dpi=120)

    fig3, ax3 = plt.subplots(figsize=(6.4, 3.8))
    ax3.plot(np.degrees(theta), np.abs(1.0 / w4), label="speed ratio |w2 / w4|")
    ax3.plot(np.degrees(theta), ma_stat, "--", label="torque ratio from statics")
    ax3.set_ylim(0, 8)
    ax3.set_xlabel("crank angle (degrees)")
    ax3.set_ylabel("mechanical advantage (no unit)")
    ax3.set_title("Power balance: speed ratio equals torque ratio")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "mechanical_advantage.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
