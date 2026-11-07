"""Session 1 (Level 1): a neuron adds up signals and fires an all-or-nothing spike.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a neuron adds up signals and fires
# **A. Real-world problem.** Your nerve cells talk with brief electrical pulses called
# *spikes*. A neuron collects signals from other cells on its branches (dendrites), adds
# them up in its cell body, and, if the total voltage crosses a threshold, fires one spike
# that runs down its long wire (the axon) to the next cells. A weak input does nothing; a
# strong input does not make a bigger spike, only more of them. Today you build the simplest
# model of that idea and draw its voltage-versus-time trace.
#
# **Plan.** (1) a voltage that rises with input and leaks away, (2) a threshold that fires a
# fixed-size spike, (3) how long the spike takes to travel down an axon.
#
# *General education only. This is a simplified model, not medical information.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

V_REST = -70.0     # resting voltage, mV (a typical textbook value)
V_THRESH = -55.0   # threshold voltage, mV (typical)
V_SPIKE = 40.0     # the drawn height of a spike, mV (every spike has the same height)
LEAK = 0.1         # fraction of the distance back to rest that leaks away each millisecond
REFRACTORY = 2     # milliseconds after a spike during which the neuron cannot fire again


# %% [markdown]
# ## Step 1: a voltage that rises with input and leaks away
# Time moves in steps of 1 ms. Each step the input pushes the voltage up by `drive` (mV),
# and the leak pulls it back towards rest:
#
#     V_new = V + drive - LEAK * (V - V_rest)
#
# If the drive is constant the voltage climbs towards V_rest + drive / LEAK and stops there.
# That final level must be above the threshold for the neuron ever to fire, so the smallest
# drive that can fire is  drive_min = LEAK * (V_thresh - V_rest) = 0.1 * 15 = 1.5 mV per ms.

# %%
def final_level(drive):
    """Voltage (mV) the neuron would settle at if it never fired."""
    return V_REST + drive / LEAK


def smallest_drive():
    """Smallest constant drive (mV per ms) that can ever reach the threshold."""
    return LEAK * (V_THRESH - V_REST)


def steps_to_first_spike(drive):
    """Hand calculation: number of 1 ms steps until V reaches the threshold (None if never)."""
    if final_level(drive) <= V_THRESH:
        return None
    need = (V_THRESH - V_REST) * LEAK / drive          # (1 - LEAK)^n must fall to 1 - need
    return int(np.ceil(np.log(1.0 - need) / np.log(1.0 - LEAK) - 1e-9))


# %% [markdown]
# ## Step 2: the threshold and the spike
# When V reaches the threshold the neuron fires: we draw a spike of fixed height, reset V to
# rest, and block firing for a short refractory time. The spike height never depends on how
# strong the input was: *all or nothing*.

# %%
def toy_neuron(drive, steps=100):
    """Simulate `steps` milliseconds. Returns (voltage trace in mV, list of spike times in ms).
    `drive` is a number (constant) or an array with one value per step."""
    drive = np.broadcast_to(np.asarray(drive, dtype=float), (steps,))
    v = V_REST
    wait = 0
    trace = []
    spikes = []
    for n in range(steps):
        if wait > 0:
            wait -= 1
            v = V_REST
            trace.append(V_REST)
            continue
        v = v + drive[n] - LEAK * (v - V_REST)
        if v >= V_THRESH:
            spikes.append(n + 1)
            trace.append(V_SPIKE)
            v = V_REST
            wait = REFRACTORY
        else:
            trace.append(v)
    return np.array(trace), spikes


# %% [markdown]
# ## Step 3: the spike travels down the axon
# A spike moves along the axon at a roughly constant speed, so the delay is
# `delay = length / speed`. Typical speeds range from about 1 m/s in thin unmyelinated fibres
# to over 100 m/s in thick myelinated ones.

# %%
def travel_time_ms(length_m, speed_m_per_s):
    return 1000.0 * length_m / speed_m_per_s


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    OUT.mkdir(exist_ok=True)
    print("smallest drive that can fire:", smallest_drive(), "mV per ms")
    for d in (1.0, 1.5, 2.0, 3.0):
        tr, sp = toy_neuron(d)
        print(f"drive {d}: {len(sp)} spikes in 100 ms, first at {sp[0] if sp else None} ms,"
              f" hand calculation {steps_to_first_spike(d)}, highest value {tr.max():.1f} mV")

    # picture of a neuron
    fig, ax = plt.subplots(figsize=(8, 3))
    for ang, ln in ((140, 1.6), (180, 1.8), (220, 1.6)):
        a = np.radians(ang)
        ax.plot([0, ln * np.cos(a)], [0, ln * np.sin(a)], color="#2a9d8f", lw=3)
    ax.add_patch(Circle((0, 0), 0.5, color="#f4a261"))
    ax.plot([0.5, 9.5], [0, 0], color="#264653", lw=2.5)
    ax.annotate("dendrites\n(collect signals)", (-1.6, 0.9), ha="center")
    ax.annotate("cell body\n(adds them up)", (0, 0.65), ha="center")
    ax.annotate("axon (carries the spike)", (5, 0.25), ha="center")
    ax.annotate("to next cells", (9.5, -0.5), ha="center")
    ax.set_xlim(-3, 10.5)
    ax.set_ylim(-1.4, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "neuron_picture.png", dpi=120)

    # voltage traces
    fig2, axs = plt.subplots(3, 1, figsize=(7, 6.5), sharex=True)
    for ax2, d in zip(axs, (1.0, 2.0, 4.0)):
        tr, sp = toy_neuron(d)
        ax2.plot(np.arange(1, 101), tr)
        ax2.axhline(V_THRESH, color="red", ls="--", lw=1)
        ax2.set_ylabel("voltage (mV)")
        ax2.set_title(f"drive {d} mV per ms: {len(sp)} spikes", fontsize=9)
        ax2.grid(alpha=0.3)
    axs[0].text(60, V_THRESH + 3, "threshold", color="red", fontsize=8)
    axs[-1].set_xlabel("time (ms)")
    fig2.tight_layout()
    fig2.savefig(OUT / "voltage_traces.png", dpi=120)
    print("delay for 0.5 m at 50 m/s:", travel_time_ms(0.5, 50.0), "ms")
