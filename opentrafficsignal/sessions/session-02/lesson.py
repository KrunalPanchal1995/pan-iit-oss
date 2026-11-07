"""Session 2 (Level 2): delay from cycle time, green split and flow.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: delay from cycle time, green split and flow
# **A. Real-world problem.** A junction has a main road (busy) and a side road (quiet). With a
# 60 second cycle, how many seconds of green should each get? Too little for the busy road and
# its queue never ends; too little for the side road and a few drivers wait a very long time.
# We turn the queue picture of Session 1 into a formula for the average delay per car.
#
# *This is a simplified educational model, not a traffic engineering tool. Real junction
# timing follows national guidance and measured data.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
S_SAT = 0.5       # saturation flow, cars per second per lane (a typical textbook value, about 1800 per hour)
LOST = 6.0        # total lost time per cycle in seconds (two phases x 3 s amber)


# %% [markdown]
# ## Step 1: the quantities
# * `C` cycle time (s), `g` effective green time of one approach (s), `r = C - g` its effective red.
# * `q` arrival rate (cars/s), `s` saturation flow (cars/s while the queue is discharging).
# * flow ratio `y = q / s` (how much of the time the road would need to be discharging).
# * green ratio `lam = g / C`, capacity `s lam`, and the degree of saturation `x = q / (s lam)`.
# `x < 1` means the queue clears every cycle; `x > 1` means it never does.

# %%
def green_ratio(C, g):
    return g / C


def flow_ratio(q, s=S_SAT):
    return q / s


def degree_of_saturation(C, g, q, s=S_SAT):
    """x = q / (s g / C). Above 1 the approach is oversaturated."""
    return q * C / (g * s)


# %% [markdown]
# ## Step 2: the average delay of the deterministic queue
# Cars arrive evenly at `q`; nobody leaves for `r` seconds, then the queue drains at `s - q`.
# Plot cumulative arrivals and departures: the area between them is the total waiting time per
# cycle. It is a triangle with height `q r` (the peak queue) and base `r s / (s - q)` (the time
# until the queue is gone), so its area is `q r^2 s / (2 (s - q))`. Divide by the `q C` cars that
# pass in one cycle and you get Webster's uniform delay term:
#
#     d = C (1 - g/C)^2 / (2 (1 - q/s))      (seconds per car)
#
# Assumptions: even arrivals, constant saturation flow while a queue exists, a queue that
# clears each cycle (x <= 1), no random surges (the random term is added in practice).

# %%
def uniform_delay(C, g, q, s=S_SAT):
    """Webster uniform delay in seconds per car; infinity if x > 1 (the queue never clears)."""
    if g <= 0:
        return float("inf")
    if degree_of_saturation(C, g, q, s) > 1.0 + 1e-12:
        return float("inf")
    return C * (1.0 - g / C) ** 2 / (2.0 * (1.0 - q / s))


# %% [markdown]
# ## Step 3: two approaches share one cycle
# The effective green of the whole cycle is `C - LOST`. Giving more to approach 1 takes it from
# approach 2. The quantity to minimise is the total delay rate `q1 d1 + q2 d2` (car-seconds of
# waiting per second, which is also the average number of delayed cars). Dividing by `q1 + q2`
# gives the average delay per car.

# %%
def total_delay_rate(C, g1, q1, q2, s=S_SAT, lost=LOST):
    """q1 d1 + q2 d2 for the split g1 and g2 = C - lost - g1 (car-seconds per second)."""
    g2 = C - lost - g1
    return q1 * uniform_delay(C, g1, q1, s) + q2 * uniform_delay(C, g2, q2, s)


def average_delay(C, g1, q1, q2, s=S_SAT, lost=LOST):
    """Average delay per car over both approaches, in seconds."""
    return total_delay_rate(C, g1, q1, q2, s, lost) / (q1 + q2)


def best_split(C, q1, q2, s=S_SAT, lost=LOST, xmax=1.0, step=0.01):
    """Green g1 (s) that minimises total delay with both degrees of saturation <= xmax."""
    best, best_val = None, float("inf")
    for g1 in np.arange(step, C - lost, step):
        if degree_of_saturation(C, g1, q1, s) > xmax or degree_of_saturation(C, C - lost - g1, q2, s) > xmax:
            continue
        v = total_delay_rate(C, g1, q1, q2, s, lost)
        if v < best_val:
            best, best_val = float(g1), v
    return best


def proportional_split(C, q1, q2, s=S_SAT, lost=LOST):
    """Webster's rule of thumb: effective green shared in proportion to the flow ratios."""
    y1, y2 = q1 / s, q2 / s
    return (C - lost) * y1 / (y1 + y2)


def webster_cycle(Y, lost=LOST):
    """Webster's classic optimum cycle C = (1.5 L + 5) / (1 - Y), Y = sum of critical flow ratios."""
    if Y >= 1.0:
        return float("inf")
    return (1.5 * lost + 5.0) / (1.0 - Y)


# %% [markdown]
# ## Step 4: see it
# Left: the average delay of one approach against its degree of saturation. It rises slowly and
# then steeply. Right: total delay against the green given to the busy road. The minimum of the
# formula sits at the very edge `x = 1` of the quiet road, which is risky, so a designer adds a
# limit such as `x <= 0.9`.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    C, q1, q2 = 60.0, 0.20, 0.10
    print(f"worked example: C=60, g=27, q=0.20 -> x={degree_of_saturation(C, 27, 0.2):.3f}, d={uniform_delay(C, 27, 0.2):.3f} s")
    print(f"                C=60, g=27, q=0.10 -> x={degree_of_saturation(C, 27, 0.1):.3f}, d={uniform_delay(C, 27, 0.1):.3f} s")
    print(f"equal split 27/27: average delay {average_delay(C, 27, q1, q2):.2f} s")
    for xmax in (1.0, 0.9):
        g1 = best_split(C, q1, q2, xmax=xmax)
        print(f"best split with x <= {xmax}: g1={g1:.2f} s, g2={C - LOST - g1:.2f} s, "
              f"average delay {average_delay(C, g1, q1, q2):.2f} s")
    gp = proportional_split(C, q1, q2)
    print(f"proportional split: g1={gp:.2f} s, average delay {average_delay(C, gp, q1, q2):.2f} s")
    Y = (q1 + q2) / S_SAT
    print(f"Webster cycle for Y={Y:.2f}, L={LOST:.0f} s: {webster_cycle(Y):.1f} s")

    fig, ax = plt.subplots(figsize=(6, 4))
    g = 27.0
    qs = np.linspace(0.0, S_SAT * g / C, 80)
    ax.plot([degree_of_saturation(C, g, q) for q in qs], [uniform_delay(C, g, q) for q in qs])
    ax.set_xlabel("degree of saturation x (no unit)")
    ax.set_ylabel("uniform delay d (s per car)")
    ax.set_title("Delay rises as the road fills up (C = 60 s, g = 27 s)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "delay_vs_saturation.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    g1s = np.linspace(24.0, 42.0, 181)
    ax2.plot(g1s, [average_delay(C, x, q1, q2) for x in g1s], label="average delay per car")
    g90 = best_split(C, q1, q2, xmax=0.9)
    ax2.axvline(g90, color="tab:green", ls="--", label=f"best with x <= 0.9: g1 = {g90:.1f} s")
    ax2.axvline(proportional_split(C, q1, q2), color="gray", ls=":", label="proportional to flow")
    ax2.set_xlabel("green time g1 of the busy road (s)")
    ax2.set_ylabel("average delay (s per car)")
    ax2.set_title("Splitting 54 s of green between two roads")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "delay_vs_split.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
