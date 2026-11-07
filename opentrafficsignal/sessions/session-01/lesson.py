"""Session 1 (Level 1): two phases, one queue.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: two phases, one queue
# **A. Real-world problem.** At a four-way junction two roads cross. Only one road may drive
# at a time, so the signal alternates: green, amber, red. While one road waits, its cars pile
# up in a queue. How long does that queue get, and how long does it take to disappear?
#
# **Plan.** (1) write the signal plan, (2) let cars arrive at a steady rate and leave only on
# green, (3) record the queue length against time, (4) check the result by hand:
# peak queue = arrival rate x red time.
#
# *This is a simplified educational model, not a traffic engineering tool.*

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

S_SAT = 0.5      # saturation flow: cars per second that can leave a queue on green (typical value, one lane)
AMBER = 3.0      # amber time in seconds; in this model cars do not leave on amber (lost time)


# %% [markdown]
# ## Step 1: the signal plan
# Two roads, A and B, share the junction. Each gets a green of `g` seconds, then amber, and
# the other road goes. The whole pattern repeats every cycle time `C = 2 (g + amber)`.
# Road B runs half a cycle behind road A.

# %%
def cycle_time(g, amber=AMBER):
    """Cycle time C in seconds for two equal phases."""
    return 2.0 * (g + amber)


def signal_state(t, g, amber=AMBER, offset=0.0):
    """'green', 'amber' or 'red' for one road at time t (seconds). offset shifts the road in time."""
    tau = (t + offset) % cycle_time(g, amber)
    if tau < g:
        return "green"
    if tau < g + amber:
        return "amber"
    return "red"


# %% [markdown]
# ## Step 2: cars arrive, cars leave
# Cars arrive at a steady rate `q` (cars per second). On green, up to `S_SAT` cars per second
# leave, but never more than are waiting. On amber and red nobody leaves. We step through
# time in small steps of `dt` seconds and keep the queue length (a fractional number of cars
# is fine for this first model).

# %%
def queue_history(q, g, T=600.0, dt=0.1, s=S_SAT, amber=AMBER, offset=0.0):
    """Queue length (cars) against time for one road. Returns (times, queue)."""
    n = int(round(T / dt))
    t = np.arange(n + 1) * dt
    queue = np.zeros(n + 1)
    for k in range(n):
        waiting = queue[k] + q * dt
        if signal_state(t[k], g, amber, offset) == "green":
            waiting = max(0.0, waiting - s * dt)
        queue[k + 1] = waiting
    return t, queue


# %% [markdown]
# ## Step 3: predict the queue by hand
# The road is not green for `r = C - g` seconds (amber plus the other road's green plus amber).
# During that time `q r` cars arrive and none leave, so the peak queue is `q r`.
# On green the queue shrinks at the speed `s - q` (cars leave at `s`, new ones arrive at `q`),
# so it needs `q r / (s - q)` seconds to disappear. That only works if it vanishes before the
# green ends, i.e. if the arrival rate is below the capacity `s g / C` of the road.

# %%
def red_time(g, amber=AMBER):
    return cycle_time(g, amber) - g


def peak_queue_theory(q, g, amber=AMBER):
    """Cars waiting at the end of red, q * r."""
    return q * red_time(g, amber)


def clear_time_theory(q, g, s=S_SAT, amber=AMBER):
    """Seconds of green needed to empty the queue, or None if the road cannot cope."""
    if q >= s:
        return None
    t = peak_queue_theory(q, g, amber) / (s - q)
    return t if t <= g + 1e-9 else None


def capacity(g, s=S_SAT, amber=AMBER):
    """Largest steady arrival rate (cars per second) a road can handle: s g / C."""
    return s * g / cycle_time(g, amber)


# %% [markdown]
# ## Step 4: see it
# Left: the queue against time for 3 cycles. It climbs during red and drains during green.
# Right: what happens to the peak queue as the arrival rate grows, with the same signal.
# When the arrival rate passes the capacity, the queue never empties.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    q, g = 0.15, 27.0
    C = cycle_time(g)
    t, qu = queue_history(q, g, T=3 * C)
    print(f"cycle time C = {C:.0f} s, red time r = {red_time(g):.0f} s")
    print(f"peak queue: theory {peak_queue_theory(q, g):.2f} cars, simulated {qu[: int(C / 0.1)].max():.2f} cars")
    print(f"time to clear: theory {clear_time_theory(q, g):.2f} s of green")
    print(f"capacity {capacity(g):.3f} cars/s against arrivals {q} cars/s")

    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.plot(t, qu, color="tab:blue", label="queue (cars)")
    for k in range(3):
        ax.axvspan(k * C, k * C + g, color="tab:green", alpha=0.15, label="green" if k == 0 else None)
        ax.axvspan(k * C + g, k * C + g + AMBER, color="gold", alpha=0.3, label="amber" if k == 0 else None)
    ax.axhline(peak_queue_theory(q, g), color="gray", ls=":", label="theory q r")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("queue length (cars)")
    ax.set_title("One road: queue rises on red, drains on green")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "queue_vs_time.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    rates = np.linspace(0.02, 0.26, 25)
    last = []
    for r_ in rates:
        _, qq = queue_history(r_, g, T=20 * C)
        last.append(qq[-int(C / 0.1):].max())
    ax2.plot(rates, last, "o-", ms=3, label="largest queue in the last cycle")
    ax2.axvline(capacity(g), color="tab:red", ls="--", label=f"capacity s g / C = {capacity(g):.3f}")
    ax2.set_xlabel("arrival rate q (cars per second)")
    ax2.set_ylabel("queue length (cars)")
    ax2.set_title("Past capacity the queue keeps growing")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "queue_vs_rate.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
