"""Session 3 (Level 3): a toy 2D matrix code, damaged by noise and bursts, and its decoding success rate.

This is NOT the QR standard. Real QR codes use Reed-Solomon codes over GF(256).

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a toy matrix code and how much damage it survives
# **A. Real-world problem.** A QR code on a parcel is scuffed, rained on and half covered by a
# sticker. It still scans. We build our own small 2D code (a *toy*, not the QR standard) and
# measure how much damage it survives, comparing the measurement with a probability formula.
#
# **Plan.** (1) message -> Hamming blocks -> squares in a grid with finder patterns,
# (2) damage it with random noise and with a burst, (3) decode, (4) success rate against the
# damage fraction versus theory, (5) interleaving against bursts, (6) a failure case.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

P = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 1, 1]])
G = np.hstack([np.eye(4, dtype=int), P])          # Session 2: 4 data bits -> 7 bits
H = np.hstack([P.T, np.eye(3, dtype=int)])
# syndrome (read as a 3-bit number) -> which of the 7 bits to flip back (-1 = none)
FIX = np.full(8, -1)
for _k in range(7):
    FIX[int(H[0, _k]) * 4 + int(H[1, _k]) * 2 + int(H[2, _k])] = _k


# %% [markdown]
# ## Step 1: from message to squares
# Message: 4 letters plus one *check byte* (their sum modulo 256, like the EAN check digit in
# Session 1). That is 40 bits = 10 nibbles of 4 bits. Each nibble becomes a 7-bit Hamming
# codeword, so 10 codewords = 70 bits.
#
# **Interleaving.** If codeword 0 sat in 7 neighbouring squares, one scratch across them would
# flip several of its bits and Hamming could not repair it. Instead we write the codewords as
# rows of a table and read the table down the columns, in groups of `group` codewords. Bits of
# one codeword are then `group` squares apart, so a burst of up to `group` squares hits each
# codeword at most once.

# %%
def message_bits(text):
    """4 letters + check byte -> 40 bits."""
    data = [ord(c) for c in text] + [sum(ord(c) for c in text) % 256]
    return np.array([(b >> k) & 1 for b in data for k in range(7, -1, -1)], dtype=int)


def bits_to_text(bits):
    """40 bits -> (text, check_ok)."""
    vals = [int("".join(map(str, bits[8 * i: 8 * i + 8])), 2) for i in range(len(bits) // 8)]
    return "".join(chr(v) for v in vals[:-1]), sum(vals[:-1]) % 256 == vals[-1]


def encode_blocks(bits):
    """Every 4 bits -> a 7-bit codeword. Returns an array of shape (C, 7)."""
    return (bits.reshape(-1, 4) @ G) % 2


def decode_blocks(words):
    """Syndrome decoding of an array (C, 7). Returns (data (C, 4), number of blocks that needed a fix)."""
    words = words.copy()
    s = (words @ H.T) % 2
    pos = FIX[s[:, 0] * 4 + s[:, 1] * 2 + s[:, 2]]
    rows = np.where(pos >= 0)[0]
    words[rows, pos[rows]] ^= 1
    return words[:, :4], len(rows)


def interleave(words, group):
    """Write `group` codewords as rows, read down the columns. group = 1 means no interleaving."""
    C = len(words)
    assert C % group == 0
    return np.concatenate([words[a:a + group].T.reshape(-1) for a in range(0, C, group)])


def deinterleave(stream, group, C):
    out = []
    for a in range(0, C, group):
        out.append(stream[7 * a: 7 * (a + group)].reshape(7, group).T)
    return np.vstack(out)


# %% [markdown]
# ## Step 2: the grid and its finder patterns
# A 12 x 12 grid. Three 3 x 3 *finder patterns* (a black ring around a white square) sit in three
# corners so a reader can find the code and its orientation; each has a white margin. The
# remaining 96 squares are *data squares*, read row by row. The first 70 carry the code bits;
# the last 26 are filler.

# %%
SIZE = 12
FINDER = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
FINDER_SPOTS = [(0, 0), (0, SIZE - 3), (SIZE - 3, 0)]


def reserved_mask():
    m = np.zeros((SIZE, SIZE), dtype=bool)
    m[0:4, 0:4] = True
    m[0:4, SIZE - 4:] = True
    m[SIZE - 4:, 0:4] = True
    return m


DATA_POS = [(r, c) for r in range(SIZE) for c in range(SIZE) if not reserved_mask()[r, c]]    # 96 squares
NBITS = 70


def make_grid(text, group=10):
    """Build the toy code for a 4-letter text."""
    words = encode_blocks(message_bits(text))
    stream = np.concatenate([interleave(words, group), np.tile([1, 0], 13)])      # 70 bits + 26 filler
    grid = np.zeros((SIZE, SIZE), dtype=int)
    for (r, c), b in zip(DATA_POS, stream):
        grid[r, c] = b
    for r0, c0 in FINDER_SPOTS:
        grid[r0:r0 + 3, c0:c0 + 3] = FINDER
    return grid


def finder_errors(grid):
    return int(sum((grid[r0:r0 + 3, c0:c0 + 3] != FINDER).sum() for r0, c0 in FINDER_SPOTS))


def read_grid(grid, group=10):
    """Decode a (possibly damaged) grid. Returns a dict with text, check_ok, fixed blocks, finder_ok."""
    f_err = finder_errors(grid)
    if f_err > 3:                                   # cannot even find the code
        return {"text": None, "check_ok": False, "fixed": 0, "finder_ok": False, "finder_errors": f_err}
    stream = np.array([grid[r, c] for r, c in DATA_POS[:NBITS]])
    words = deinterleave(stream, group, NBITS // 7)
    data, fixed = decode_blocks(words)
    text, ok = bits_to_text(data.reshape(-1))
    return {"text": text, "check_ok": ok, "fixed": fixed, "finder_ok": True, "finder_errors": f_err}


# %% [markdown]
# ## Step 3: damage
# *Random noise*: every data square flips independently with probability q (the damage
# fraction). *Burst*: `length` neighbouring squares in reading order flip, like a scratch.

# %%
def random_noise(grid, q, rng):
    g = grid.copy()
    flips = rng.random(len(DATA_POS)) < q
    for (r, c), f in zip(DATA_POS, flips):
        g[r, c] ^= int(f)
    return g


def burst_noise(grid, start, length):
    g = grid.copy()
    for r, c in DATA_POS[start:start + length]:
        g[r, c] ^= 1
    return g


def error_map(clean, damaged):
    """1 where a square differs from the clean code."""
    return (clean != damaged).astype(int)


# %% [markdown]
# ## Step 4: success rate versus damage, and the theory
# A Hamming block survives if it has at most 1 flipped bit out of 7:
# P_block = (1-q)^7 + 7 q (1-q)^6. The 10 blocks are independent, so the message survives with
# probability P_block^10. A repetition code that sends every bit n times (n odd) and takes a
# majority vote corrects up to (n-1)/2 flips per bit.

# %%
def block_ok_prob(q):
    return (1 - q) ** 7 + 7 * q * (1 - q) ** 6


def hamming_theory(q, blocks=10):
    return block_ok_prob(q) ** blocks


def repetition_theory(q, n, bits=40):
    """Probability that all `bits` bits survive an n-fold repetition code (n odd)."""
    from math import comb
    t = (n - 1) // 2
    bit_ok = sum(comb(n, j) * q ** j * (1 - q) ** (n - j) for j in range(t + 1))
    return bit_ok ** bits


def uncoded_theory(q, bits=40):
    return (1 - q) ** bits


def hamming_mc(q, trials, seed, blocks=10):
    """Fast Monte Carlo on the codewords (random noise only), decoding with decode_blocks."""
    rng = np.random.default_rng(seed)
    words = encode_blocks(rng.integers(0, 2, size=blocks * 4))
    good = 0
    for _ in range(trials):
        noisy = words ^ (rng.random(words.shape) < q).astype(int)
        data, _ = decode_blocks(noisy)
        good += np.array_equal(data, words[:, :4])
    return good / trials


def repetition_mc(q, n, trials, seed, bits=40):
    rng = np.random.default_rng(seed)
    flips = rng.random((trials, bits, n)) < q
    return float(np.mean(flips.sum(axis=2).max(axis=1) <= (n - 1) // 2))


def grid_success(q, trials, seed, text="OPEN", group=10):
    """End-to-end: build the grid, damage it, read it, and compare with the true text."""
    rng = np.random.default_rng(seed)
    grid = make_grid(text, group)
    good = accepted_wrong = 0
    for _ in range(trials):
        res = read_grid(random_noise(grid, q, rng), group)
        if res["text"] == text and res["check_ok"]:
            good += 1
        elif res["check_ok"] and res["text"] is not None:
            accepted_wrong += 1        # wrong text that still passed the check byte
    return good / trials, accepted_wrong / trials


# %% [markdown]
# ## Step 5: bursts and interleaving
# We try every possible start position of a burst of a given length and count how often the
# message is read correctly, with and without interleaving.

# %%
def burst_survival(group, length, text="OPEN"):
    grid = make_grid(text, group)
    starts = range(len(DATA_POS) - length + 1)
    good = 0
    for s in starts:
        res = read_grid(burst_noise(grid, s, length), group)
        good += res["text"] == text and res["check_ok"]
    return good / len(starts)


def guaranteed_burst(group, text="OPEN", maxlen=20):
    """Longest burst length L such that every burst of length 1..L at every position is repaired."""
    best = 0
    for L in range(1, maxlen + 1):
        if burst_survival(group, L, text) < 1.0:
            break
        best = L
    return best


# %% [markdown]
# ## Step 6: see it
# Figure 1: the clean code, the damaged code, the error map and the repaired code.
# Figure 2: success rate against damage fraction (theory lines, simulation dots).
# Figure 3: burst survival with and without interleaving.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    text = "OPEN"
    clean = make_grid(text, 10)
    rng = np.random.default_rng(7)
    damaged = burst_noise(clean, 20, 9)
    damaged = random_noise(damaged, 0.0, rng)
    res = read_grid(damaged, 10)
    print("burst of 9 squares -> read", res)
    repaired = make_grid(res["text"], 10) if res["text"] else clean
    fig, axs = plt.subplots(1, 4, figsize=(11, 3.1))
    for ax, g, title in zip(axs, [clean, damaged, error_map(clean, damaged), repaired],
                            ["clean code", "after a 9-square scratch", "error map (1 = wrong)", "repaired by decoding"]):
        ax.imshow(1 - g, cmap="gray", vmin=0, vmax=1)
        ax.set_title(title, fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(OUT / "toy_code_repair.png", dpi=120)

    qs = np.array([0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3])
    dense = np.linspace(0, 0.3, 120)
    print(" q      theory  hamming_mc  grid_mc | uncoded rep3  rep5")
    mc = []
    for i, q in enumerate(qs):
        m = hamming_mc(q, 4000, 100 + i)
        g, wrong = grid_success(q, 300, 200 + i) if q in (0.01, 0.02, 0.05, 0.1) else (float("nan"), 0)
        mc.append(m)
        print(f"{q:5.3f}  {hamming_theory(q):.4f}  {m:.4f}     {g:.4f}  | {uncoded_theory(q):.4f}  "
              f"{repetition_theory(q, 3):.4f}  {repetition_theory(q, 5):.4f}   false-accept {wrong:.3f}")
    fig2, ax2 = plt.subplots(figsize=(6.6, 4.0))
    ax2.plot(100 * dense, [hamming_theory(q) for q in dense], label="Hamming(7,4) x 10 blocks, 70 squares")
    ax2.plot(100 * dense, [repetition_theory(q, 3) for q in dense], label="repeat 3 times, 120 squares")
    ax2.plot(100 * dense, [repetition_theory(q, 5) for q in dense], label="repeat 5 times, 200 squares")
    ax2.plot(100 * dense, [uncoded_theory(q) for q in dense], "k--", label="no protection, 40 squares")
    ax2.plot(100 * qs, mc, "o", color="tab:blue", label="simulation (Hamming)")
    ax2.set_xlabel("damage fraction q (percent of squares flipped at random)")
    ax2.set_ylabel("probability the message is read correctly")
    ax2.set_title("Success versus damage: theory and simulation")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "success_vs_damage.png", dpi=120)

    lengths = list(range(1, 16))
    fig3, ax3 = plt.subplots(figsize=(6.6, 3.8))
    for g in (1, 2, 5, 10):
        ax3.plot(lengths, [100 * burst_survival(g, L) for L in lengths], "o-", label=f"group {g}")
        print(f"group {g:2d}: guaranteed burst length {guaranteed_burst(g)}")
    ax3.set_xlabel("burst length (neighbouring squares flipped)")
    ax3.set_ylabel("starts that are read correctly (percent)")
    ax3.set_title("Interleaving defeats bursts")
    ax3.legend(title="interleave group")
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "burst_interleaving.png", dpi=120)

    g, wrong = grid_success(0.15, 400, 5)
    print(f"failure case: at q = 0.15 only {g:.1%} read correctly (theory {hamming_theory(0.15):.1%}); false accepts {wrong:.1%}")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
