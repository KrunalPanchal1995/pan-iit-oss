"""Session 2 (Level 2): keys, key space, frequency analysis and the Vigenere cipher.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the key, the key space, and breaking a substitution cipher
# **A. Real-world problem.** Caesar has only 25 keys. What if we allow *any* rearrangement
# of the alphabet as the key? There are about 4 x 10^26 of them, far too many to try one by
# one. Is that safe? You will count the keys, then break the cipher anyway by counting
# letters, then meet the Vigenere cipher, the classic attempt to fix the weakness.
#
# **Kerckhoffs's principle.** A cipher should stay secure even if the attacker knows
# everything about the method; only the *key* is secret. So we always assume the attacker
# has our code. All of this is a toy study: real systems use vetted libraries.

# %%
import math
import pathlib
import string

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ALPHABET = string.ascii_uppercase

# Standard textbook letter frequencies of English, in percent, for A..Z.
ENGLISH_PCT = np.array([8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4,
                        6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074])
ENGLISH = ENGLISH_PCT / ENGLISH_PCT.sum()          # as probabilities that add to 1

# A short passage written for this course (plain English, about 1300 letters).
SAMPLE = (
    "A secret is only as safe as the key that protects it. Long ago, people sent messages by "
    "hand, and a message that was lost or stolen could be read by anyone who found it. So they "
    "began to hide the meaning by changing the letters. The simplest idea is to replace every "
    "letter by another letter, always in the same way. A friend who knows the rule can turn the "
    "strange letters back into words, but a stranger sees only nonsense. Or so it seems. The "
    "trouble is that language has habits. In English the letter e appears far more often than "
    "the letter z, and the short words the, and, and of appear again and again. If every e in a "
    "message becomes the same strange symbol, then that symbol will also appear again and again, "
    "and a patient reader will notice it. Count the symbols, line them up with the usual order "
    "of letters, and the first guesses come quickly. Each right guess reveals more of the text, "
    "and the text itself helps with the next guess, because a half-built word is easy to "
    "finish. This is why clever people do not rely on keeping the method hidden. They assume "
    "that the other side knows exactly how the machine works, and they put all the strength "
    "into the key. A good key is long, it is chosen without any pattern, and it is never used "
    "twice in a careless way. A short key, or a key made from a favourite word, can be searched "
    "by a computer in the time it takes to blink. Learning how a toy cipher breaks teaches us "
    "why real systems are built by experts, tested in public for many years, and used through "
    "trusted libraries. Nobody should invent a home-made scheme to guard something that "
    "matters, because the person who invents it is the last person able to find its flaws."
)


def letters_only(text):
    """Upper-case letters of text with everything else removed."""
    return "".join(c for c in text.upper() if c in ALPHABET)


# %% [markdown]
# ## Step 1: count the keys (the key space)
# The **key space** is the number of different keys. For a Caesar cipher it is 25 useful
# shifts. For a general **substitution cipher** the key is a rearrangement (permutation) of
# the 26 letters: 26 choices for A, 25 for B, ... so 26! = 26 x 25 x ... x 1 keys.
# We also express a key space in **bits**: bits = log2(number of keys).

# %%
def keyspace_caesar():
    return 25


def keyspace_substitution():
    return math.factorial(26)


def key_bits(n_keys):
    """Bits of key needed to name one of n_keys equally likely keys."""
    return math.log2(n_keys)


def keyspace_vigenere(m):
    """Number of Vigenere keys of length m (each of m letters free): 26^m."""
    return 26 ** m


# %% [markdown]
# ## Step 2: a substitution cipher, and a letter counter
# The key is a string of 26 letters: plain A becomes key[0], plain B becomes key[1], ...
# Because every plain letter always becomes the same cipher letter, the *shape* of the
# letter counts survives. That is the leak.

# %%
def random_substitution_key(seed):
    rng = np.random.default_rng(seed)
    return "".join(rng.permutation(list(ALPHABET)))


def substitute(text, key):
    """Encrypt: plain letter -> key letter. Non-letters are dropped, text is upper-cased."""
    table = {p: c for p, c in zip(ALPHABET, key)}
    return "".join(table[c] for c in letters_only(text))


def unsubstitute(text, key):
    table = {c: p for p, c in zip(ALPHABET, key)}
    return "".join(table[c] for c in letters_only(text))


def letter_counts(text):
    """How many times each of A..Z occurs (array of 26 integers)."""
    t = letters_only(text)
    return np.array([t.count(c) for c in ALPHABET])


def letter_percent(text):
    c = letter_counts(text)
    return 100.0 * c / c.sum()


# %% [markdown]
# ## Step 3: frequency analysis
# Sort the cipher letters from most to least common and match them, in that order, with the
# English letters sorted the same way (E T A O I N ...). The most common cipher letter is
# probably E, and so on. This guess is right for the common letters and shaky for the rare
# ones, but it already makes the text half readable.

# %%
def rank_match_key(ciphertext):
    """Guess a decryption key by matching letter ranks. Returns a 26-letter string K where
    cipher letter ALPHABET[i] is decrypted to K[i]."""
    cipher_rank = np.argsort(-letter_counts(ciphertext), kind="stable")
    english_rank = np.argsort(-ENGLISH, kind="stable")
    guess = [""] * 26
    for c, e in zip(cipher_rank, english_rank):
        guess[c] = ALPHABET[e]
    return "".join(guess)


def apply_decryption_key(ciphertext, dkey):
    table = {c: p for c, p in zip(ALPHABET, dkey)}
    return "".join(table[c] for c in letters_only(ciphertext))


def true_decryption_key(key):
    """The decryption key (cipher letter -> plain letter) for an encryption key."""
    out = [""] * 26
    for p, c in zip(ALPHABET, key):
        out[ALPHABET.index(c)] = p
    return "".join(out)


def key_accuracy(guess, truth):
    """Fraction of the 26 key positions that are right."""
    return sum(a == b for a, b in zip(guess, truth)) / 26


def text_accuracy(guess_text, true_text):
    """Fraction of letters of the decrypted text that are right."""
    return sum(a == b for a, b in zip(guess_text, true_text)) / len(true_text)


# %% [markdown]
# ## Step 4: Vigenere, and the index of coincidence
# Vigenere uses a *word* as key: letter i of the message is shifted by letter (i mod m) of
# the key (A=0, B=1, ...). Now the letter E no longer always becomes the same letter, so
# simple counting fails. But the key repeats every m letters, so every m-th letter of the
# ciphertext (a *column*) is just a Caesar cipher.
#
# **Index of coincidence (IC)**: the chance that two letters picked at random from the text
# are equal, IC = sum n_i (n_i - 1) / (N (N - 1)). English text gives about 0.067; random
# letters give 1/26 = 0.038. If we split a ciphertext into m columns and each column has
# IC near 0.067, then m is probably the key length.

# %%
def vigenere(text, key, sign=1):
    t = letters_only(text)
    k = [ALPHABET.index(c) for c in key.upper()]
    return "".join(ALPHABET[(ALPHABET.index(c) + sign * k[i % len(k)]) % 26] for i, c in enumerate(t))


def vigenere_encrypt(text, key):
    return vigenere(text, key, +1)


def vigenere_decrypt(text, key):
    return vigenere(text, key, -1)


def index_of_coincidence(text):
    c = letter_counts(text)
    n = int(c.sum())
    if n < 2:
        return 0.0
    return float((c * (c - 1)).sum() / (n * (n - 1)))


def ic_for_length(ciphertext, m):
    """Average IC of the m columns when the ciphertext is cut every m letters."""
    t = letters_only(ciphertext)
    return float(np.mean([index_of_coincidence(t[i::m]) for i in range(m)]))


def guess_key_length(ciphertext, max_len=12, threshold=0.062):
    """Smallest length whose columns look like English (average IC above the threshold)."""
    for m in range(1, max_len + 1):
        if ic_for_length(ciphertext, m) > threshold:
            return m
    return None


def column_shift(column):
    """Best Caesar shift for one column: the shift whose decrypted letter counts are
    closest to English (smallest chi-squared distance)."""
    counts = letter_counts(column).astype(float)
    n = counts.sum()
    best, best_chi = 0, float("inf")
    for s in range(26):
        decrypted = np.roll(counts, -s)            # decrypted[j] = counts[(j + s) % 26]
        chi = float((((decrypted - n * ENGLISH) ** 2) / (n * ENGLISH)).sum())
        if chi < best_chi:
            best, best_chi = s, chi
    return best


def recover_key(ciphertext, m):
    t = letters_only(ciphertext)
    return "".join(ALPHABET[column_shift(t[i::m])] for i in range(m))


# %% [markdown]
# ## Step 5: a design problem, by simulation
# How long must a Vigenere key be, for a message of n letters, before this attack stops
# working? We generate random English-like text (letters drawn with the English
# frequencies), encrypt with a random key of length m, run the attack with the right key
# length, and count how often the whole key is recovered.

# %%
def english_like_text(n, rng):
    return "".join(rng.choice(list(ALPHABET), size=n, p=ENGLISH))


def random_text(n, rng):
    return "".join(rng.choice(list(ALPHABET), size=n))


def success_rate(n, m, trials=200, seed=1):
    """Share of trials in which recover_key(ciphertext, m) returns the exact key."""
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(trials):
        key = "".join(rng.choice(list(ALPHABET), size=m))
        ct = vigenere_encrypt(english_like_text(n, rng), key)
        wins += recover_key(ct, m) == key
    return wins / trials


# %% [markdown]
# ## Step 6: see it
# Figure 1: cipher letter counts (sorted) next to English. Figure 2: the average IC for each
# guessed key length of a Vigenere ciphertext; it jumps up at the true length and its
# multiples. Figure 3: success rate against letters per column.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    plain = letters_only(SAMPLE)
    print("letters in the sample:", len(plain))
    print("Caesar keys:", keyspace_caesar(), " substitution keys 26! =", f"{keyspace_substitution():.3e}",
          " bits: %.1f" % key_bits(keyspace_substitution()))
    smallest = next(m for m in range(1, 40) if keyspace_vigenere(m) > keyspace_substitution())
    print("smallest Vigenere key length with more keys than 26!:", smallest)

    key = random_substitution_key(7)
    ct = substitute(SAMPLE, key)
    guess = rank_match_key(ct)
    truth = true_decryption_key(key)
    dec = apply_decryption_key(ct, guess)
    print("ciphertext start:", ct[:60])
    print("rank-match key accuracy: %.2f, text accuracy: %.2f" % (key_accuracy(guess, truth), text_accuracy(dec, plain)))
    print("decrypted start :", dec[:60])
    print("true start      :", plain[:60])
    print("IC of the sample: %.4f ; IC of random letters: %.4f" % (
        index_of_coincidence(plain), index_of_coincidence(random_text(20000, np.random.default_rng(3)))))
    print("sum of squared English probabilities: %.4f" % float((ENGLISH ** 2).sum()))

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    axs[0].bar(range(26), letter_percent(ct), color="tab:red")
    axs[0].set_xticks(range(26), list(ALPHABET), fontsize=7)
    axs[0].set_title("Ciphertext letter counts (shuffled)")
    axs[1].bar(range(26), letter_percent(dec), color="tab:blue", label="after rank matching")
    axs[1].plot(range(26), ENGLISH_PCT, "k.", label="English")
    axs[1].set_xticks(range(26), list(ALPHABET), fontsize=7)
    axs[1].set_title("Decrypted with the rank-match guess")
    axs[1].legend()
    for a in axs:
        a.set_xlabel("letter")
        a.grid(alpha=0.3)
    axs[0].set_ylabel("share of text (%)")
    fig.tight_layout()
    fig.savefig(OUT / "frequency_analysis.png", dpi=120)

    vkey = "ORCHID"
    vct = vigenere_encrypt(SAMPLE, vkey)
    ics = [ic_for_length(vct, m) for m in range(1, 19)]
    print("IC by guessed length:", " ".join(f"{m}:{v:.3f}" for m, v in enumerate(ics, 1)))
    print("guessed key length:", guess_key_length(vct), " recovered key:", recover_key(vct, guess_key_length(vct)))
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.bar(range(1, 19), ics, color=["tab:red" if m % len(vkey) == 0 else "tab:gray" for m in range(1, 19)])
    ax2.axhline(0.067, color="k", ls=":")
    ax2.axhline(0.038, color="k", ls=":")
    ax2.set_xlabel("guessed key length m")
    ax2.set_ylabel("average index of coincidence of the m columns")
    ax2.set_title("IC jumps at the true key length (6) and its multiples")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "ic_by_length.png", dpi=120)

    n = 300
    ms = [1, 2, 3, 5, 8, 12, 20, 30]
    rates = [success_rate(n, m, trials=150) for m in ms]
    print("success rate, n = 300:", {m: round(r, 2) for m, r in zip(ms, rates)})
    fig3, ax3 = plt.subplots(figsize=(6.5, 4))
    ax3.plot([n / m for m in ms], [100 * r for r in rates], "o-")
    ax3.set_xscale("log")
    ax3.set_xlabel("letters per column (n / m)")
    ax3.set_ylabel("key fully recovered (% of trials)")
    ax3.set_title("Longer keys starve each column of letters (n = 300)")
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "success_vs_letters.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
