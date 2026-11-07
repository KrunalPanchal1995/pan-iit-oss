"""Checkpoint for Session 2. Prints PASS or FAIL."""
import random


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # addresses as numbers
    checks.append(("192.168.1.20 is the number 3232235796", L.ip_to_int("192.168.1.20") == 3232235796))
    checks.append(("0.0.0.0 is 0 and 255.255.255.255 is 2**32 - 1",
                   L.ip_to_int("0.0.0.0") == 0 and L.ip_to_int("255.255.255.255") == 2 ** 32 - 1))
    rng = random.Random(5)
    values = [rng.randrange(2 ** 32) for _ in range(200)]
    checks.append(("converting 200 random numbers to dotted decimal and back restores them",
                   all(L.ip_to_int(L.int_to_ip(v)) == v for v in values)))
    try:
        L.ip_to_int("256.1.1.1")
        refused = False
    except ValueError:
        refused = True
    checks.append(("an address with a part above 255 is refused", refused))

    # toy packet
    pkt = L.make_packet("192.168.1.20", "10.1.2.77", 7, b"hello")
    src, dst, seq, payload, ok = L.parse_packet(pkt)
    checks.append(("toy packet: 14 byte header + 5 byte payload = 19 bytes, fields read back",
                   L.HEADER_SIZE == 14 and len(pkt) == 19 and (src, dst, seq, payload, ok) == ("192.168.1.20", "10.1.2.77", 7, b"hello", True)))
    flips = 0
    for i in range(len(pkt)):
        for bit in range(8):
            bad = bytearray(pkt)
            bad[i] ^= 1 << bit
            flips += 0 if L.parse_packet(bytes(bad))[4] else 1
    checks.append((f"every one of the {8 * len(pkt)} single-bit flips is caught by the checksum", flips == 8 * len(pkt)))
    checks.append(("a hand-sized checksum: the words 0x0001 and 0xF203 sum to 0xF204, checksum 0x0DFB",
                   L.internet_checksum(bytes([0x00, 0x01, 0xF2, 0x03])) == 0x0DFB))

    # subnets
    checks.append(("a /24 subnet has 256 addresses and a /16 has 65536",
                   L.subnet_size(24) == 256 and L.subnet_size(16) == 65536))
    checks.append(("the /24 mask is 0xFFFFFF00, /0 is 0 and /32 is all ones",
                   L.mask_of(24) == 0xFFFFFF00 and L.mask_of(0) == 0 and L.mask_of(32) == 0xFFFFFFFF))
    checks.append(("192.168.1.0/24 holds 192.168.1.255 but not 192.168.2.0 (bitwise AND with the mask)",
                   L.in_subnet("192.168.1.255", "192.168.1.0/24") and not L.in_subnet("192.168.2.0", "192.168.1.0/24")))
    first, last = L.ip_to_int("192.168.1.0"), L.ip_to_int(L.broadcast_of("192.168.1.0/24"))
    checks.append(("counting from the first to the last address of the /24 gives 256", last - first + 1 == 256))
    checks.append(("a /32 holds exactly one address", L.in_subnet("1.2.3.4", "1.2.3.4/32") and not L.in_subnet("1.2.3.5", "1.2.3.4/32")))

    # longest prefix match
    t = L.SMALL_TABLE
    expect = {"10.1.2.77": "lab", "10.1.3.5": "campus", "10.9.9.9": "corporate gateway",
              "8.8.8.8": "ISP", "192.168.1.5": "local network"}
    checks.append(("longest-prefix match picks lab, campus, corporate gateway, ISP, local network for the five test addresses",
                   all(L.longest_prefix_match(t, a) == n for a, n in expect.items())))
    shuffled = t[:]
    random.Random(2).shuffle(shuffled)
    checks.append(("the answer does not depend on the order of the rows",
                   all(L.longest_prefix_match(shuffled, a) == n for a, n in expect.items())))
    checks.append(("without a default route an unknown address has no next hop",
                   L.longest_prefix_match(t[1:], "8.8.8.8") is None))

    # latency
    d_km = L.great_circle_km(28.61, 77.21, 51.51, -0.13)
    checks.append((f"Delhi to London great-circle distance is about 6712 km (got {d_km:.0f})", abs(d_km - 6712) < 15))
    checks.append(("the haversine distance of a point to itself is 0 and a quarter of the equator is 10007.5 km",
                   L.great_circle_km(10, 10, 10, 10) == 0 and abs(L.great_circle_km(0, 0, 0, 90) - 10007.5) < 0.1))
    d = 6.712e6
    prop = L.propagation_s(d)
    trans = L.transmission_s(8 * 1500, 100e6)
    total = L.one_way_delay_s(1500, 100e6, d, queueing_s=0.002)
    checks.append((f"worked example: 33.56 ms + 0.12 ms + 2 ms = 35.68 ms (got {1000 * prop:.2f} + {1000 * trans:.2f}, total {1000 * total:.2f})",
                   abs(prop - 0.03356) < 1e-9 and abs(trans - 0.00012) < 1e-12 and abs(total - 0.03568) < 1e-9))
    checks.append(("minimum round trip over 6712 km of fibre is 67.12 ms", abs(L.min_rtt_s(d) - 0.06712) < 1e-9))
    checks.append(("light in vacuum would give a one-way propagation of 22.4 ms over 6712 km",
                   abs(1000 * L.propagation_s(d, L.LIGHT_SPEED) - 22.4) < 0.05))
    checks.append(("a hundred times more bandwidth cuts transmission 100 times but propagation not at all",
                   abs(L.transmission_s(12000, 1e6) / L.transmission_s(12000, 100e6) - 100) < 1e-9
                   and abs((L.one_way_delay_s(1500, 1e6, d) - L.one_way_delay_s(1500, 100e6, d))
                           - (L.transmission_s(12000, 1e6) - L.transmission_s(12000, 100e6))) < 1e-12))

    # packet size design
    checks.append(("14 byte header: payload of 267 bytes gives under 5 percent, 266 gives exactly 5 percent",
                   L.min_payload_for_overhead(14) == 267 and abs(L.overhead(14, 266) - 0.05) < 1e-12 and L.overhead(14, 267) < 0.05))
    checks.append(("40 byte header needs at least 761 bytes of payload (4.99 percent); 760 is exactly 5 percent",
                   L.min_payload_for_overhead(40) == 761 and L.overhead(40, 761) < 0.05 and abs(L.overhead(40, 760) - 0.05) < 1e-12))
    checks.append(("20 byte header needs at least 381 bytes", L.min_payload_for_overhead(20) == 381))
    checks.append(("a 10 percent limit with a 40 byte header needs 361 bytes", L.min_payload_for_overhead(40, 0.1) == 361))
    checks.append(("a /20 subnet has 4096 addresses; 10.1.15.200 is inside 10.1.0.0/20 but 10.1.16.0 is not",
                   L.subnet_size(20) == 4096 and L.in_subnet("10.1.15.200", "10.1.0.0/20") and not L.in_subnet("10.1.16.0", "10.1.0.0/20")))
    fits = [pl for pl in range(1, 1500) if L.transmission_s(8 * (pl + 40), 1e6) <= 0.010 + 1e-12]
    checks.append(("40 byte header at 1 Mbit/s: at most 1210 bytes of payload keep transmission within 10 ms, so 761 to 1210 works",
                   max(fits) == 1210 and L.overhead(40, 761) < 0.05 <= L.overhead(40, 760) + 1e-12))
    checks.append(("in vacuum the minimum round trip over 6712 km would be 44.8 ms",
                   abs(2000 * L.propagation_s(d, L.LIGHT_SPEED) - 44.8) < 0.1))
    checks.append(("a /26 holds 64 addresses; the /20 mask is 0xFFFFF000 (255.255.240.0)",
                   L.subnet_size(26) == 64 and L.mask_of(20) == 0xFFFFF000 and L.int_to_ip(L.mask_of(20)) == "255.255.240.0"))
    matches = [c for c, _ in t_ if L.in_subnet("10.1.2.77", c)] if (t_ := L.SMALL_TABLE) else []
    checks.append(("10.1.2.77 matches four rows of the table (/0, /8, /16, /24) and the /24 wins", len(matches) == 4))
    ext = L.SMALL_TABLE + [("10.1.2.64/26", "server room")]
    checks.append(("with a /26 row added, 10.1.2.77 goes to the server room", L.longest_prefix_match(ext, "10.1.2.77") == "server room"))
    checks.append(("a 1000 byte payload with a 40 byte header has 3.85 percent overhead", abs(100 * L.overhead(40, 1000) - 3.85) < 0.005))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
