"""Checkpoint for Session 1. Prints PASS or FAIL."""
import random


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    msg = bytes(range(200))
    pk = L.packetize(msg, 64)
    checks.append(("200 bytes in packets of 64 make 4 packets of 64, 64, 64 and 8 bytes",
                   [len(d) for _, d in pk] == [64, 64, 64, 8]))
    shuffled = pk[:]
    random.Random(3).shuffle(shuffled)
    checks.append(("packets that arrive in a shuffled order are put back into the original message",
                   L.reassemble(shuffled) == msg))
    checks.append(("an empty message makes no packets and rebuilds to nothing",
                   L.packetize(b"", 10) == [] and L.reassemble([]) == b""))
    try:
        L.packetize(b"abc", 0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("a packet size of 0 is refused", bad))
    checks.append(("an exact multiple needs no extra packet: 600 bytes in 300 byte packets is 2",
                   L.packet_count(600, 300) == 2 and L.packet_count(601, 300) == 3))
    route = L.follow_route(L.NEXT_HOP, "laptop", "server")
    checks.append(("the route has 6 nodes and so 5 hops", len(route) == 6 and route[0] == "laptop" and route[-1] == "server"))
    looped = {"a": {"z": "b"}, "b": {"z": "a"}}
    try:
        L.follow_route(looped, "a", "z")
        caught = False
    except RuntimeError:
        caught = True
    checks.append(("a routing loop is detected instead of running forever", caught))
    checks.append(("a single packet over 5 hops needs 5 steps", L.journey_steps(1, 5) == 5))
    checks.append(("hand calculation: 4 packets over 3 hops need 3 + 4 - 1 = 6 steps", L.journey_steps(4, 3) == 6))
    checks.append(("steps = hops + packets - 1 for every case from 1 to 12 packets and 1 to 8 hops",
                   all(L.journey_steps(n, h) == h + n - 1 for n in range(1, 13) for h in range(1, 9))))
    # worked example: 1000 bytes, 300 byte payloads, 3 hops, 40 byte label, 1 Mbit/s links
    n = L.packet_count(1000, 300)
    t = L.delivery_time_ms(1000, 300, 3)
    checks.append((f"worked example: 1000 bytes in 300 byte packets is 4 packets, 6 steps, 16.32 ms (got {n}, {t:.2f})",
                   n == 4 and L.journey_steps(n, 3) == 6 and abs(t - 16.32) < 1e-9))
    checks.append(("one 1000 byte packet over 5 hops takes 41.6 ms",
                   abs(L.delivery_time_ms(1000, 1000, 5) - 41.6) < 1e-9))
    checks.append(("100 byte packets: 10 packets, 14 steps, 15.68 ms over 5 hops",
                   L.packet_count(1000, 100) == 10 and abs(L.delivery_time_ms(1000, 100, 5) - 15.68) < 1e-9))
    checks.append(("20 byte packets are slower than 100 byte packets (25.92 ms against 15.68 ms)",
                   abs(L.delivery_time_ms(1000, 20, 5) - 25.92) < 1e-9
                   and L.delivery_time_ms(1000, 20, 5) > L.delivery_time_ms(1000, 100, 5)))
    best = min(range(10, 1001, 10), key=lambda s: L.delivery_time_ms(1000, s, 5))
    checks.append(("the best payload size in steps of 10 bytes for 1000 bytes over 5 hops is 100", best == 100))
    pk = L.packetize(bytes(900), 250)
    checks.append(("900 bytes in 250 byte payloads: 4 packets of 250, 250, 250 and 150 bytes, 7 steps over 4 hops, 16.24 ms",
                   [len(d) for _, d in pk] == [250, 250, 250, 150] and L.journey_steps(4, 4) == 7
                   and abs(L.delivery_time_ms(900, 250, 4) - 16.24) < 1e-9))
    got = [round(L.delivery_time_ms(1000, s, 5), 2) for s in (50, 100, 200, 500)]
    checks.append((f"1000 bytes over 5 hops: payloads 50, 100, 200, 500 take 17.28, 15.68, 17.28, 25.92 ms (got {got})",
                   got == [17.28, 15.68, 17.28, 25.92]))
    checks.append(("the app default (1000 bytes, 300 byte packets, 5 hops) takes 21.76 ms",
                   abs(L.delivery_time_ms(1000, 300, 5) - 21.76) < 1e-9))
    checks.append(("20 byte packets: 50 packets, 54 steps over 5 hops",
                   L.packet_count(1000, 20) == 50 and L.journey_steps(50, 5) == 54))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
