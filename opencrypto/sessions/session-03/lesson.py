"""Session 3 (Level 3): one-time pad, toy stream cipher, hashing, HMAC, key size, and a Vigenere break.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: perfect secrecy, hashes, and why key size matters
# **A. Real-world problem.** Which kinds of secret-keeping are unbreakable, which are only
# hard, and how do we check that a message was not changed on the way? You will study toy
# versions of: the one-time pad, a stream cipher with a short key, SHA-256 hashing, salted
# password hashes and HMAC, and put a number on "how long would it take to try every key".
#
# **Safety note.** Everything here is for learning on toy data. Real systems must use
# vetted libraries and protocols written and reviewed by experts. Never invent your own
# cryptography to protect anything that matters. (`random` and numpy generators below are
# for reproducible demos only; real keys come from `secrets` or `os.urandom`.)

# %%
import hashlib
import hmac
import math
import pathlib
import secrets
import string
import time

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SECONDS_PER_YEAR = 365.25 * 24 * 3600


# %% [markdown]
# ## Step 1: XOR and the one-time pad
# XOR (written ^) combines two bits: 0^0=0, 0^1=1, 1^0=1, 1^1=0. Two facts matter:
# x ^ k ^ k = x (doing it twice undoes it), and if k is truly random then x ^ k is also
# completely random. The **one-time pad** encrypts a message by XOR with a truly random key
# that is as long as the message and used **once**. Then the ciphertext tells an attacker
# nothing at all (perfect secrecy): for any guessed plaintext of the same length, some key
# would have produced exactly this ciphertext.

# %%
def xor_bytes(a, b):
    """XOR two byte strings of equal length."""
    if len(a) != len(b):
        raise ValueError("XOR needs equal lengths")
    return bytes(x ^ y for x, y in zip(a, b))


def otp_key(n):
    """n truly random bytes from the operating system."""
    return secrets.token_bytes(n)


def otp_encrypt(message, key):
    return xor_bytes(message, key)


def otp_decrypt(ciphertext, key):
    return xor_bytes(ciphertext, key)


def key_that_explains(ciphertext, wanted_plaintext):
    """The key that would turn wanted_plaintext into this ciphertext. It exists for EVERY
    plaintext of the right length, which is why the ciphertext alone reveals nothing."""
    return xor_bytes(ciphertext, wanted_plaintext)


# %% [markdown]
# ## Step 2: the failure case, reusing the pad
# Suppose two messages p1 and p2 are encrypted with the same key k. Then
# c1 ^ c2 = (p1 ^ k) ^ (p2 ^ k) = p1 ^ p2: **the key cancels**. What is left is the XOR of
# two English texts, which still has the structure of English. If a part of p1 is known or
# guessed, the same part of p2 falls out immediately.

# %%
def reuse_leak(c1, c2):
    """What an eavesdropper gets for free when a pad is used twice: p1 XOR p2."""
    return xor_bytes(c1, c2)


def crib_reveal(c1, c2, guess, pos):
    """If the bytes `guess` sit at position pos in p1, return the bytes at that position in p2."""
    return xor_bytes(reuse_leak(c1, c2)[pos:pos + len(guess)], guess)


# %% [markdown]
# ## Step 3: a toy stream cipher and its short key
# A stream cipher stretches a short key (the *seed*) into a long keystream with a
# pseudo-random generator, then XORs it with the message. Our toy generator is a linear
# congruential generator. It is **not secure**; it shows what a small key space means.
# A 16-bit seed has only 2^16 = 65536 values, so we can try them all.

# %%
def keystream(seed, n):
    """n pseudo-random bytes from a 16-bit seed (toy LCG; NOT secure)."""
    x = seed & 0xFFFF
    out = bytearray()
    for _ in range(n):
        x = (1103515245 * x + 12345) % (2 ** 31)
        out.append((x >> 16) & 0xFF)
    return bytes(out)


def stream_encrypt(data, seed):
    return xor_bytes(data, keystream(seed, len(data)))


stream_decrypt = stream_encrypt          # XOR with the same keystream undoes it


def brute_force_seed(ciphertext, known_start):
    """Try every 16-bit seed; keep those whose decryption begins with known_start.
    Returns (list_of_seeds, number_of_tries)."""
    n = len(known_start)
    found = [s for s in range(2 ** 16) if stream_decrypt(ciphertext[:n], s) == known_start]
    return found, 2 ** 16


def seconds_to_exhaust(bits, rate):
    """Seconds to try all 2^bits keys at `rate` guesses per second (the average is half)."""
    return 2.0 ** bits / rate


def years(seconds):
    return seconds / SECONDS_PER_YEAR


def bits_needed(target_seconds, rate):
    """Smallest whole number of key bits so that trying every key takes at least target_seconds."""
    return math.ceil(math.log2(target_seconds * rate))


# %% [markdown]
# ## Step 4: hashing and the avalanche effect
# A hash function (SHA-256) turns any input into 256 bits. Good hashes show the
# **avalanche effect**: flip one input bit and about half of the 256 output bits change.

# %%
def sha256_bits(data):
    return int.from_bytes(hashlib.sha256(data).digest(), "big")


def bit_difference(a, b):
    """Number of differing bits between two non-negative integers."""
    return bin(a ^ b).count("1")


def avalanche_samples(samples=2000, size=32, seed=0):
    """For random messages, flip one random input bit; return the 256-bit differences."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(samples):
        msg = bytearray(rng.integers(0, 256, size=size, dtype=np.uint8).tobytes())
        flipped = bytearray(msg)
        bit = int(rng.integers(0, size * 8))
        flipped[bit // 8] ^= 1 << (bit % 8)
        out.append(bit_difference(sha256_bits(bytes(msg)), sha256_bits(bytes(flipped))))
    return np.array(out)


# %% [markdown]
# ## Step 5: storing passwords: salt and PBKDF2
# A site should never store passwords. It stores a hash. But if the hash is plain SHA-256,
# one precomputed table (hash -> password) for a dictionary of likely passwords cracks every
# user at once, and equal passwords show up as equal hashes. A **salt** is a random value,
# different for every user and stored beside the hash; the hash is computed from salt and
# password together. A precomputed table is then useless, because it would need a separate
# table for every possible salt. **PBKDF2** repeats the hashing many times to make each
# guess slow. Here we use few repetitions so the lesson runs fast; real systems use far
# more and follow current guidance from a vetted library.

# %%
DICTIONARY = ["sunrise", "tiger99", "violet", "lemon22", "monsoon", "rocket7", "banyan", "pebble"]
USERS = {"alice": "sunrise", "bob": "tiger99", "carol": "sunrise", "dave": "violet", "erin": "lemon22"}
ITERATIONS = 1000


def unsalted_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def salted_hash(password, salt, iterations=ITERATIONS):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations).hex()


