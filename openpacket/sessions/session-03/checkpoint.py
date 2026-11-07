"""Checkpoint for Session 3. Prints PASS or FAIL."""
import itertools
import math
import random


def _best_by_brute_force(graph, src, dst):
    """Cheapest cost over all simple paths (only for tiny graphs): a check that does not use Dijkstra."""
    others = [n for n in graph if n not in (src, dst)]
    best = math.inf
    for r in range(len(others) + 1):
        for mid in itertools.permutations(others, r):
            path = [src, *mid, dst]
            if all(b in graph[a] for a, b in zip(path, path[1:])):
                best = min(best, sum(graph[a][b] for a, b in zip(path, path[1:])))
    return best


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # --- Dijkstra
    g = {"A": {"B": 4, "C": 1}, "B": {"A": 4, "C": 2, "D": 1}, "C": {"A": 1, "B": 2, "D": 5}, "D": {"B": 1, "C": 5}}
    dist, _ = L.dijkstra(g, "A")
    checks.append(("hand calculation: from A the costs are B 3, C 1, D 4 (A-C-B-D)",
                   dist == {"A": 0.0, "B": 3.0, "C": 1.0, "D": 4.0}))
    tab = L.routing_tables(g)
    checks.append(("the next hop from A to D is C, and from D to A is B",
                   tab["A"]["D"] == "C" and tab["D"]["A"] == "B"))
    rng = random.Random(4)
    names = list("ABCDEFG")
    big = {n: {} for n in names}
    for a, b in itertools.combinations(names, 2):
        if rng.random() < 0.5:
            w = rng.randint(1, 9)
            big[a][b] = big[b][a] = w
    agree = True
    for a in names:
        d, _ = L.dijkstra(big, a)
        for b in names:
            if a != b:
                agree &= abs(d.get(b, math.inf) - _best_by_brute_force(big, a, b)) < 1e-12
    checks.append(("Dijkstra equals brute-force search over all paths for every pair in a random 7-node graph", agree))
    iso = {"A": {"B": 1}, "B": {"A": 1}, "Z": {}}
    checks.append(("an unreachable node gets no route", "Z" not in L.routing_tables(iso)["A"]))

    # --- delay validation
    net = L.line_network([10e6, 2e6, 10e6], [0.005, 0.020, 0.005])
    net.inject(0.0, "n0", "n3", 12000)
    net.run()
    sim = net.delays()[0]
    checks.append((f"one packet over 3 links: simulated {1000 * sim:.3f} ms equals the sum of transmission and propagation, 38.400 ms",
                   abs(sim - 0.0384) < 1e-12 and abs(L.path_delay(net, ["n0", "n1", "n2", "n3"], 12000) - 0.0384) < 1e-12))
    net = L.line_network([10e6, 2e6, 10e6], [0.005, 0.020, 0.005])
    for _ in range(6):
        net.inject(0.0, "n0", "n3", 12000)
    net.run()
    last = max(net.delays())
    checks.append(("a burst of 6 over links of 10, 2 and 10 Mbit/s: last packet delay = sum of x + 5 * slowest x + delays",
                   abs(last - L.burst_last_delay(net, ["n0", "n1", "n2", "n3"], 12000, 6)) < 1e-12))

    # --- queue, buffer, loss (worked example of Section E)
    net = L.two_node_network(buffer=4)
    for _ in range(10):
        net.inject(0.0, "S", "D", 12000)
    net.run()
    d = sorted(net.delays())
    checks.append((f"worked example: burst of 10, buffer 4: 5 delivered, 5 dropped, last delivered delay 16.0 ms (got {len(d)}, {net.dropped['buffer']}, {1000 * d[-1]:.1f})",
                   len(d) == 5 and net.dropped["buffer"] == 5 and abs(d[-1] - 0.016) < 1e-12))
    checks.append(("delay of packet k in the burst is k * 1.2 ms + 10 ms (k = 1..5), so queueing adds 1.2 ms per packet ahead",
                   all(abs(x - (k * 0.0012 + 0.010)) < 1e-12 for k, x in enumerate(d, 1))))
    checks.append(("queueing delay of the last delivered packet is 4 * 1.2 = 4.8 ms", abs((d[-1] - d[0]) - 0.0048) < 1e-12))
    net0 = L.two_node_network(buffer=0)
    for _ in range(2):
        net0.inject(0.0, "S", "D", 12000)
    net0.run()
    checks.append(("edge case: with no buffer a burst of 2 delivers 1 and drops 1", len(net0.delivered) == 1 and net0.dropped["buffer"] == 1))

    # --- conservation at many stop times
    lossy = L.two_node_network(buffer=5, loss=0.1, seed=7)
    for i in range(60):
        lossy.inject(i * 0.0005, "S", "D", 12000)
    ok, busy = True, 0
    for stop in (0.0, 0.003, 0.0171, 0.02, 0.05, 0.1):
        lossy.run(until=stop)
        ok &= lossy.conserved()
        busy += lossy.totals()["in_flight"] > 0
    lossy.run()
    end = lossy.totals()
    checks.append(("sent = delivered + dropped + in flight at six stop times", ok and busy >= 3))
    checks.append(("at the end nothing is in flight and 60 sent = delivered + dropped",
                   end["in_flight"] == 0 and end["sent"] == 60 and end["delivered"] + end["dropped"] == 60 and lossy.dropped["buffer"] > 0 and lossy.dropped["loss"] > 0))

    # --- stop-and-wait and windows
    x, rtt = 12000 / 10e6, 2 * 0.010 + 400 / 10e6
    u1, tr1, _ = L.utilisation(2000, 12000, 1)
    checks.append((f"stop-and-wait U = x / (x + RTT) = 1.2 / 21.24 = 0.0565 (got {u1:.4f})",
                   abs(u1 - x / (x + rtt)) < 1e-9 and abs(u1 - 0.056497) < 1e-5 and len(tr1.acked) == 2000))
    ok = True
    for w, target in ((4, 0.2260), (8, 0.4520)):
        u, _, _ = L.utilisation(2000, 12000, w)
        ok &= abs(u - L.utilisation_formula(12000, w)) < 0.005 * target and abs(u - target) < 0.001
    checks.append(("windows of 4 and 8 give utilisation 0.226 and 0.452 as W x / (x + RTT) says", ok))
    u18, _, _ = L.utilisation(2000, 12000, 18)
    checks.append(("a window of 18 fills the pipe: utilisation above 0.99, and equals N x / (N x + RTT) for N = 2000",
                   u18 > 0.99 and abs(u18 - 2000 * x / (2000 * x + rtt)) < 1e-4))
    p = 0.2
    ul, trl, netl = L.utilisation(3000, 12000, 1, loss=p, timeout=0.05, seed=1)
    per = (x + rtt) + p / (1 - p) * 0.05
    checks.append((f"with 20 percent loss every packet still arrives; transmissions per packet about 1/(1-p) = 1.25 (got {trl.transmissions / 3000:.3f})",
                   len(trl.acked) == 3000 and len(trl.received) == 3000 and abs(trl.transmissions / 3000 - 1.25) < 0.03))
    checks.append((f"with loss, U = x / ((x + RTT) + p/(1-p) * timeout) = 0.0356 within 5 percent (got {ul:.4f})",
                   abs(ul - x / per) < 0.05 * x / per))
    checks.append(("lossy transfer keeps the packet count balanced", netl.conserved() and netl.totals()["in_flight"] == 0))

    checks.append(("x = 1.2 ms, RTT after sending = 20.04 ms, and a window of 18 is the smallest that fills the pipe",
                   abs(x - 0.0012) < 1e-12 and abs(rtt - 0.02004) < 1e-12 and math.ceil((x + rtt) / x) == 18
                   and L.utilisation_formula(12000, 17) < 1.0 and L.utilisation_formula(12000, 18) == 1.0))
    checks.append(("stop-and-wait throughput is 0.0565 * 10 Mbit/s = 0.565 Mbit/s", abs(u1 * 10 - 0.565) < 0.001))

    # --- link failure and re-routing
    net, times = L.reroute_experiment()
    arrivals = [0.001 + 0.004 * k + 0.005 + 12000 / 10e6 for k in range(len(times))]
    expected_lost = sum(1 for a in arrivals if 0.100 - 0.0012 <= a < 0.150)
    t = net.totals()
    checks.append((f"link R1-R2 cut at 0.10 s, routes updated at 0.15 s: {expected_lost} packets lost, as counted from arrival times at R1 (got {net.dropped['link_down']})",
                   net.dropped["link_down"] == expected_lost == 13 and t["sent"] == 99 and t["delivered"] == 86))
    byt = {round(p.t_sent, 6): tt - p.t_sent for p, tt in net.delivered}
    before = [v for s, v in byt.items() if s < 0.09]
    after = [v for s, v in byt.items() if s > 0.2]
    checks.append(("before the cut every delay is 18.6 ms (3 links of 5 + 1.2 ms); after re-routing it is 33.6 ms (3 links of 10 + 1.2 ms)",
                   all(abs(v - 0.0186) < 1e-9 for v in before) and all(abs(v - 0.0336) < 1e-9 for v in after) and len(before) > 10 and len(after) > 10))
    checks.append(("the re-routed path is the shortest path of the remaining graph", L.diamond().tables["A"]["B"] == "R1"
                   and net.tables["A"]["B"] == "R3"))
    checks.append(("packet count balanced through the failure", net.conserved() and t["in_flight"] == 0))

    net2, times2 = L.reroute_experiment(detect_after=0.025)
    arr2 = [0.001 + 0.004 * k + 0.005 + 0.0012 for k in range(len(times2))]
    checks.append(("detecting the failure after 0.025 s instead of 0.05 s loses 7 packets instead of 13",
                   net2.dropped["link_down"] == 7 == sum(1 for a in arr2 if 0.1 - 0.0012 <= a < 0.125)))

    # --- failure cases
    net = L.diamond()
    net.tables["R2"]["B"] = "R1"
    net.inject(0.0, "A", "B", 12000, ttl=10)
    net.run()
    hops = sum(lk.carried for lk in net.links.values())
    checks.append(("routing loop: detected by has_loop, the packet makes exactly 10 hops (its TTL) and is dropped, never delivered",
                   L.has_loop(net.tables, "A", "B") and hops == 10 and net.dropped["ttl"] == 1 and not net.delivered and net.conserved()))
    net = L.diamond()
    checks.append(("the healthy tables contain no loop", not L.has_loop(net.tables, "A", "B")))
    del net.tables["R1"]["B"]
    net.inject(0.0, "A", "B", 12000)
    net.run()
    checks.append(("missing route: the packet is dropped at R1 with reason no_route", net.dropped["no_route"] == 1 and not net.delivered))

    # --- AIMD toy model
    w, dl, dr = L.aimd(20, 20, 400)
    tail = w[200:]
    checks.append((f"AIMD sawtooth: window climbs to about 40 then halves to about 20 (peak {tail.max():.1f}, low {tail.min():.1f})",
                   abs(tail.max() - 40) < 0.5 and abs(tail.min() - 20) < 0.5))
    checks.append((f"AIMD mean window is about 3/4 of the peak (got {tail.mean() / tail.max():.3f})", abs(tail.mean() / tail.max() - 0.75) < 0.02))
    checks.append(("AIMD packets: sent = delivered + dropped", abs(w.sum() - dl.sum() - dr.sum()) < 1e-9))
    u0, u10, u20 = (L.aimd_utilisation(20, b) for b in (0, 10, 20))
    checks.append((f"buffer 0, 10 and 20 give utilisation about 0.75, 0.95 and 1.00 (got {u0:.3f}, {u10:.3f}, {u20:.3f})",
                   abs(u0 - 0.75) < 0.01 and abs(u10 - 0.954) < 0.01 and u20 > 0.999))

    # --- mini-project
    n = math.ceil(20000 / 1177)
    done, worst, lost = L.video_trial(1177, 16)
    checks.append((f"mini-project: payload 1177 gives 17 packets per frame, loses nothing with 16 buffer slots, worst frame delay 43.10 ms (got {n}, {lost}, {1000 * worst:.2f})",
                   n == 17 and lost == 0 and done == 60 and abs(worst - (17 * 1217 * 8 / 5e6 + 0.010)) < 1e-9))
    done2, _, lost2 = L.video_trial(1176, 16)
    checks.append(("payload 1176 needs 18 packets per frame and loses one per frame with 16 slots, so no frame is complete",
                   math.ceil(20000 / 1176) == 18 and lost2 == 60 and done2 == 0))
    checks.append(("the smallest loss-free payload for 16 slots is 1177, found by bisection", L.smallest_payload(16) == 1177))
    checks.append(("overhead of that choice is 40 / 1217 = 3.29 percent, below 5 percent", 40 / 1217 < 0.05 and abs(40 / 1217 - 0.0329) < 5e-5))
    checks.append(("the smallest loss-free buffer is n - 1: 13 slots for payload 1460, 26 for payload 761",
                   L.min_buffer(1460) == 13 and L.min_buffer(761) == 26))
    checks.append(("payload 761 into 20 slots: 27 packets per frame, 6 lost from each of the 60 frames",
                   math.ceil(20000 / 761) == 27 and L.video_trial(761, 20)[2] == 360))
    checks.append(("worst frame delay of the chosen design is below the 45 ms limit", worst < 0.045))
    checks.append(("a router with 20 slots needs payload 953 (21 packets per frame), overhead 40 / 993 = 4.03 percent",
                   L.smallest_payload(20) == 953 and math.ceil(20000 / 953) == 21 and abs(40 / 993 - 0.0403) < 5e-5))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
