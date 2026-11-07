"""Session 2 (Level 2): headers, addresses, routing tables and the latency budget.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of a packet
# **A. Real-world problem.** A packet must say who sent it, where it is going, which piece of
# the message it is, and carry a check so damage can be noticed. All of that is *header* and
# costs bytes. Then every router must choose the next hop in a fraction of a microsecond, and
# the whole trip takes time that no engineering can shrink below the speed of light in fibre.
# How big is the header overhead? How does a router choose? How fast can Delhi talk to London?
#
# **Plan.** (1) treat IPv4 addresses as 32-bit numbers, (2) build a toy packet from bytes with
# a checksum, (3) use bit masks for subnets, (4) write longest-prefix-match routing, (5) add up
# the delays, (6) size packets to keep the header overhead under 5 percent.

# %%
import math
import pathlib
import struct
from fractions import Fraction

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

HEADER_FORMAT = "!IIHHH"          # source (4 bytes), destination (4), sequence (2), length (2), checksum (2)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
FIBRE_SPEED = 2.0e8               # metres per second: light in glass is about two thirds of its speed in vacuum
LIGHT_SPEED = 299_792_458.0       # metres per second in vacuum


# %% [markdown]
# ## Step 1: addresses are 32-bit numbers
# An IPv4 address such as 192.168.1.20 is four bytes. As one number it is
# `192*256**3 + 168*256**2 + 1*256 + 20`. Going back means taking the four bytes again.

# %%
def ip_to_int(text):
    """'192.168.1.20' -> 3232235796"""
    parts = [int(x) for x in text.split(".")]
    if len(parts) != 4 or any(p < 0 or p > 255 for p in parts):
        raise ValueError("not an IPv4 address: " + text)
    value = 0
    for p in parts:
        value = value * 256 + p
    return value


def int_to_ip(value):
    """3232235796 -> '192.168.1.20'"""
    if not 0 <= value < 2 ** 32:
        raise ValueError("an IPv4 address is a number from 0 to 2**32 - 1")
    return ".".join(str((value >> shift) & 255) for shift in (24, 16, 8, 0))


# %% [markdown]
# ## Step 2: a toy packet with header, payload and checksum
# Header = source, destination, sequence number, payload length, checksum (14 bytes). The
# checksum is the *internet checksum*: add all 16-bit words, fold the carries back in, and
# flip the bits. A receiver adds everything including the checksum and must get all ones, which
# the code reports as 0 after the flip. This is a simplified toy, not the real IPv4 header.

# %%
def internet_checksum(data):
    """16-bit ones-complement checksum of `data` (bytes)."""
    if len(data) % 2:
        data = data + b"\x00"
    total = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    while total > 0xFFFF:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def make_packet(src, dst, seq, payload):
    """Bytes of a packet: 14 byte header followed by the payload."""
    head = struct.pack(HEADER_FORMAT, ip_to_int(src), ip_to_int(dst), seq, len(payload), 0)
    checksum = internet_checksum(head + payload)
    return struct.pack(HEADER_FORMAT, ip_to_int(src), ip_to_int(dst), seq, len(payload), checksum) + payload


def parse_packet(packet):
    """Return (source, destination, sequence, payload, checksum_ok)."""
    src, dst, seq, length, _ = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
    payload = packet[HEADER_SIZE:HEADER_SIZE + length]
    ok = len(packet) == HEADER_SIZE + length and internet_checksum(packet) == 0
    return int_to_ip(src), int_to_ip(dst), seq, payload, ok


# %% [markdown]
# ## Step 3: subnets with bit masks
# `192.168.1.0/24` means: the first 24 bits are the network, the last 8 bits number the hosts.
# The *mask* has 24 ones then 8 zeros. An address belongs to the subnet when
# `address AND mask == network`. The subnet has 2**(32 - 24) = 256 addresses.

# %%
def parse_cidr(text):
    """'10.1.2.0/24' -> (network as int, prefix length)"""
    address, prefix = text.split("/")
    prefix = int(prefix)
    if not 0 <= prefix <= 32:
        raise ValueError("prefix length must be 0 to 32")
    return ip_to_int(address), prefix


def mask_of(prefix):
    """32-bit mask with `prefix` ones followed by zeros."""
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF


def subnet_size(prefix):
    return 2 ** (32 - prefix)


def in_subnet(address, cidr):
    network, prefix = parse_cidr(cidr)
    return (ip_to_int(address) & mask_of(prefix)) == (network & mask_of(prefix))


def broadcast_of(cidr):
    """Last address of the subnet: the host bits all ones."""
    network, prefix = parse_cidr(cidr)
    return int_to_ip((network & mask_of(prefix)) | (~mask_of(prefix) & 0xFFFFFFFF))


# %% [markdown]
# ## Step 4: routing table with longest-prefix match
# A router holds rows (prefix, next hop). Several rows can match one address; the router must
# use the *most specific* one: the match with the longest prefix. `0.0.0.0/0` matches
# everything and is the default route.

# %%
SMALL_TABLE = [
    ("0.0.0.0/0", "ISP"),
    ("10.0.0.0/8", "corporate gateway"),
    ("10.1.0.0/16", "campus"),
    ("10.1.2.0/24", "lab"),
    ("192.168.1.0/24", "local network"),
]


def longest_prefix_match(table, address):
    """Next hop of the matching row with the longest prefix, or None when no row matches."""
    best, best_len = None, -1
    for cidr, next_hop in table:
        prefix = parse_cidr(cidr)[1]
        if in_subnet(address, cidr) and prefix > best_len:
            best, best_len = next_hop, prefix
    return best


# %% [markdown]
# ## Step 5: the latency budget
# One-way delay of a packet over one link is the sum of three parts:
#
#     propagation = distance / speed        (light in fibre, about 2e8 m/s)
#     transmission = bits / bandwidth       (time to push all bits onto the wire)
#     queueing = time waiting behind other packets
#
# Even with zero queueing, the round trip cannot be shorter than 2 * distance / speed.

# %%
def great_circle_km(lat1, lon1, lat2, lon2):
    """Distance over the Earth's surface in km (haversine formula, Earth radius 6371 km)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(a))