def precomputed_table(dictionary):
    """The attacker's table: hash -> password, built once."""
    return {unsalted_hash(w): w for w in dictionary}


def store_unsalted(users):
    return {u: unsalted_hash(p) for u, p in users.items()}


def store_salted(users):
    records = {}
    for u, p in users.items():
        salt = secrets.token_bytes(16)
        records[u] = (salt, salted_hash(p, salt))
    return records


def crack_with_table(stored_hashes, table):
    """Users whose stored hash is found in the table."""
    return {u: table[h] for u, h in stored_hashes.items() if h in table}


def crack_salted_by_search(records, dictionary):
    """Without a table the attacker must hash every dictionary word for every user (no early stop):
    returns (cracked users, number of hashes computed)."""
    cracked, work = {}, 0
    for u, (salt, h) in records.items():
        for w in dictionary:
            work += 1
            if salted_hash(w, salt) == h:
                cracked[u] = w
    return cracked, work


# %% [markdown]
# ## Step 6: integrity with HMAC
# A hash alone does not prove who made a message: anyone can compute SHA-256 of a changed
# message. **HMAC** mixes a secret key into the hash, so only holders of the key can make a
# valid tag. Compare tags with `hmac.compare_digest`, which takes the same time whatever the
# position of the first difference, so timing leaks nothing.

# %%
def make_tag(key, message):
    return hmac.new(key, message, hashlib.sha256).digest()


def check_tag(key, message, tag):
    return hmac.compare_digest(make_tag(key, message), tag)


# %% [markdown]
# ## Step 7: key size against brute-force time
# At an assumed rate of 10^12 guesses per second (an assumption, not a measurement of any
# real machine), the time to try all 2^b keys is 2^b / 10^12 seconds.

# %%
RATE = 1e12


def key_size_table(sizes=(40, 56, 80, 128), rate=RATE):
    return [(b, 2.0 ** b, seconds_to_exhaust(b, rate)) for b in sizes]


# %% [markdown]
# ## Step 8: mini-project, break a Vigenere ciphertext
# Find the key length with the index of coincidence, then each key letter with the letter
# frequencies of English (as in Session 2). The ciphertext is generated here, so you can
# check your answer.

# %%
ALPHABET = string.ascii_uppercase
ENGLISH_PCT = np.array([8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4,
                        6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074])
EN = ENGLISH_PCT / ENGLISH_PCT.sum()
MINI_TEXT = (
    "The harbor of the small town woke before the sun. Fishermen carried nets down the stone "
    "steps, and gulls circled above the boats, waiting for scraps. At the end of the long pier "
    "stood the old lighthouse, painted in red and white stripes that had faded after many "
    "winters of salt and wind. The keeper, a quiet woman named Mira, climbed the narrow stairs "
    "each evening to light the great lamp. She had done this for thirty years, and she knew "
    "every step by touch. One night a storm rolled in from the north, and the waves rose higher "
    "than the pier. The boats were still out. Mira turned the lamp slowly, so that its beam "
    "swept across the dark water again and again, showing the captains the safe path between "
    "the rocks. Hour after hour she stayed at her post, and one by one the little boats found "
    "the channel and slid into the harbor. By morning the wind had died, and the town gathered "
    "on the pier to count the boats. All of them had returned. Nobody made a speech, because "
    "nobody needed to. A boy brought her a cup of hot tea, and an old fisherman nodded his "
    "thanks. Mira smiled, rubbed her tired eyes, and said that the lamp had done the work. "
    "Then she went home to sleep while the sun rose over the quiet water, bright and warm, and "
    "the town began another ordinary day."
)
MINI_KEY = "BEACON"


