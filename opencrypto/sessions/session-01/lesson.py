"""Session 1 (Level 1): a secret message, the Caesar shift cipher, and why it is easy to break.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a secret message
# **A. Real-world problem.** You want to pass a note in class so that only your friend can
# read it. A very old trick, used by Julius Caesar, is to *shift* every letter along the
# alphabet by a fixed number. This is a **toy cipher**: it is perfect for learning and
# useless for protecting anything real. Today you encrypt and decrypt by hand and in code,
# then discover why anyone can break it in a minute.
#
# **Plan.** (1) shift letters with modular arithmetic, (2) decrypt, (3) try all shifts,
# (4) let the computer pick the readable one.

# %%
import pathlib
import string
import time

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ALPHABET = string.ascii_uppercase           # A..Z, 26 letters
MESSAGE = "MEET ME AT THE OLD GATE AT NOON"  # the secret note used in the app
COMMON = "ETAOINSHR"                         # the nine most common English letters


# %% [markdown]
# ## Step 1: shift a letter
# Number the letters A=0, B=1, ..., Z=25. Encrypting with key k means: new number =
# (old number + k) mod 26. "mod 26" means: after Z, wrap round to A.
#
# Check by hand with k = 3: H is 7, so 7 + 3 = 10, which is K. E is 4, so 7 -> K, 4 -> H.
# "HELLO" becomes "KHOOR". Y is 24, and 24 + 3 = 27, which wraps to 27 - 26 = 1, so Y -> B.

# %%
def shift_text(text, k):
    """Shift every letter by k places (k can be negative or larger than 25).
    Letters keep their case; spaces and punctuation are left alone."""
    out = []
    for ch in text:
        if ch.isalpha() and ch.isascii():
            base = ord("A") if ch.isupper() else ord("a")
            out.append(chr((ord(ch) - base + k) % 26 + base))
        else:
            out.append(ch)
    return "".join(out)


def caesar_encrypt(text, k):
    return shift_text(text, k)


def caesar_decrypt(text, k):
    return shift_text(text, -k)


# %% [markdown]
# ## Step 2: try every shift
# Shift 0 and shift 26 change nothing, so there are only **25** useful keys. An attacker
# does not need to be clever: write down all 25 shifts and read the one that makes sense.

# %%
def all_shifts(ciphertext):
    """Return [(k, text), ...] for k = 1..25: the ciphertext decrypted with each key."""
    return [(k, caesar_decrypt(ciphertext, k)) for k in range(1, 26)]


# %% [markdown]
# ## Step 3: let the computer read for us
# English uses some letters much more than others. The nine letters E T A O I N S H R make
# up most of normal English text, while a random mix of letters would give only 9/26,
# about 35 percent. A *readability score* = share of letters that are in COMMON.
# The right shift gives a high score; wrong shifts give low ones.

# %%
def readability(text):
    """Fraction of the letters of text that are among the nine common letters."""
    letters = [c for c in text.upper() if c in ALPHABET]
    if not letters:
        return 0.0
    return sum(c in COMMON for c in letters) / len(letters)


def score_by_guess(ciphertext):
    """Readability of the ciphertext decrypted with each guess 0..25 (26 numbers)."""
    return [readability(caesar_decrypt(ciphertext, g)) for g in range(26)]


def best_shift(ciphertext):
    """The guess (0..25) whose decryption looks most like English."""
    scores = score_by_guess(ciphertext)
    return max(range(26), key=lambda g: scores[g])


def time_to_try_all(ciphertext):
    """Seconds the computer needs to decrypt with all 25 keys and score them."""
    t0 = time.perf_counter()
    best_shift(ciphertext)
    return time.perf_counter() - t0


# %% [markdown]
# ## Step 4: see it
# Left: the two alphabet rows (plain on top, cipher below) for key 3. Right: the
# readability score for each of the 26 guesses on a message encrypted with key 3. Only one
# guess stands out: the right one.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    key = 3
    ct = caesar_encrypt(MESSAGE, key)
    print("message   :", MESSAGE)
    print("ciphertext:", ct)
    print("HELLO with key 3 ->", caesar_encrypt("HELLO", 3))
    print("best guess:", best_shift(ct), " time to try all keys: %.5f s" % time_to_try_all(ct))
    for k, t in all_shifts(ct)[:5]:
        print(f"  key {k:2d}: {t}")
    sc = score_by_guess(ct)
    print("score at the right guess: %.3f ; best wrong guess: %.3f" % (sc[key], max(s for g, s in enumerate(sc) if g != key)))

    fig, ax = plt.subplots(figsize=(8, 2.6))
    for i, ch in enumerate(ALPHABET):
        ax.text(i, 1, ch, ha="center", va="center", fontsize=12)
        ax.text(i, 0, ALPHABET[(i + key) % 26], ha="center", va="center", fontsize=12, color="tab:red")
        ax.plot([i, i], [0.25, 0.75], color="gray", lw=0.6)
    ax.text(-1.2, 1, "plain", ha="right", va="center")
    ax.text(-1.2, 0, "cipher", ha="right", va="center", color="tab:red")
    ax.set_xlim(-3.5, 25.8)
    ax.set_ylim(-0.5, 1.5)
    ax.axis("off")
    ax.set_title("Caesar cipher with key 3: every letter moves 3 places along")
    fig.tight_layout()
    fig.savefig(OUT / "caesar_wheel.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.bar(range(26), [100 * s for s in sc], color=["tab:red" if g == key else "tab:gray" for g in range(26)])
    ax2.set_xlabel("guessed key (shift used to decrypt)")
    ax2.set_ylabel("readability score (% common letters)")
    ax2.set_title("Trying all shifts: only the right key reads as English")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "try_all_shifts.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Remember: Caesar is a toy. Real systems use vetted libraries, never home-made
# ciphers.
