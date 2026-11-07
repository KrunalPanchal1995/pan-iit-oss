"""Session 2 (Level 2): the speed-density law, maximum flow and where queues form.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: speed, density and the bottleneck
# **A. Real-world problem.** A 2 m wide corridor carries students out of a lecture block.
# At its end is a 1.2 m door into the stair. Will a queue form at that door, how fast will it
# grow, and why does squeezing more people into the corridor not make them leave faster?
#
# **Plan.** (1) a linear speed-density law, (2) specific flow and its maximum,
# (3) stairs are slower than corridors, (4) conservation of flow at a change of width,
# which tells you where queues form.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

A_COEF = 0.266        # m2 per person: the slope a in v = k (1 - a D)
D_MIN = 0.15 / A_COEF # persons/m2: about 0.56; below this people walk at their free speed
D_JAM = 1.0 / A_COEF  # persons/m2: about 3.8, the crowd stops
K_LEVEL = 1.40        # m/s: constant k for corridors, ramps and doorways
# k for stairs depends on the step size: (riser m, tread m) -> k in m/s
STAIR_K = {(0.191, 0.254): 1.00, (0.178, 0.279): 1.08, (0.165, 0.305): 1.16, (0.165, 0.330): 1.23}
EDGE = {"door": 0.15, "stair": 0.15, "corridor": 0.20}   # m lost at each side


# %% [markdown]
# ## Step 1: a speed-density law
# Measurements of real crowds (Fruin, Pauls, Predtechenskii and Milinskii; collected in the
# SFPE Handbook) show that walking speed falls roughly in a straight line as the crowd gets
# denser:
#
#     v = k (1 - a D)        a = 0.266 m2/person
#
# k is 1.40 m/s on level ground. Below about 0.55 persons/m2 people are not slowed by others
# and walk at their free speed 0.85 k (1.19 m/s on the level). (The handbook quotes 0.54; we
# use 0.15 / a = 0.564 so that the two pieces of the law meet without a jump.) At D = 1 / a = 3.8 persons/m2
# the crowd is jammed and v = 0.

# %%
def speed(density, k=K_LEVEL):
    """Walking speed (m/s) at a crowd density (persons/m2). Works on numbers and arrays."""
    d = np.asarray(density, float)
    if np.any(d < 0):
        raise ValueError("density cannot be negative")
    v = k * (1.0 - A_COEF * np.clip(d, D_MIN, D_JAM))
    v = np.where(d < D_MIN, 0.85 * k, v)
    return float(v) if v.ndim == 0 else v


# %% [markdown]
# ## Step 2: specific flow has a maximum
# The specific flow (persons per second per metre of effective width) is density x speed:
#
#     Fs = D v = k D (1 - a D)
#
# This is a downward parabola. It is zero for an empty corridor (no people) and for a jammed
# one (no speed). Its peak is half way, at D* = 1 / (2a) = 1.88 persons/m2, where
#
#     Fs_max = k / (4a) = 1.40 / 1.064 = 1.32 persons/(s m)
#
# This is the 1.3 we used in Session 1. Pushing the density above D* lowers the flow: a
# packed crowd is slower than a dense but moving one.

# %%
def specific_flow(density, k=K_LEVEL):
    """Specific flow Fs = D v (persons per second per metre of effective width)."""
    fs = np.asarray(density, float) * speed(density, k)
    return float(fs) if np.ndim(fs) == 0 else fs


def optimal_density():
    """Density (persons/m2) at which the specific flow is largest: 1 / (2a)."""
    return 1.0 / (2.0 * A_COEF)


def max_specific_flow(k=K_LEVEL):
    """Largest specific flow k / (4a), persons/(s m)."""
    return k / (4.0 * A_COEF)


def density_for_flow(fs, k=K_LEVEL):
    """The lower (uncongested) density that carries a specific flow fs. Solves a D^2 - D + fs/k = 0."""
    disc = 1.0 - 4.0 * A_COEF * fs / k
    if fs < 0 or disc < -1e-12:
        raise ValueError("this specific flow is above the maximum; a queue must form")
    if fs <= 0.85 * k * D_MIN:          # thin crowd: everyone walks at the free speed
        return fs / (0.85 * k)
    return (1.0 - np.sqrt(max(disc, 0.0))) / (2.0 * A_COEF)


# %% [markdown]
# ## Step 3: stairs and effective widths
# On a stair people step down one tread at a time, so they are slower. k depends on the steps:
# for the common 178 mm riser and 279 mm tread, k = 1.08 m/s (speed measured along the slope),
# so Fs_max = 1.08 / 1.064 = 1.01 persons/(s m). Each kind of passage also loses an edge
# strip on both sides: 0.15 m for doors and stair walls, 0.20 m for corridor walls.

# %%
def stair_k(riser, tread):
    """Constant k (m/s) for a stair with the given riser and tread (m), from the table."""
    key = min(STAIR_K, key=lambda rt: abs(rt[0] - riser) + abs(rt[1] - tread))
    if abs(key[0] - riser) + abs(key[1] - tread) > 0.02:
        raise ValueError("this step size is not in the table")
    return STAIR_K[key]


def effective_width(clear_width, kind="door"):
    """Clear width minus the edge strip on both sides (m)."""
    we = clear_width - 2.0 * EDGE[kind]
    if we <= 0:
        raise ValueError("the passage is narrower than its two edge strips")
    return we


def max_flow(clear_width, kind="door", k=K_LEVEL):
    """Largest flow (persons/s) a passage can carry: Fs_max x effective width."""
    return max_specific_flow(k) * effective_width(clear_width, kind)


# %% [markdown]
# ## Step 4: conservation of flow at a transition
# People are not created or lost where a corridor meets a door. So the flow in equals the
# flow out:
#
#     Fs_in x We_in = Fs_out x We_out
#
# If the Fs_out this asks for is above Fs_max of the narrower passage, it cannot be carried:
# a **queue** forms in front of it. The passage then runs at its maximum flow, and the queue
# grows at (flow in - maximum flow out) persons per second.

# %%
def transition(flow_in, clear_out, kind_out="door", k_out=K_LEVEL):
    """Flow arriving at a narrower (or wider) passage. Returns a dict with the flow that gets
    through (persons/s), the queue growth rate (persons/s) and the density after it."""
    if flow_in < 0:
        raise ValueError("flow cannot be negative")
    cap = max_flow(clear_out, kind_out, k_out)
    out = min(flow_in, cap)
    fs_out = out / effective_width(clear_out, kind_out)
    return {"flow_out": out, "queue_rate": flow_in - out, "fs_out": fs_out,
            "density_out": density_for_flow(fs_out, k_out), "queue": flow_in > cap + 1e-12}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    ks = stair_k(0.178, 0.279)
    print(f"optimal density {optimal_density():.2f} persons/m2")
    print(f"max specific flow: level {max_specific_flow():.3f}, stair {max_specific_flow(ks):.3f} persons/(s m)")

    # Figure 1: speed and flow against density, level and stair
    d = np.linspace(0, D_JAM, 400)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    for k, name, col in [(K_LEVEL, "corridor / door (k = 1.40)", "#1f6feb"), (ks, "stair 178/279 mm (k = 1.08)", "#d9534f")]:
        a1.plot(d, speed(d, k), color=col, lw=2, label=name)
        a2.plot(d, specific_flow(d, k), color=col, lw=2, label=name)
        a2.plot(optimal_density(), max_specific_flow(k), "o", color=col)
        a2.annotate(f"max {max_specific_flow(k):.2f}", (optimal_density(), max_specific_flow(k)),
                    textcoords="offset points", xytext=(8, 6), fontsize=9)
    a1.set_xlabel("density D (persons/m2)")
    a1.set_ylabel("walking speed v (m/s)")
    a1.set_title("speed falls as the crowd gets denser")
    a2.set_xlabel("density D (persons/m2)")
    a2.set_ylabel("specific flow Fs (persons/(s m))")
    a2.set_title("flow = density x speed has a maximum")
    a2.axvline(optimal_density(), color="k", ls=":", lw=1)
    for a in (a1, a2):
        a.grid(alpha=0.3)
        a.legend(fontsize=8)
        a.set_xlim(0, 4)
    fig.tight_layout()
    fig.savefig(OUT / "fundamental_diagram.png", dpi=120)

    # Figure 2: the worked example: a 2 m corridor at D = 1.0 feeding a 1.2 m door
    d_in = 1.0
    f_in = specific_flow(d_in) * effective_width(2.0, "corridor")
    tr = transition(f_in, 1.2, "door")
    print(f"corridor: v = {speed(d_in):.3f} m/s, Fs = {specific_flow(d_in):.3f}, flow in {f_in:.3f} persons/s")
    print(f"door: max flow {max_flow(1.2):.3f}, queue grows at {tr['queue_rate']:.3f} persons/s")
    widths = np.linspace(0.8, 2.4, 161)
    flows = [transition(f_in, w)["flow_out"] for w in widths]
    rates = [transition(f_in, w)["queue_rate"] for w in widths]
    fig2, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.plot(widths, flows, color="#2a9d8f", lw=2, label="flow through the door")
    ax.plot(widths, rates, color="#d9534f", lw=2, label="queue growth rate")
    ax.axhline(f_in, color="k", ls="--", lw=1)
    ax.text(0.82, f_in + 0.04, f"flow arriving {f_in:.2f} persons/s", fontsize=8)
    w_ok = f_in / max_specific_flow() + 2 * EDGE["door"]
    ax.axvline(w_ok, color="0.4", ls=":")
    ax.text(w_ok + 0.03, 0.2, f"no queue above {w_ok:.2f} m", fontsize=8)
    ax.set_xlabel("clear width of the door (m)")
    ax.set_ylabel("persons per second")
    ax.set_title("2 m corridor at 1.0 persons/m2 meets a door")
    ax.set_ylim(0, 2.0)
    ax.legend(fontsize=8, loc="center right")
    ax.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "bottleneck.png", dpi=120)

# %% [markdown]
# ## Where this stops
# A real building is a network: rooms feed corridors, corridors feed stair doors, every floor
# pours into the same stair. Session 3 links these pieces into a step-by-step simulation,
# validates it against Sessions 1 and 2, and uses it to plan a safe evacuation.