def clean(text):
    return [ALPHABET.index(c) for c in text.upper() if c in ALPHABET]


def vig(text, key, sign):
    k = clean(key)
    return "".join(ALPHABET[(v + sign * k[i % len(k)]) % 26] for i, v in enumerate(clean(text)))


def mini_ciphertext():
    """The self-generated challenge: MINI_TEXT encrypted with a secret Vigenere key."""
    return vig(MINI_TEXT, MINI_KEY, +1)


def ic(values):
    counts = np.bincount(values, minlength=26)
    n = counts.sum()
    return float((counts * (counts - 1)).sum() / (n * (n - 1))) if n > 1 else 0.0


def find_key_length(values, max_len=12, threshold=0.062):
    for m in range(1, max_len + 1):
        if np.mean([ic(values[i::m]) for i in range(m)]) > threshold:
            return m
    return None


def find_shift(column):
    counts = np.bincount(column, minlength=26).astype(float)
    n = counts.sum()
    chi = [(((np.roll(counts, -s) - n * EN) ** 2) / (n * EN)).sum() for s in range(26)]
    return int(np.argmin(chi))


def break_vigenere(ciphertext):
    """Return (key_length, key, plaintext) found from the ciphertext alone."""
    v = np.array(clean(ciphertext))
    m = find_key_length(v)
    key = "".join(ALPHABET[find_shift(v[i::m])] for i in range(m))
    return m, key, vig(ciphertext, key, -1)


# %% [markdown]
# ## Step 9: see it
# Figure 1: bit differences after flipping one input bit, over many samples, centred near
# 128 of 256. Figure 2: brute-force time against key bits at the assumed rate.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    msg1 = b"MEET AT NOON AT THE GATE"
    msg2 = b"BRING THE MAP AND A LAMP"
    key = otp_key(len(msg1))
    c1, c2 = otp_encrypt(msg1, key), otp_encrypt(msg2, key)
    print("pad reuse: c1^c2 equals p1^p2:", reuse_leak(c1, c2) == xor_bytes(msg1, msg2))
    print("crib 'MEET' at 0 reveals:", crib_reveal(c1, c2, b"MEET", 0))

    seed = 40503
    sct = stream_encrypt(b"HDR: the plan is ready", seed)
    t0 = time.perf_counter()
    found, tries = brute_force_seed(sct, b"HDR:")
    print("16-bit seed found:", found, "after", tries, "tries in %.3f s" % (time.perf_counter() - t0))
    print("2^40 tries at 1e6 per second: %.2f days" % (seconds_to_exhaust(40, 1e6) / 86400))

    d = avalanche_samples()
    print("avalanche: mean %.1f bits, std %.1f, min %d, max %d" % (d.mean(), d.std(), d.min(), d.max()))

    table = precomputed_table(DICTIONARY)
    print("unsalted, cracked by one table:", len(crack_with_table(store_unsalted(USERS), table)), "of", len(USERS))
    recs = store_salted(USERS)
    print("salted, cracked by the same table:", len(crack_with_table({u: h for u, (s, h) in recs.items()}, table)))
    cracked, work = crack_salted_by_search(recs, DICTIONARY)
    print("salted, per-user search:", len(cracked), "cracked using", work, "hashes")

    k = secrets.token_bytes(32)
    tag = make_tag(k, b"pay 100 to alice")
    print("HMAC ok:", check_tag(k, b"pay 100 to alice", tag), " tampered:", check_tag(k, b"pay 900 to alice", tag))

    for b, n, s in key_size_table():
        print(f"{b:4d} bits: {n:.3e} keys, {s:.3e} s = {years(s):.3e} years")

    m, kk, plain = break_vigenere(mini_ciphertext())
    print("mini-project: key length", m, "key", kk)

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.hist(d, bins=range(int(d.min()), int(d.max()) + 2), color="tab:blue", alpha=0.8)
    ax.axvline(128, color="k", ls=":")
    ax.set_xlabel("output bits changed (out of 256)")
    ax.set_ylabel("number of samples")
    ax.set_title("SHA-256 avalanche: one flipped input bit changes about half the output")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "avalanche.png", dpi=120)

    bits = np.arange(16, 129)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.plot(bits, [math.log10(seconds_to_exhaust(b, RATE)) for b in bits], color="tab:red")
    ax2.axhline(math.log10(SECONDS_PER_YEAR), color="k", ls=":", label="one year")
    for b in (40, 56, 80, 128):
        ax2.plot(b, math.log10(seconds_to_exhaust(b, RATE)), "ko")
    ax2.set_xlabel("key size (bits)")
    ax2.set_ylabel("log10 of seconds to try every key (10^12 guesses/s)")
    ax2.set_title("Each extra bit doubles the work")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "key_size_vs_time.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Real systems: vetted libraries only.
