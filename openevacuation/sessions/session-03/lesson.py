"""Session 3 (Level 3): simulate the evacuation of a building as a flow network and validate it.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate a building evacuation and plan it safely
# **A. Real-world problem.** A four-storey college block (ground + 3 upper floors) holds 120
# people on every floor. Everyone above the ground floor must come down the stairs. How long
# does the whole building take to empty, where do the queues form, and how many stairs of
# what width are needed so that everyone is out well before smoke makes the stairs unsafe?
#
# **Plan.** (1) a building as a network of links (doors, stair flights) with a capacity and a
# travel time, (2) a time-stepping queue model, (3) validation: Session 1 formula, conservation
# of people, bottleneck bound, convergence, (4) RSET against ASET: is the plan safe?

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

A_COEF = 0.266                      # m2/person, speed-density slope (Session 2)
K_LEVEL, K_STAIR = 1.40, 1.08       # m/s, level ground and 178/279 mm stair
EDGE = 0.15                         # m, edge strip of doors and stair walls


def fs_max(k):
    """Largest specific flow k / (4a), persons/(s m) (Session 2)."""
    return k / (4.0 * A_COEF)


def free_speed(k):
    """Unhindered walking speed 0.85 k (m/s): 1.19 on the level, 0.92 on the stair."""
    return 0.85 * k


def capacity(clear_width, k):
    """Largest flow (persons/s) of a door (k = 1.40) or stair (k = 1.08) of this clear width."""
    we = clear_width - 2.0 * EDGE
    if we <= 0:
        raise ValueError("the opening is narrower than its two edge strips")
    return fs_max(k) * we


# %% [markdown]
# ## Step 1: a building is a network of links
# Every door and every stair flight (one storey of stair) is a **link** with
#
# * a **capacity** C (persons/s): the largest flow it can carry, Fs_max x We (Session 2);
# * a **travel time** tau (s): how long it takes to walk through it when it is not crowded;
# * a **next** link: where people go after it.
#
# Each link has a queue at its entrance. In a time step dt at most C dt people leave the
# queue; they walk for tau seconds and then join the queue of the next link. People from a
# floor and people coming down the stair from above meet in the same queue, so they merge.
# This is the "hydraulic" or network model used in fire engineering hand calculations.

# %%
def simulate(links, sources, dt=0.5, t_max=7200.0):
    """Time-step a flow network.

    links: dict name -> {"cap": persons/s, "tau": s, "next": name or None (None = outside)}
    sources: list of (link name, release time s, persons): people who join that link's queue
    at that time. Returns a dict with the time array, people outside, people inside, the queue
    of every link and the evacuation time (when the last person is outside)."""
    if dt <= 0:
        raise ValueError("time step must be positive")
    for name, ln in links.items():
        if ln["cap"] <= 0 or ln["tau"] < 0:
            raise ValueError(f"link {name}: capacity must be positive and travel time not negative")
        if ln["next"] is not None and ln["next"] not in links:
            raise ValueError(f"link {name} leads to an unknown link {ln['next']}")
    total = float(sum(s[2] for s in sources))
    names = list(links)
    queue = {n: 0.0 for n in names}
    lag = {n: int(round(links[n]["tau"] / dt)) for n in names}
    pipe = {n: np.zeros(lag[n] + 1) for n in names}          # people walking inside each link
    todo = sorted(([s[1], s[0], float(s[2])] for s in sources), key=lambda s: s[0])
    t, outside = 0.0, 0.0
    T, OUTS, Q = [0.0], [0.0], {n: [0.0] for n in names}
    while t < t_max:
        while todo and todo[0][0] <= t + 1e-9:                 # release people whose time has come
            _, n, p = todo.pop(0)
            queue[n] += p
        arrive = {n: 0.0 for n in names}
        for n in names:
            served = min(queue[n], links[n]["cap"] * dt)
            queue[n] -= served
            pipe[n][0] += served
            leaving = pipe[n][-1]
            pipe[n] = np.roll(pipe[n], 1)
            pipe[n][0] = 0.0
            if lag[n] == 0:                                    # no travel time: leaves in the same step
                leaving = served
            if links[n]["next"] is None:
                outside += leaving
            else:
                arrive[links[n]["next"]] += leaving
        for n in names:
            queue[n] += arrive[n]
        t += dt
        T.append(t)
        OUTS.append(outside)
        for n in names:
            Q[n].append(queue[n])
        if outside >= total - 1e-6 and not todo:
            break
    outs = np.array(OUTS)
    return {"t": np.array(T), "outside": outs, "inside": total - outs,
            "queues": {n: np.array(v) for n, v in Q.items()}, "t_evac": t, "total": total}


# %% [markdown]
# ## Step 2: build a multi-storey block
# Floors 1..F are above the ground floor (floor 0). On every floor, n people react to the
# alarm after a **pre-movement time**, walk `corridor` metres to a stair door and queue. The
# stair flight of floor f takes them down to floor f - 1. The ground floor people walk straight
# to the final exit door, where they meet everyone coming down. With several stairs, each
# floor's people split equally and every stair has its own exit door.

# %%
def building(floors=3, per_floor=120, n_stairs=1, stair_width=1.2, door_width=1.2,
             exit_width=1.2, corridor=20.0, stair_length=9.0, t_pre=60.0):
    """Links and sources of a block with `floors` upper floors plus a ground floor."""
    if floors < 0 or per_floor < 0 or n_stairs < 1:
        raise ValueError("need floors >= 0, per_floor >= 0 and at least one stair")
    links, sources = {}, []
    t_release = t_pre + corridor / free_speed(K_LEVEL)
    share = per_floor / n_stairs
    for s in range(n_stairs):
        links[f"exit{s}"] = {"cap": capacity(exit_width, K_LEVEL), "tau": 0.0, "next": None}
        sources.append((f"exit{s}", t_release, share))                 # ground floor
        for f in range(1, floors + 1):
            below = f"stair{s}_{f - 1}" if f > 1 else f"exit{s}"
            links[f"stair{s}_{f}"] = {"cap": capacity(stair_width, K_STAIR),
                                      "tau": stair_length / free_speed(K_STAIR), "next": below}
            links[f"door{s}_{f}"] = {"cap": capacity(door_width, K_LEVEL), "tau": 0.0, "next": f"stair{s}_{f}"}
            sources.append((f"door{s}_{f}", t_release, share))
    return links, sources


def evacuate(dt=0.5, **kw):
    """Build the block and simulate it. Keyword arguments go to building()."""
    links, sources = building(**kw)
    return simulate(links, sources, dt=dt)


# %% [markdown]
# ## Step 3: a hand estimate to validate against
# Everyone from the upper floors must pass the lowest stair flight, whose capacity is C_s.
# The floor-1 people reach it first, at t_pre + corridor / v. Even if the flight is busy at
# full capacity from then on, the last person cannot leave it before
#
#     t_bound = t_pre + corridor / v + (floors x n) / C_s + tau_stair
#
# (tau_stair is that last person's walk down the flight). When the stair is the bottleneck and
# the exit door is wide enough, the simulation should sit just above this bound.

# %%
def bottleneck_bound(floors=3, per_floor=120, n_stairs=1, stair_width=1.2, corridor=20.0,
                     stair_length=9.0, t_pre=60.0):
    """Lower bound (s) on the evacuation time set by the lowest stair flight."""
    tau = stair_length / free_speed(K_STAIR)
    upper = floors * per_floor / n_stairs
    return t_pre + corridor / free_speed(K_LEVEL) + upper / capacity(stair_width, K_STAIR) + tau


# %% [markdown]
# ## Step 4: is the plan safe? RSET against ASET
# Fire engineers compare two times:
#
# * **RSET**, the required safe escape time: detection + pre-movement + movement (our t_evac
#   already contains pre-movement; we add a detection time);
# * **ASET**, the available safe escape time: how long until smoke or heat make the escape
#   route untenable. It comes from a fire model, not from this repo; here it is a given number.
#
# A plan is acceptable only when RSET x safety factor <= ASET. We use a factor of 1.5 for
# illustration; real codes and fire engineers set their own.

# %%
def rset(t_detect=30.0, **kw):
    """Required safe escape time (s) = detection + simulated evacuation (which contains t_pre)."""
    return t_detect + evacuate(**kw)["t_evac"]


def is_safe(aset, rset_value, factor=1.5):
    """True when RSET x factor does not exceed ASET."""
    if aset <= 0 or rset_value <= 0 or factor < 1:
        raise ValueError("ASET and RSET must be positive and the factor at least 1")
    return rset_value * factor <= aset + 1e-9


def stair_rset(n_stairs, width, **kw):
    """RSET (s) of the block with n_stairs stairs of this clear width. Stair doors are at least
    1.2 m and each final exit is 0.3 m wider than its stair door."""
    door = max(width, 1.2)
    return rset(n_stairs=n_stairs, stair_width=width, door_width=door, exit_width=door + 0.3, **kw)


def plan_stairs(aset, widths=(1.0, 1.2, 1.5, 1.8, 2.0), factor=1.5, **kw):
    """Narrowest width for TWO stairs that is safe with both open AND with one blocked by smoke
    (then everyone uses the other one). Returns (width, rset both open, rset one blocked) or None."""
    for w in widths:
        both, blocked = stair_rset(2, w, **kw), stair_rset(1, w, **kw)
        if is_safe(aset, both, factor) and is_safe(aset, blocked, factor):
            return w, both, blocked
    return None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    base = dict(floors=3, per_floor=120, stair_width=1.2, door_width=1.2, exit_width=1.5)
    one = evacuate(n_stairs=1, **base)
    two = evacuate(n_stairs=2, **base)
    print(f"stair capacity {capacity(1.2, K_STAIR):.3f} persons/s, door capacity {capacity(1.2, K_LEVEL):.3f} persons/s")
    print(f"one stair : t_evac {one['t_evac']:.1f} s, bound {bottleneck_bound(n_stairs=1):.1f} s")
    print(f"two stairs: t_evac {two['t_evac']:.1f} s, bound {bottleneck_bound(n_stairs=2):.1f} s")

    # Figure 1: people still inside the building
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    for res, lab, col in [(one, "one 1.2 m stair", "#d9534f"), (two, "two 1.2 m stairs", "#2a9d8f")]:
        ax.plot(res["t"], res["inside"], color=col, lw=2.2, label=f"{lab}: empty at {res['t_evac']:.0f} s")
    ax.axvspan(0, 60, color="0.85", alpha=0.6)
    ax.text(30, 30, "pre-\nmovement", ha="center", fontsize=8)
    ax.set_xlabel("time after the alarm (s)")
    ax.set_ylabel("people still inside")
    ax.set_title("480 people leave a 4-storey block")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 500)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "building_emptying.png", dpi=120)

    # Figure 2: where the queues form (one stair)
    fig2, ax2 = plt.subplots(figsize=(6.6, 4.2))
    cols = {"3": "#6f42c1", "2": "#1f6feb", "1": "#2a9d8f"}
    for f, c in cols.items():
        q = one["queues"][f"door0_{f}"] + one["queues"][f"stair0_{f}"]
        ax2.plot(one["t"], q, color=c, lw=2, label=f"landing of floor {f} (top of flight {f})")
    ax2.plot(one["t"], one["queues"]["exit0"], color="#d9534f", lw=2, label="final exit (ground)")
    ax2.set_xlabel("time after the alarm (s)")
    ax2.set_ylabel("people waiting in the queue")
    ax2.set_title("one 1.2 m stair: the big queue builds on the floor-1 landing")
    ax2.set_xlim(0, 600)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "queues.png", dpi=120)

    # Figure 3: the plan: RSET x 1.5 against ASET for each design
    aset = 900.0
    designs = [(n, w) for n in (1, 2) for w in (1.0, 1.2, 1.5, 2.0)]
    vals = [stair_rset(n, w) for n, w in designs]
    fig3, ax3 = plt.subplots(figsize=(7.2, 4.2))
    colors = ["#2a9d8f" if is_safe(aset, r) else "#d9534f" for r in vals]
    ax3.bar(range(len(designs)), [1.5 * r for r in vals], color=colors)
    ax3.axhline(aset, color="k", ls="--", lw=1.2)
    ax3.text(len(designs) - 0.5, aset + 15, f"ASET = {aset:.0f} s (illustrative)", ha="right", fontsize=8)
    for i, r in enumerate(vals):
        ax3.text(i, 1.5 * r + 10, f"{r:.0f}", ha="center", fontsize=8)
        print(f"design {designs[i][0]} stair(s) x {designs[i][1]} m: RSET {r:.0f} s, 1.5 x RSET {1.5 * r:.0f} s, safe {is_safe(aset, r)}")
    ax3.set_xticks(range(len(designs)))
    ax3.set_xticklabels([f"{n} x {w} m" for n, w in designs], fontsize=8)
    ax3.text(1.5, 1220, "one stair open (or the other is blocked)", ha="center", fontsize=8)
    ax3.text(5.5, 1220, "two stairs open", ha="center", fontsize=8)
    ax3.axvline(3.5, color="0.5", lw=1)
    ax3.set_xlabel("stairs x clear width (numbers on bars: RSET in s)")
    ax3.set_ylabel("1.5 x RSET (s)")
    ax3.set_title("Which stair plan is safe? green: 1.5 x RSET below ASET")
    ax3.set_ylim(0, 1300)
    fig3.tight_layout()
    fig3.savefig(OUT / "rset_aset.png", dpi=120)
    w, both, blocked = plan_stairs(aset)
    print(f"plan: two stairs of {w} m; RSET {both:.0f} s with both open, {blocked:.0f} s with one blocked")

# %% [markdown]
# ## Where this stops
# Every person here is part of a smooth fluid with one pre-movement time and one speed. Real
# people start at different times, some move slowly or need help, and people choose exits.
# The roadmap shows how to add these effects, a floor plan you can draw, and agent-based
# simulation, on the way to the Target.
