"""Session 1 (Level 1): a message is cut into packets that hop from router to router.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: packets and hops
# **A. Real-world problem.** When you open a web page, the server does not send it as one
# piece. The page is cut into many small *packets*. Each packet is labelled with where it is
# going, and routers pass it on from one to the next, like post offices passing a parcel. The
# packets may even arrive in the wrong order, so they carry a number.
#
# **Plan.** (1) cut a message into numbered packets and put it back together, (2) follow one
# route hop by hop, (3) count how many time steps a whole message needs, (4) see why very
# small and very large packets are both slow.

# %%
import math
import pathlib
import random

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

HEADER_BYTES = 40        # label added to every packet (a typical size for the address labels)
LINK_RATE = 1_000_000    # bits per second on every link in this session (slow, to see the effect)


# %% [markdown]
# ## Step 1: cut a message into numbered packets
# A packet is a piece of the message (the *payload*) plus a sequence number. The number lets
# the receiver sort the pieces even if they arrive in a different order.

# %%
def packetize(message, size):
    """Cut `message` (bytes) into [(sequence number, payload)] with payloads of at most `size` bytes."""
    if size <= 0:
        raise ValueError("packet size must be positive")
    return [(i, message[k:k + size]) for i, k in enumerate(range(0, len(message), size))]


def reassemble(packets):
    """Put packets back in order of their sequence number and join the payloads."""
    return b"".join(data for _, data in sorted(packets))


def packet_count(message_bytes, size):
    """How many packets a message of `message_bytes` needs: round up."""
    return math.ceil(message_bytes / size)


# %% [markdown]
# ## Step 2: routers pass packets hop by hop
# Each router knows only the *next hop* for each destination. No router knows the whole path.
# Following the next hops one after another gives the route.

# %%
NEXT_HOP = {
    "laptop": {"server": "home router"},
    "home router": {"server": "ISP router"},
    "ISP router": {"server": "backbone router"},
    "backbone router": {"server": "data-centre router"},
    "data-centre router": {"server": "server"},
}


def follow_route(tables, source, destination):
    """List of nodes from source to destination, found by asking each node for its next hop."""
    path = [source]
    while path[-1] != destination:
        nxt = tables[path[-1]][destination]
        if nxt in path:
            raise RuntimeError("routing loop at " + nxt)
        path.append(nxt)
    return path


# %% [markdown]
# ## Step 3: how many time steps does the whole message need?
# One *step* is the time one packet needs to cross one link. A link carries one packet at a
# time, and a router can only pass on a packet after it has fully received it. So the packets
# follow each other like cars on a road: the first packet needs `hops` steps, and each of the
# other packets arrives one step after the previous one.
#
#     steps = hops + packets - 1

# %%
def journey_steps(n_packets, hops):
    """Simulate the journey step by step and return the steps until all packets have arrived."""
    queue = [0] * (hops + 1)          # queue[i] = packets waiting at node i (node 0 = sender)
    queue[0] = n_packets
    steps = 0
    while queue[hops] < n_packets:
        movers = [i for i in range(hops) if queue[i] > 0]   # each link moves one packet per step
        for i in movers:
            queue[i] -= 1
            queue[i + 1] += 1
        steps += 1
    return steps


def delivery_time_ms(message_bytes, size, hops):
    """Time for the whole message: steps times the time one packet needs to cross one link."""
    n = packet_count(message_bytes, size)
    step_seconds = (size + HEADER_BYTES) * 8 / LINK_RATE
    return 1000 * (hops + n - 1) * step_seconds


# %% [markdown]
# ## Step 4: see it
# Left: the six nodes of a journey with the packets of a 4-packet message, one picture per time
# step. Right: the delivery time against packet size for a 1000 byte message over 5 hops. Tiny
# packets waste time on labels and need many steps; huge packets make every step long.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    msg = bytes(range(256)) * 4 + bytes(range(232))     # 1256 bytes of test data
    pk = packetize(msg, 300)
    shuffled = pk[:]
    random.Random(1).shuffle(shuffled)
    print("packets:", [(i, len(d)) for i, d in pk], "-> rebuilt equals original:", reassemble(shuffled) == msg)
    route = follow_route(NEXT_HOP, "laptop", "server")
    print("route:", " -> ".join(route))
    print("4 packets over 3 hops need", journey_steps(4, 3), "steps")

    fig, axs = plt.subplots(2, 3, figsize=(10, 4.2), sharex=True, sharey=True)
    hops, n = 5, 4
    for ax, step in zip(axs.ravel(), range(6)):
        for i in range(hops + 1):
            ax.plot(i, 0, "s", color="tab:gray", ms=10)
        ax.set_title(f"after step {step}", fontsize=9)
        for k in range(n):
            pos = min(max(step - k, 0), hops)      # packet k leaves one step after packet k-1
            ax.plot(pos, 0.15 + 0.12 * k, "o", color="tab:blue")
        ax.set_ylim(-0.2, 0.8)
        ax.set_yticks([])
        ax.set_xticks(range(hops + 1))
    for ax in axs[1]:
        ax.set_xlabel("node number (0 = laptop, 5 = server)")
    fig.suptitle("Four packets move forward like cars on a road (dots = packets)")
    fig.tight_layout()
    fig.savefig(OUT / "packet_journey.png", dpi=120)

    sizes = np.arange(20, 1001, 10)
    times = [delivery_time_ms(1000, int(s), 5) for s in sizes]
    best = int(sizes[int(np.argmin(times))])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(sizes, times)
    ax2.plot(best, min(times), "ro")
    ax2.set_xlabel("payload size per packet (bytes)")
    ax2.set_ylabel("delivery time of the whole message (ms)")
    ax2.set_title(f"1000 byte message, 5 hops: best size about {best} bytes")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "time_vs_packet_size.png", dpi=120)
    print("best payload size", best, "bytes ->", round(min(times), 2), "ms")
    print("one big packet:", round(delivery_time_ms(1000, 1000, 5), 2), "ms;  20 byte packets:",
          round(delivery_time_ms(1000, 20, 5), 2), "ms")

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
