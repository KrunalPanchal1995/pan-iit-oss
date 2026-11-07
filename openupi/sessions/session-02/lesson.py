"""Session 2 (Level 2): a double-entry ledger, atomic payments and idempotent retries.

Run:  python start.py 2

A simplified teaching model. Real banks add many more rules, audits and legal duties.
"""
# %% [markdown]
# # Session 2: the ledger behind a payment
# **A. Real-world problem.** You tap "pay", the screen freezes, so you tap again. Did the shop
# get paid once or twice? A bank must answer that correctly millions of times a day. The tools
# are old and simple: a *double-entry ledger* (every payment is written twice, once as money
# leaving and once as money arriving), *atomic* transactions (both writes happen or neither),
# and *idempotency* (doing the same request again changes nothing the second time).
#
# **Plan.** (1) build the ledger, (2) make a payment all-or-nothing, (3) make retries safe,
# (4) decide in which order a bank should check things before it debits.
#
# General education about how such systems are built; not advice about real accounts.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a ledger of entries
# An *entry* is (transaction id, account, signed amount). Money leaving an account is negative,
# money arriving is positive (for a customer's account, a bank calls the first a *debit* and the
# second a *credit*). A balance is never stored on its own here: it is the **sum of the
# account's entries**. A special account `MINT` is where money enters the toy world, so that
# every transaction, even the first deposit, has two sides. Two facts follow:
#
#     every transaction:  sum of its entries = 0
#     whole ledger:       sum of all entries = 0, so customer money = money deposited

# %%
class Ledger:
    def __init__(self):
        self.entries = []         # (txn_id, account, signed amount)
        self.results = {}         # txn_id -> first reply (this is the idempotency memory)

    def deposit(self, account, amount):
        self.entries += [(f"dep-{len(self.entries)}", "MINT", -amount), (f"dep-{len(self.entries)}", account, amount)]

    def balance(self, account):
        return sum(a for _, acct, a in self.entries if acct == account)

    def customer_total(self):
        return sum(a for _, acct, a in self.entries if acct != "MINT")

    def ledger_sum(self):
        return sum(a for _, _, a in self.entries)


# %% [markdown]
# ## Step 2: atomic or not?
# Suppose the program crashes between writing the debit and writing the credit. Compare two ways
# of writing a transfer. The careless one writes line by line. The atomic one first prepares both
# lines and then writes them together, so a crash before the write leaves nothing behind.

# %%
class Crash(Exception):
    """Stands in for a power cut or a software fault at the worst moment."""


def transfer_careless(ledger, txn_id, src, dst, amount, crash=False):
    ledger.entries.append((txn_id, src, -amount))
    if crash:
        raise Crash()
    ledger.entries.append((txn_id, dst, amount))


def transfer_atomic(ledger, txn_id, src, dst, amount, crash=False):
    prepared = [(txn_id, src, -amount), (txn_id, dst, amount)]
    if crash:
        raise Crash()
    ledger.entries.extend(prepared)           # one step: both lines or none


# %% [markdown]
# ## Step 3: what to check before debiting, and in which order
# A request carries: a transaction id, who pays, who is paid, an amount, and proof that the owner
# approved it (here a simple True/False `authenticated`; Session 3 checks a real PIN hash).
#
# 1. **Authenticated?** First, so strangers learn nothing about accounts.
# 2. **Duplicate id?** If this id was seen, return the *same answer as before*. This check must
#    come BEFORE the balance check: after a successful payment of 900 from 1000, the balance is
#    100, so a retry would fail the balance test and wrongly say "declined" for a payment that
#    actually happened.
# 3. **Valid amount?** Positive whole rupees, and not more than the per-payment limit.
# 4. **Different accounts?**
# 5. **Sufficient balance?**
# Only then commit atomically.

# %%
def pay(ledger, txn_id, src, dst, amount, authenticated=True, per_payment_limit=2000, dup_first=True):
    """Returns a reply dict: status 'ok' or 'declined', a reason, and whether it is a replay."""

    def reply(status, reason=""):
        r = {"status": status, "reason": reason, "replayed": False}
        if reason != "not authenticated":
            ledger.results[txn_id] = r
        return r

    if not authenticated:
        return reply("declined", "not authenticated")
    if dup_first and txn_id in ledger.results:
        return {**ledger.results[txn_id], "replayed": True}
    if not isinstance(amount, int) or amount <= 0:
        return reply("declined", "bad amount")
    if amount > per_payment_limit:
        return reply("declined", "over per-payment limit")
    if src == dst:
        return reply("declined", "same account")
    if ledger.balance(src) < amount:
        return reply("declined", "insufficient balance")
    if not dup_first and txn_id in ledger.results:       # the wrong order, for comparison
        return {**ledger.results[txn_id], "replayed": True}
    transfer_atomic(ledger, txn_id, src, dst, amount)
    return reply("ok")


