"""Session 2 (Level 2): parity bits and the Hamming(7,4) code that fixes one flipped bit.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: parity bits and Hamming(7,4)
# **A. Real-world problem.** A check digit (Session 1) tells you *that* something is wrong.
# A scratched QR code still scans, so the code must also tell you *where*, and fix it.
# We build the smallest famous code that does this: Hamming(7,4).
#
# **Plan.** (1) parity, (2) the generator matrix G, (3) the parity-check matrix H and the
# syndrome, (4) the cost of protection (rate), (5) how many parity bits do we need?

# %%
import itertools
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: parity
# The *parity* of a group of bits is their sum modulo 2: 0 if the number of 1s is even, 1 if odd.
# Adding one extra bit that makes the total number of 1s even lets you notice a single flip
# (the count becomes odd) but not find it. To find it we use several overlapping parity checks.

# %%
def parity(bits):
    return int(sum(bits) % 2)


# %% [markdown]
# ## Step 2: the generator matrix G
# Four data bits d1 d2 d3 d4 are followed by three parity bits:
#
#     p1 = d1 + d2 + d4     p2 = d1 + d3 + d4     p3 = d2 + d3 + d4      (all modulo 2)
#
# As a matrix: codeword = data @ G (mod 2), with G = [ I | P ], where I is the 4x4 identity
# (it copies the data) and P holds the parity rules. 4 data bits become 7 bits: the code rate
# is 4/7.

# %%
P = np.array([[1, 1, 0],
              [1, 0, 1],
              [0, 1, 1],
              [1, 1, 1]])
G = np.hstack([np.eye(4, dtype=int), P])          # 4 x 7 generator matrix
H = np.hstack([P.T, np.eye(3, dtype=int)])        # 3 x 7 parity-check matrix


def encode(data4):
    """4 data bits -> 7-bit codeword (modulo 2)."""
    return (np.array(data4) @ G) % 2


# %% [markdown]
# ## Step 3: the syndrome finds the flipped bit
# Multiply the received word r by H (mod 2). The 3-bit answer is the *syndrome*.
# For a valid codeword the syndrome is 000 because H @ G^T = 0 (mod 2). If bit k flips, the
# syndrome equals column k of H. The seven columns of H are all different and non-zero, so the
# syndrome names the bad bit. Flip it back.

# %%
def syndrome(received):
    return (H @ np.array(received)) % 2


def error_position(received):
    """1..7 = which bit to flip back, 0 = syndrome 000 (nothing to fix)."""
    s = syndrome(received)
    if not s.any():
        return 0
    for k in range(7):
        if np.array_equal(H[:, k], s):
            return k + 1
    return 0        # cannot happen for Hamming(7,4): every non-zero syndrome is a column


def decode(received):
    """Return (data4, position corrected or 0)."""
    r = np.array(received).copy()
    pos = error_position(r)
    if pos:
        r[pos - 1] ^= 1
    return r[:4], pos


# %% [markdown]
# ## Step 4: redundancy is a trade-off, and how many parity bits do we need?
# With r parity bits there are 2^r possible syndromes. They must name "no error" plus each of
# the n = k + r bit positions: 2^r >= k + r + 1. Smaller r means a higher code rate k/n but
# less protection per block. The Hamming code is *perfect* when the equality holds
# (r = 3: 8 = 4 + 3 + 1).

# %%
def min_parity_bits(k):
    """Smallest r with 2**r >= k + r + 1 (integers only, no rounding)."""
    r = 1
    while 2 ** r < k + r + 1:
        r += 1
    return r


def code_rate(k, r):
    return k / (k + r)


def hamming_family(rmax=8):
    """Rows (r, n, k, rate) of the perfect Hamming codes n = 2^r - 1."""
    return [(r, 2 ** r - 1, 2 ** r - 1 - r, (2 ** r - 1 - r) / (2 ** r - 1)) for r in range(2, rmax + 1)]


def all_codewords():
    return np.array([encode(d) for d in itertools.product([0, 1], repeat=4)])


def min_distance():
    """Smallest number of differing bits between two different codewords."""
    cw = all_codewords()
    return min(int((a != b).sum()) for i, a in enumerate(cw) for b in cw[i + 1:])


def single_error_success():
    """Try every data word and every single flipped bit; return how many were repaired."""
    ok = total = 0
    for d in itertools.product([0, 1], repeat=4):
        c = encode(d)
        for k in range(7):
            r = c.copy()
            r[k] ^= 1
            total += 1
            ok += np.array_equal(decode(r)[0], d)
    return ok, total


def double_error_success():
    """Same with TWO flipped bits: the decoder is fooled."""
    ok = total = 0
    for d in itertools.product([0, 1], repeat=4):
        c = encode(d)
        for i, j in itertools.combinations(range(7), 2):
            r = c.copy()
            r[i] ^= 1
            r[j] ^= 1
            total += 1
            ok += np.array_equal(decode(r)[0], d)
    return ok, total


# %% [markdown]
# ## Step 5: see it
# Left: the code rate k/n of the Hamming family against the number of parity bits.
# Right: the parity-check matrix H - each column is the syndrome that points at that bit.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("G =\n", G, "\nH =\n", H)
    data = [1, 0, 1, 1]
    c = encode(data)
    print("data", data, "-> codeword", c)
    r = c.copy()
    r[2] ^= 1
    print("received", r, "syndrome", syndrome(r), "-> flip bit", error_position(r), "-> data", decode(r)[0])
    print("minimum distance:", min_distance())
    print("single errors repaired: %d of %d" % single_error_success())
    print("double errors repaired: %d of %d" % double_error_success())
    for k in (1, 4, 8, 11, 26, 64, 120):
        print(f"k = {k:3d} data bits needs r = {min_parity_bits(k)} parity bits, rate {code_rate(k, min_parity_bits(k)):.3f}")

    fam = hamming_family(8)
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.8))
    axs[0].plot([f[0] for f in fam], [f[3] for f in fam], "o-")
    for f in fam:
        axs[0].annotate(f"({f[1]},{f[2]})", (f[0], f[3]), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=8)
    axs[0].axhline(1 / 3, color="gray", ls=":")
    axs[0].text(2.1, 0.355, "repeat each bit 3 times: rate 1/3", fontsize=8)
    axs[0].set_xlabel("parity bits r")
    axs[0].set_ylabel("code rate k / n")
    axs[0].set_ylim(0, 1)
    axs[0].set_title("Hamming codes (n, k): longer blocks cost less")
    axs[0].grid(alpha=0.3)

    axs[1].imshow(H, cmap="Blues", vmin=0, vmax=1.6)
    for i in range(3):
        for j in range(7):
            axs[1].text(j, i, str(H[i, j]), ha="center", va="center")
    axs[1].set_xticks(range(7))
    axs[1].set_xticklabels(["d1", "d2", "d3", "d4", "p1", "p2", "p3"])
    axs[1].set_yticks(range(3))
    axs[1].set_yticklabels(["check 1", "check 2", "check 3"])
    axs[1].set_xlabel("each column = the syndrome if that bit flips")
    axs[1].set_title("Parity-check matrix H")
    fig.tight_layout()
    fig.savefig(OUT / "rate_and_H.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.2, 3.6))
    ks = np.arange(1, 130)
    ax2.step(ks, [min_parity_bits(k) for k in ks], where="post")
    ax2.set_xlabel("data bits k in the block")
    ax2.set_ylabel("parity bits r needed")
    ax2.set_title("Protecting one error: 2^r >= k + r + 1")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "parity_bits_needed.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