def propagation_s(distance_m, speed=FIBRE_SPEED):
    return distance_m / speed


def transmission_s(bits, bandwidth_bps):
    return bits / bandwidth_bps


def one_way_delay_s(packet_bytes, bandwidth_bps, distance_m, queueing_s=0.0, speed=FIBRE_SPEED):
    return propagation_s(distance_m, speed) + transmission_s(8 * packet_bytes, bandwidth_bps) + queueing_s


def min_rtt_s(distance_m, speed=FIBRE_SPEED):
    """Smallest possible round-trip time: there and back at the signal speed, no queueing."""
    return 2 * distance_m / speed


# %% [markdown]
# ## Step 6: how big should packets be?
# With header `h` bytes and payload `p` bytes the overhead is `h / (h + p)`. To keep it below a
# limit `x` we need `p > h * (1 - x) / x`. We use exact fractions so that a result exactly on
# the limit is not wrongly accepted.

# %%
def overhead(header_bytes, payload_bytes):
    return header_bytes / (header_bytes + payload_bytes)


def min_payload_for_overhead(header_bytes, limit=Fraction(5, 100)):
    """Smallest whole number of payload bytes whose overhead is strictly below `limit`."""
    limit = Fraction(limit).limit_denominator(10 ** 6)     # 0.1 as a float becomes exactly 1/10
    payload = 1
    while Fraction(header_bytes, header_bytes + payload) >= limit:
        payload += 1
    return payload


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("192.168.1.20 as a number:", ip_to_int("192.168.1.20"), "->", int_to_ip(ip_to_int("192.168.1.20")))
    pkt = make_packet("192.168.1.20", "10.1.2.77", 7, b"hello")
    print("toy packet:", len(pkt), "bytes, header", HEADER_SIZE, "bytes;", pkt.hex())
    print("parsed:", parse_packet(pkt))
    damaged = bytearray(pkt)
    damaged[-1] ^= 0x01
    print("after flipping one bit, checksum ok:", parse_packet(bytes(damaged))[4])
    print("/24 has", subnet_size(24), "addresses; mask", hex(mask_of(24)), "broadcast", broadcast_of("192.168.1.0/24"))
    for ip in ("10.1.2.77", "10.1.3.5", "10.9.9.9", "8.8.8.8", "192.168.1.5"):
        print(f"  {ip:12s} -> {longest_prefix_match(SMALL_TABLE, ip)}")

    d_km = great_circle_km(28.61, 77.21, 51.51, -0.13)     # Delhi to London
    d_m = d_km * 1000
    print(f"Delhi-London great circle: {d_km:.0f} km")
    print(f"propagation in fibre: {1000 * propagation_s(d_m):.1f} ms,  in vacuum: {1000 * propagation_s(d_m, LIGHT_SPEED):.1f} ms")
    print(f"minimum RTT in fibre: {1000 * min_rtt_s(d_m):.1f} ms")
    for bw in (10e6, 100e6, 1e9):
        print(f"  1500 byte packet at {bw / 1e6:6.0f} Mbit/s: transmission {1e6 * transmission_s(12000, bw):9.1f} us, "
              f"one-way {1000 * one_way_delay_s(1500, bw, d_m):.3f} ms")
    print("with 2 ms queueing at 100 Mbit/s:", round(1000 * one_way_delay_s(1500, 100e6, d_m, 0.002), 3), "ms")
    for h in (HEADER_SIZE, 20, 40):
        p = min_payload_for_overhead(h)
        print(f"header {h} bytes: payload at least {p} bytes ({100 * overhead(h, p):.2f} percent)")
    print("payload where transmission = propagation at 1 Mbit/s:", round(1e6 * propagation_s(d_m) / 8), "bytes")

    p = np.arange(1, 1501)
    fig, ax = plt.subplots(figsize=(6, 4))
    for h in (HEADER_SIZE, 40):
        ax.plot(p, 100 * h / (h + p), label=f"header {h} bytes")
    ax.axhline(5, color="red", ls="--", label="5 percent limit")
    ax.set_xlabel("payload per packet (bytes)")
    ax.set_ylabel("header overhead (percent of the packet)")
    ax.set_title("Header overhead falls as packets grow")
    ax.set_ylim(0, 40)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "overhead_vs_payload.png", dpi=120)

    bw = np.logspace(5, 10, 200)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.loglog(bw / 1e6, 1000 * transmission_s(12000, bw), label="transmission of 1500 bytes")
    ax2.loglog(bw / 1e6, np.full_like(bw, 1000 * propagation_s(d_m)), label="propagation Delhi-London")
    ax2.set_xlabel("link bandwidth (Mbit/s)")
    ax2.set_ylabel("delay (ms)")
    ax2.set_title("More bandwidth cannot remove propagation delay")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "delay_budget.png", dpi=120)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
