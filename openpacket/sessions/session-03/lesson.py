"""Session 3 (Level 3): a tiny network simulator, validated against the delay formulas.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a network in a computer
# **A. Real-world problem.** Real networks are too big and too fast to watch. So we build a
# toy one: routers are points on a graph, links have a delay and a bandwidth, and packets move
# hop by hop through queues. Nothing here touches a real network: no sockets, only arithmetic.
# The point is to check our simulator against the formulas of Session 2, and then to break
# the network on purpose (full buffers, a cut link, a routing loop) and watch what happens.
#
# **Plan.** (1) Dijkstra's shortest-path algorithm builds routing tables, (2) an event-driven
# simulator forwards packets through finite queues, (3) measured delay is compared with
# propagation + transmission + queueing, (4) loss and retransmission: stop-and-wait and
# window protocols, (5) a link failure and re-routing, (6) failure cases, (7) a simplified
# additive-increase multiplicative-decrease (AIMD) sawtooth, (8) a video link mini-project.

# %%
import heapq
import itertools
import math
import pathlib
import random
from collections import Counter, deque

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: Dijkstra builds the routing tables
# `graph[u][v]` is the cost of the link from u to v. Dijkstra keeps a priority queue of the
# cheapest known way to reach each node and always expands the cheapest one next. Each router
# then keeps only the *next hop* for every destination.

# %%
def dijkstra(graph, source):
    """Return (dist, prev): cheapest cost to every node and the node before it on that path."""
    dist = {source: 0.0}
    prev = {}
    heap = [(0.0, source)]
    done = set()
    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for v, cost in graph.get(u, {}).items():
            nd = d + cost
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, prev


def routing_tables(graph):
    """{router: {destination: next hop}} from Dijkstra run at every router."""
    tables = {}
    for src in graph:
        _, prev = dijkstra(graph, src)
        row = {}
        for dst in prev:
            hop = dst
            while prev[hop] != src:
                hop = prev[hop]
            row[dst] = hop
        tables[src] = row
    return tables


# %% [markdown]
# ## Step 2: the simulator
# Time jumps from event to event (a packet arrives, a transmission ends). Each directed link has
# a *transmitter* that sends one packet at a time (`bits / rate` seconds), a *queue* of waiting
# packets of finite length `buffer` (a packet that finds it full is dropped), and a *wire delay*.
# Every packet is counted: sent = delivered + dropped + in flight.

# %%
class Packet:
    __slots__ = ("pid", "src", "dst", "bits", "t_sent", "ttl", "kind", "seq")

    def __init__(self, pid, src, dst, bits, t_sent, ttl, kind, seq):
        self.pid, self.src, self.dst, self.bits = pid, src, dst, bits
        self.t_sent, self.ttl, self.kind, self.seq = t_sent, ttl, kind, seq


class Link:
    def __init__(self, u, v, delay, rate, buffer, loss):
        self.u, self.v, self.delay, self.rate, self.buffer, self.loss = u, v, delay, rate, buffer, loss
        self.up = True
        self.queue = deque()
        self.current = None          # the packet being transmitted
        self.carried = 0             # packets that finished transmission on this link


class Network:
    def __init__(self, seed=0):
        self.links = {}
        self.tables = {}
        self.now = 0.0
        self.events = []
        self.counter = itertools.count()
        self.pids = itertools.count()
        self.rng = random.Random(seed)
        self.sent = 0
        self.delivered = []          # (packet, arrival time)
        self.dropped = Counter()     # reason -> number of packets
        self.live = set()            # ids of packets that exist and are not yet delivered or dropped
        self.on_deliver = {}         # node -> function(packet), used by the protocols below

    # ---- building the network
    def add_link(self, u, v, delay, rate, buffer=50, loss=0.0):
        """Add a two-way link: delay in seconds, rate in bit/s, buffer = packets that may wait."""
        self.links[(u, v)] = Link(u, v, delay, rate, buffer, loss)
        self.links[(v, u)] = Link(v, u, delay, rate, buffer, 0.0)

    def cost_graph(self, ref_bits=12000):
        """Link costs for Dijkstra: the delay a packet of `ref_bits` would see on an empty link."""
        g = {}
        for (u, v), lk in self.links.items():
            g.setdefault(u, {})
            g.setdefault(v, {})
            if lk.up:
                g[u][v] = lk.delay + ref_bits / lk.rate
        return g

    def recompute_routes(self):
        self.tables = routing_tables(self.cost_graph())

    # ---- the clock
    def schedule(self, t, fn, *args):
        heapq.heappush(self.events, (t, next(self.counter), fn, args))

    def run(self, until=math.inf):
        while self.events and self.events[0][0] <= until:
            t, _, fn, args = heapq.heappop(self.events)
            self.now = t
            fn(*args)
        if until != math.inf:
            self.now = until

    # ---- packets
    def inject(self, t, src, dst, bits, ttl=64, kind="data", seq=0):
        """Create a packet at time t at node src."""
        self.schedule(t, self.originate, src, dst, bits, ttl, kind, seq)

    def originate(self, src, dst, bits, ttl=64, kind="data", seq=0):
        pkt = Packet(next(self.pids), src, dst, bits, self.now, ttl, kind, seq)
        self.sent += 1
        self.live.add(pkt.pid)
        self.arrive(pkt, src)

    def drop(self, pkt, reason):
        self.dropped[reason] += 1
        self.live.discard(pkt.pid)

    def arrive(self, pkt, node):
        if node == pkt.dst:
            self.delivered.append((pkt, self.now))
            self.live.discard(pkt.pid)
            if node in self.on_deliver:
                self.on_deliver[node](pkt)
            return
        if pkt.ttl <= 0:
            return self.drop(pkt, "ttl")
        nxt = self.tables.get(node, {}).get(pkt.dst)
        if nxt is None:
            return self.drop(pkt, "no_route")
        link = self.links.get((node, nxt))
        if link is None or not link.up:
            return self.drop(pkt, "link_down")
        pkt.ttl -= 1
        if link.current is None:
            self.start_tx(link, pkt)
        elif len(link.queue) >= link.buffer:
            self.drop(pkt, "buffer")
        else:
            link.queue.append(pkt)

    def start_tx(self, link, pkt):
        link.current = pkt
        self.schedule(self.now + pkt.bits / link.rate, self.tx_done, link)

    def tx_done(self, link):
        pkt, link.current = link.current, None
        link.carried += 1
        if link.queue:
            self.start_tx(link, link.queue.popleft())
        if not link.up:
            self.drop(pkt, "link_down")
        elif link.loss > 0 and self.rng.random() < link.loss:
            self.drop(pkt, "loss")
        else:
            self.schedule(self.now + link.delay, self.arrive, pkt, link.v)

    # ---- failures
    def fail_link(self, t, u, v, detect_after):
        """At time t the link u-v breaks; routers learn of it (tables recomputed) detect_after seconds later."""
        self.schedule(t, self._break, u, v)
        self.schedule(t + detect_after, self.recompute_routes)

    def _break(self, u, v):
        for key in ((u, v), (v, u)):
            lk = self.links[key]
            lk.up = False
            while lk.queue:
                self.drop(lk.queue.popleft(), "link_down")

    # ---- bookkeeping
    def in_flight_count(self):
        """Count packets directly: in transmitters, in queues and travelling on wires."""
        n = sum(len(lk.queue) + (1 if lk.current is not None else 0) for lk in self.links.values())
        n += sum(1 for ev in self.events if ev[2] == self.arrive)
        return n

    def totals(self):
        return {"sent": self.sent, "delivered": len(self.delivered), "dropped": sum(self.dropped.values()),
                "in_flight": self.in_flight_count()}

    def conserved(self):
        t = self.totals()
        return t["sent"] == t["delivered"] + t["dropped"] + t["in_flight"] and len(self.live) == t["in_flight"]

    def delays(self, kind="data"):
        return [t - p.t_sent for p, t in self.delivered if p.kind == kind]


def path_delay(net, path, bits):
    """Analytic delay of one packet on an empty path: sum of transmission + propagation on each link."""
    return sum(bits / net.links[(a, b)].rate + net.links[(a, b)].delay for a, b in zip(path, path[1:]))


def burst_last_delay(net, path, bits, n):
    """Analytic delay of the last of n packets sent at the same instant (store and forward)."""
    x = [bits / net.links[(a, b)].rate for a, b in zip(path, path[1:])]
    return sum(x) + (n - 1) * max(x) + sum(net.links[(a, b)].delay for a, b in zip(path, path[1:]))


def line_network(rates, delays, buffer=1000):
    """Nodes n0 - n1 - ... in a line with the given per-link rates (bit/s) and delays (s)."""
    net = Network()
    for i, (r, d) in enumerate(zip(rates, delays)):
        net.add_link(f"n{i}", f"n{i + 1}", d, r, buffer)
    net.recompute_routes()
    return net


# %% [markdown]
# ## Step 3: loss and retransmission (stop-and-wait and windows)
# A sender sends `window` packets and waits for acknowledgements (ACKs). If an ACK does not
# come back before the *timeout*, the packet is sent again. Window 1 is *stop-and-wait*.
#
# Define `x = L / R` (time to send one packet) and `RTT` = the time from the end of sending a
# packet to the arrival of its ACK = 2 * delay + ACK transmission time. Stop-and-wait sends one
# packet per `x + RTT`, so the fraction of time the link is busy is
#
#     U = x / (x + RTT)          and for a window W:   U = min(1, W * x / (x + RTT))

# %%
class Transfer:
    """Send n packets from src to dst with a sliding window and per-packet timeouts."""

    def __init__(self, net, src, dst, n, data_bits, window, timeout, ack_bits=400):
        self.net, self.src, self.dst, self.n = net, src, dst, n
        self.data_bits, self.window, self.timeout, self.ack_bits = data_bits, window, timeout, ack_bits
        self.attempt = [0] * n
        self.next_new = 0
        self.outstanding, self.acked, self.received = set(), set(), set()
        self.transmissions = 0
        self.done_time = None
        net.on_deliver[dst] = self._at_receiver
        net.on_deliver[src] = self._at_sender

    def start(self, t=0.0):
        self.net.schedule(t, self._fill)

    def _send(self, seq):
        self.attempt[seq] += 1
        self.transmissions += 1
        self.net.originate(self.src, self.dst, self.data_bits, 64, "data", seq)
        self.net.schedule(self.net.now + self.timeout, self._timeout, seq, self.attempt[seq])

    def _fill(self):
        while self.next_new < self.n and len(self.outstanding) < self.window:
            seq = self.next_new
            self.next_new += 1
            self.outstanding.add(seq)
            self._send(seq)

    def _timeout(self, seq, attempt):
        if seq in self.outstanding and self.attempt[seq] == attempt:
            self._send(seq)

    def _at_receiver(self, pkt):
        if pkt.kind == "data":
            self.received.add(pkt.seq)
            self.net.originate(self.dst, self.src, self.ack_bits, 64, "ack", pkt.seq)

    def _at_sender(self, pkt):
        if pkt.kind == "ack" and pkt.seq in self.outstanding:
            self.outstanding.discard(pkt.seq)
            self.acked.add(pkt.seq)
            if len(self.acked) == self.n:
                self.done_time = self.net.now
            else:
                self._fill()


def two_node_network(rate=10e6, delay=0.010, buffer=1000, loss=0.0, seed=0):
    net = Network(seed)
    net.add_link("S", "D", delay, rate, buffer, loss)
    net.recompute_routes()
    return net


def utilisation(n, data_bits, window, rate=10e6, delay=0.010, ack_bits=400, loss=0.0, timeout=1.0, seed=0):
    """Run a transfer and return (measured U, transfer, network). U = useful sending time / total time."""
    net = two_node_network(rate, delay, loss=loss, seed=seed)
    tr = Transfer(net, "S", "D", n, data_bits, window, timeout, ack_bits)
    tr.start()
    net.run()
    return n * data_bits / rate / tr.done_time, tr, net


def utilisation_formula(data_bits, window, rate=10e6, delay=0.010, ack_bits=400):
    x = data_bits / rate
    rtt = 2 * delay + ack_bits / rate
    return min(1.0, window * x / (x + rtt))


# %% [markdown]
# ## Step 4: a toy congestion window (a simplified illustration)
# Real TCP is far more complex. In this toy, once per round trip the sender sends `w` packets.
# The path can deliver `bdp` packets per round trip (the bandwidth-delay product) and a buffer
# holds `buffer` more; packets beyond `bdp + buffer` are lost. No loss: `w` grows by 1 (additive
# increase). Loss: `w` is halved (multiplicative decrease). The graph of `w` is a sawtooth.

# %%
def aimd(bdp, buffer, rounds, w0=1.0):
    """Return per-round arrays: window, delivered and dropped packets of the toy AIMD model."""
    w = float(w0)
    window, delivered, dropped = [], [], []
    capacity = bdp + buffer
    for _ in range(rounds):
        window.append(w)
        lost = max(0.0, w - capacity)
        delivered.append(w - lost)
        dropped.append(lost)
        w = max(1.0, w / 2) if lost > 0 else w + 1.0
    return np.array(window), np.array(delivered), np.array(dropped)


def aimd_utilisation(bdp, buffer, rounds=2000):
    """Fraction of the path's capacity (bdp packets per round trip) used, after the start-up."""
    w, _, _ = aimd(bdp, buffer, rounds)
    used = np.minimum(w, bdp)
    return float(used[rounds // 2:].mean() / bdp)


# %% [markdown]
# ## Step 5: failure cases
# * **Routing loop:** two routers each think the other is the way to the destination. The
#   packet ping-pongs until its *time to live* (TTL) runs out. Without TTL it would circle forever.
# * **Missing route:** a router has no row for the destination and must drop the packet.

# %%
def has_loop(tables, src, dst):
    seen = {src}
    node = src
    while node != dst:
        node = tables.get(node, {}).get(dst)
        if node is None:
            return False
        if node in seen:
            return True
        seen.add(node)
    return False


def diamond():
    """A - R1 - R2 - B (short, 5 ms links) and A - R3 - R4 - B (long, 10 ms links), all 10 Mbit/s."""
    net = Network()
    for a, b, d in (("A", "R1", 0.005), ("R1", "R2", 0.005), ("R2", "B", 0.005),
                    ("A", "R3", 0.010), ("R3", "R4", 0.010), ("R4", "B", 0.010)):
        net.add_link(a, b, d, 10e6, buffer=100)
    net.recompute_routes()
    return net


def reroute_experiment(fail_at=0.100, detect_after=0.050, interval=0.004, offset=0.001, end=0.4, bits=12000):
    """A steady flow A -> B; the link R1-R2 breaks at `fail_at`. Returns (network, send times)."""
    net = diamond()
    times = [offset + k * interval for k in range(int((end - offset) / interval))]
    for t in times:
        net.inject(t, "A", "B", bits)
    net.fail_link(fail_at, "R1", "R2", detect_after)
    net.run()
    return net, times


# %% [markdown]
# ## Step 6: mini-project, a video stream over one link
# A camera sends 25 frames per second. Each frame is 20000 bytes of payload that the sender cuts
# into packets (payload `P` bytes plus a 40 byte header) and hands to the link all at once. The
# link has rate 5 Mbit/s and 10 ms delay, and its router has a buffer of `B` waiting packets.

# %%
VIDEO = {"frame_bytes": 20000, "header": 40, "fps": 25, "rate": 5e6, "delay": 0.010, "frames": 60}


def video_trial(payload, buffer):
    """Simulate the stream; return (frames fully delivered, worst frame delay in s, packets dropped)."""
    v = VIDEO
    n = math.ceil(v["frame_bytes"] / payload)
    bits = (payload + v["header"]) * 8
    net = Network()
    net.add_link("cam", "viewer", v["delay"], v["rate"], buffer)
    net.recompute_routes()
    for f in range(v["frames"]):
        for _ in range(n):
            net.inject(f / v["fps"], "cam", "viewer", bits, seq=f)
    net.run()
    got = Counter(p.seq for p, _ in net.delivered)
    last = {}
    for p, t in net.delivered:
        last[p.seq] = max(last.get(p.seq, 0.0), t - p.t_sent)
    complete = [f for f in range(v["frames"]) if got[f] == n]
    worst = max((last[f] for f in complete), default=float("inf"))
    return len(complete), worst, sum(net.dropped.values())


def min_buffer(payload, limit=60):
    """Smallest buffer (packets) that loses no packet of the stream, found by trying 0, 1, 2, ..."""
    for b in range(limit + 1):
        if video_trial(payload, b)[2] == 0:
            return b
    return None


def smallest_payload(buffer, lo=761, hi=1460):
    """Smallest payload in [lo, hi] bytes that loses nothing with `buffer` waiting packets (bisection:
    a bigger payload never needs more packets per frame). Returns None if even `hi` loses packets."""
    if video_trial(hi, buffer)[2] > 0:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if video_trial(mid, buffer)[2] == 0:
            hi = mid
        else:
            lo = mid + 1
    return lo


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # --- routing
    g = {"A": {"B": 4, "C": 1}, "B": {"A": 4, "C": 2, "D": 1}, "C": {"A": 1, "B": 2, "D": 5}, "D": {"B": 1, "C": 5}}
    dist, _ = dijkstra(g, "A")
    print("Dijkstra from A:", dist, " next hops:", routing_tables(g)["A"])

    # --- delay validation: one packet over a 3-link path with different rates
    net = line_network([10e6, 2e6, 10e6], [0.005, 0.020, 0.005])
    net.inject(0.0, "n0", "n3", 12000)
    net.run()
    sim = net.delays()[0]
    ana = path_delay(net, ["n0", "n1", "n2", "n3"], 12000)
    print(f"one packet: simulated {1000 * sim:.3f} ms, analytic {1000 * ana:.3f} ms")

    # --- burst through one link: queueing grows 1.2 ms per packet, buffer of 4 drops the rest
    net = two_node_network(buffer=4)
    for _ in range(10):
        net.inject(0.0, "S", "D", 12000)
    net.run()
    d = np.array(sorted(net.delays()))
    print("burst of 10, buffer 4: delivered", len(d), "dropped", dict(net.dropped), "delays (ms)", np.round(1000 * d, 2))

    # --- stop-and-wait and windows
    for w in (1, 4, 8, 18, 64):
        u, tr, _ = utilisation(2000, 12000, w)
        print(f"window {w:2d}: measured U = {u:.4f}, formula {utilisation_formula(12000, w):.4f}")
    u, tr, net = utilisation(3000, 12000, 1, loss=0.2, timeout=0.05, seed=1)
    print("stop-and-wait with 20 percent loss: all delivered", len(tr.acked) == 3000, ", transmissions", tr.transmissions,
          ", U", round(u, 4))

    # --- link failure
    net, times = reroute_experiment()
    t = net.totals()
    print("reroute:", t, dict(net.dropped))
    for s in (0.021, 0.081, 0.201, 0.301):
        pk = [(p, tt) for p, tt in net.delivered if abs(p.t_sent - s) < 1e-9]
        print(f"  packet sent at {s:.3f} s: delay {1000 * (pk[0][1] - s):.2f} ms" if pk else f"  packet sent at {s:.3f} s: lost")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    got = {round(p.t_sent, 6): tt - p.t_sent for p, tt in net.delivered}
    ax.plot([s for s in times if round(s, 6) in got], [1000 * got[round(s, 6)] for s in times if round(s, 6) in got], "o", ms=3, label="delivered")
    lost = [s for s in times if round(s, 6) not in got]
    ax.plot(lost, [0] * len(lost), "rx", label="lost")
    ax.axvline(0.100, color="gray", ls=":")
    ax.axvline(0.150, color="gray", ls=":")
    ax.set_xlabel("time the packet was sent (s)")
    ax.set_ylabel("end-to-end delay (ms)")
    ax.set_title("Link cut at 0.10 s, routes updated at 0.15 s")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "reroute.png", dpi=120)

    # --- delay validation figure
    fig2, axs = plt.subplots(1, 2, figsize=(10, 4))
    k = np.arange(len(d))
    axs[0].plot(k + 1, 1000 * d, "o", label="simulated (delivered)")
    axs[0].plot(k + 1, 1000 * ((k + 1) * 0.0012 + 0.010), "-", label="(k x 1.2 ms) + 10 ms formula")
    axs[0].set_xlabel("packet number in the burst (k)")
    axs[0].set_ylabel("end-to-end delay (ms)")
    axs[0].set_title("Burst of 10, buffer of 4: 5 delivered, 5 dropped")
    axs[0].grid(alpha=0.3)
    axs[0].legend()
    ws = np.arange(1, 25)
    meas = [utilisation(600, 12000, int(w))[0] for w in ws]
    axs[1].plot(ws, meas, "o", label="simulated")
    axs[1].plot(ws, [utilisation_formula(12000, int(w)) for w in ws], "-", label="min(1, W x / (x + RTT))")
    axs[1].set_xlabel("window W (packets)")
    axs[1].set_ylabel("link utilisation U")
    axs[1].set_title("Window protocol: simulation against the formula")
    axs[1].grid(alpha=0.3)
    axs[1].legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "delay_and_window.png", dpi=120)

    # --- AIMD
    w, dl, dr = aimd(bdp=20, buffer=20, rounds=200)
    print("AIMD bdp 20, buffer 20: peak", w[100:].max(), "min", w[100:].min(), "mean", round(w[100:].mean(), 2),
          "sent", w.sum(), "delivered", dl.sum(), "dropped", dr.sum())
    for buf in (0, 10, 20):
        print(f"  buffer {buf:2d}: utilisation {aimd_utilisation(20, buf):.3f}")
    fig3, ax3 = plt.subplots(figsize=(6.5, 4))
    ax3.plot(w, label="window w")
    ax3.axhline(40, color="red", ls="--", label="pipe + buffer = 40")
    ax3.axhline(20, color="gray", ls=":", label="pipe (bdp) = 20")
    ax3.set_xlabel("round trip number")
    ax3.set_ylabel("window (packets)")
    ax3.set_title("Toy AIMD sawtooth (simplified illustration)")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "aimd_sawtooth.png", dpi=120)

    # --- failure cases
    net = diamond()
    net.tables["R2"]["B"] = "R1"
    print("loop:", has_loop(net.tables, "A", "B"))
    net.inject(0.0, "A", "B", 12000, ttl=10)
    net.run()
    print("   traversals", sum(lk.carried for lk in net.links.values()), "dropped", dict(net.dropped))
    net = diamond()
    del net.tables["R1"]["B"]
    net.inject(0.0, "A", "B", 12000)
    net.run()
    print("missing route:", dict(net.dropped))

    # --- mini-project
    print("payload  packets/frame  min buffer  worst frame delay (ms)  overhead")
    for payload in (400, 761, 800, 1000, 1200, 1460):
        n = math.ceil(20000 / payload)
        b = min_buffer(payload)
        done, worst, lost = video_trial(payload, b)
        print(f"{payload:6d}  {n:12d}  {b:10d}  {1000 * worst:20.2f}  {100 * 40 / (40 + payload):.2f}%   memory {b * (payload + 40)} bytes")
    best = smallest_payload(16)
    print("router with 16 buffer slots: smallest loss-free payload", best, "->", video_trial(best, 16),
          "; one byte less:", video_trial(best - 1, 16))

# %% [markdown]
# ## Where this stops
# Real routers use distributed protocols instead of one global Dijkstra, real senders adapt
# their window to feedback, and queues are managed actively. The simulator is a model; the
# roadmap in `promo/roadmap.md` shows how to take it toward the Target.