# %% [markdown]
# ## Step 4: retries with and without a transaction id check
# A phone whose reply was lost resends the request `retries` times. `charge_count` is how many
# times the payer was debited. With the id check it is 1 (or 0 if declined). Without it, every
# arrival is a new payment until the balance runs out.

# %%
def charge_count(amount, retries, balance=1000, idempotent=True):
    if amount <= 0 or amount > balance:
        return 0
    if idempotent:
        return 1
    return min(retries, balance // amount)


def payer_after(amount, retries, balance=1000, idempotent=True):
    return balance - amount * charge_count(amount, retries, balance, idempotent)


def retry_demo(amount, retries, idempotent):
    """The same idea run through the real Ledger: returns (payer balance, payee balance)."""
    led = Ledger()
    led.deposit("payer", 1000)
    led.deposit("payee", 400)
    for k in range(retries):
        tid = "T1" if idempotent else f"T1-attempt{k}"      # a new id per attempt = no id check
        pay(led, tid, "payer", "payee", amount)
    return led.balance("payer"), led.balance("payee")


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    led = Ledger()
    led.deposit("payer", 1000)
    led.deposit("payee", 400)
    print("start: payer", led.balance("payer"), "payee", led.balance("payee"), "customer total", led.customer_total())
    print("T1 pay 250     ->", pay(led, "T1", "payer", "payee", 250))
    print("T1 again       ->", pay(led, "T1", "payer", "payee", 250))
    print("T2 pay 900     ->", pay(led, "T2", "payer", "payee", 900))
    print("end:   payer", led.balance("payer"), "payee", led.balance("payee"), "customer total", led.customer_total(),
          "ledger sum", led.ledger_sum())
    print("entries:")
    for e in led.entries:
        print("  ", e)

    for fn in (transfer_careless, transfer_atomic):
        t = Ledger()
        t.deposit("payer", 1000)
        t.deposit("payee", 400)
        try:
            fn(t, "X", "payer", "payee", 250, crash=True)
        except Crash:
            pass
        print(f"{fn.__name__:17s} after a crash: payer {t.balance('payer')} payee {t.balance('payee')} "
              f"customer total {t.customer_total()} ledger sum {t.ledger_sum()}")

    bad = Ledger()
    bad.deposit("payer", 1000)
    bad.deposit("payee", 400)
    pay(bad, "T1", "payer", "payee", 900)
    print("retry of a 900 payment, check order duplicate-first :", pay(bad, "T1", "payer", "payee", 900))
    print("retry of a 900 payment, check order balance-first   :", pay(bad, "T1", "payer", "payee", 900, dup_first=False))
    print("3 retries of 250, no id check:", retry_demo(250, 3, False), " with id check:", retry_demo(250, 3, True))

    # figure 1: ledger lines and balances after the three requests
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    names = ["payer", "payee"]
    ax[0].bar(names, [1000, 400], color="#9aa5b1", label="before")
    ax[0].bar(names, [led.balance(n) for n in names], width=0.4, color="#2a9d8f", label="after T1 (twice) and T2")
    ax[0].set_ylabel("balance (rupees)")
    ax[0].set_title("Balances are sums of entries")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3, axis="y")
    cum = np.cumsum([a for _, acct, a in led.entries if acct in names])
    ax[1].step(range(len(cum)), cum, where="post")
    ax[1].set_xlabel("entry number (customer entries only)")
    ax[1].set_ylabel("running customer total (rupees)")
    ax[1].set_title("Customer money only changes when money is deposited")
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "ledger_balances.png", dpi=120)

    # figure 2: charges versus retries
    r = np.arange(1, 9)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(r, [payer_after(250, k, idempotent=False) for k in r], "o-", label="no id check")
    ax2.plot(r, [payer_after(250, k, idempotent=True) for k in r], "s--", label="with id check")
    ax2.set_xlabel("number of times the request arrives (count)")
    ax2.set_ylabel("payer balance after (rupees)")
    ax2.set_title("Paying 250 from 1000: retries")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "retries.png", dpi=120)

# %% [markdown]
# ## Where this stops
# A real bank has many ledgers, not one list in memory. Session 3 turns this into a small
# switch that you can stress with lost messages and fraud rules.
