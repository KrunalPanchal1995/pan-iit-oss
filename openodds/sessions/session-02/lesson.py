"""Session 2 (Level 2): counting rules, poker hands, birthdays and expected value.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: counting rules, birthdays and expected value
# **A. Real-world problem.** How likely is a pair in a 5-card hand? Do 23 people in a room
# really have a 50 percent chance of sharing a birthday? Could a school fair raffle break even?
# One rule answers all: count the favourable outcomes and divide by the total.
#
# *Education about chance only. The raffle and prizes are made-up; this is not betting advice.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: probability = favourable / total, and independent events multiply
# If all outcomes are equally likely, P(event) = favourable / total. If two events do not
# influence each other (independent), P(both) = P(first) x P(second).
# Order matters for a *permutation*: n!/(n-k)! ways to line up k of n things.
# Order does not matter for a *combination*: C(n, k) = n!/(k!(n-k)!), read "n choose k".

# %%
def probability(favourable, total):
    if total <= 0:
        raise ValueError("total must be positive")
    return favourable / total


def permutations(n, k):
    """Ordered ways to pick k from n."""
    return math.perm(n, k)


def combinations(n, k):
    """Unordered ways to pick k from n (0 if k > n)."""
    return math.comb(n, k) if 0 <= k <= n else 0


# %% [markdown]
# ## Step 2: a 5-card poker hand
# A deck has 52 cards: 13 ranks in 4 suits. A hand is a combination, so there are C(52, 5)
# hands, all equally likely.
#  * One pair (exactly two cards of one rank, the other three cards of three different ranks):
#    choose the rank 13, choose 2 of its 4 suits C(4,2), choose 3 other ranks C(12,3), choose a
#    suit for each of them 4^3.
#  * Flush (all five cards of one suit, straight flushes included): 4 suits x C(13, 5).

# %%
def poker_counts():
    total = combinations(52, 5)
    pair = 13 * combinations(4, 2) * combinations(12, 3) * 4 ** 3
    flush = 4 * combinations(13, 5)
    return {"total": total, "one pair": pair, "flush": flush}


# %% [markdown]
# ## Step 3: the birthday problem
# Ignore leap years and assume all 365 days are equally likely. The chance that n people all
# have different birthdays is (365/365) x (364/365) x ... x ((365-n+1)/365), because each new
# person must avoid the days already taken. Then P(shared) = 1 - that.

# %%
def birthday_shared(n, days=365):
    """Probability that at least two of n people share a birthday."""
    if n > days:
        return 1.0
    p_all_different = 1.0
    for i in range(n):
        p_all_different *= (days - i) / days
    return 1.0 - p_all_different


# %% [markdown]
# ## Step 4: expected value and a fair game
# Expected value = sum of (value x probability). It is the long-run average per play.
# A game is *fair* (breaks even) when the expected net gain is 0.

# %%
def expected_value(values, probs):
    if abs(sum(probs) - 1.0) > 1e-9:
        raise ValueError("probabilities must add up to 1")
    return float(sum(v * p for v, p in zip(values, probs)))


def raffle_net_gain(tickets, price, prize):
    """Expected net gain for one ticket: win the prize with probability 1/tickets, always pay the price."""
    return expected_value([prize - price, -price], [1 / tickets, 1 - 1 / tickets])


def break_even_prize(tickets, price):
    """Prize that makes the expected net gain of one ticket exactly 0."""
    return tickets * price


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    c = poker_counts()
    for name in ("one pair", "flush"):
        print(f"{name}: {c[name]} of {c['total']} hands = {c[name] / c['total']:.6f}")
    print(f"birthday, 23 people: {birthday_shared(23):.4f}")
    print(f"raffle 500 tickets at Rs 20: break-even prize Rs {break_even_prize(500, 20)}")

    n = np.arange(1, 61)
    pb = np.array([birthday_shared(int(k)) for k in n])
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(n, pb)
    ax.axhline(0.5, color="gray", ls=":")
    ax.plot([23], [birthday_shared(23)], "ro")
    ax.annotate("23 people: 0.507", (23, birthday_shared(23)), textcoords="offset points", xytext=(10, -15))
    ax.set_xlabel("number of people in the room")
    ax.set_ylabel("probability two share a birthday")
    ax.set_title("The birthday curve")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "birthday.png", dpi=120)

    labels = ["one pair", "flush"]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(labels, [c[k] / c["total"] for k in labels], color=["#2a9d8f", "#e9a23b"])
    ax2.set_ylabel("probability of the hand")
    ax2.set_title("5-card hands: pair is common, flush is rare")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "poker.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
