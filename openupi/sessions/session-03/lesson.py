"""Session 3 (Level 3): a toy payment switch, failure injection, fraud rules, and the invariants that keep it honest.

Run:  python start.py 3

This is a TOY. It borrows only the ideas behind real payment systems. There is no networking,
no real bank, no real UPI protocol and no real data. Never use it to hold real money or real PINs.
"""
# %% [markdown]
# # Session 3: a toy payment switch you can break and fix
# **A. Real-world problem.** Real payment systems must stay correct when messages are lost,
# when people tap twice, and when someone who is not the owner tries to pay. Today you build a
# small in-memory *switch* (the middle box from Session 1) with accounts, a transaction log,
# a safely stored PIN, an idempotency key, and simple fraud rules. Then you stress it with
# *synthetic* trouble (lost replies, retries, rapid-fire payments) and check that three
# invariants always hold: money is conserved, no balance goes negative, nobody is charged twice.
#
# **Responsible use.** Everything here is defence: finding out where checks belong and how well
# they work. The data is invented, seeded random numbers. General education only, not advice
# about any real bank, app or account.

# %%
import hashlib
import hmac
import pathlib
import secrets
from collections import Counter

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ITER_DEFAULT = 20_000      # real systems use slower, stronger settings and hardware modules


# %% [markdown]
# ## Step 1: store a PIN safely (never the PIN itself)
# If the switch stored PINs as text, anyone who read the database could read every PIN.
# Instead we store a *salted hash*. A hash is a one-way scramble: easy to compute from the PIN,
# practically impossible to run backwards. The *salt* is a random string, different for every
# account, mixed in before hashing so that two people with the same PIN get different hashes
# and one table of precomputed answers is useless. We use `hashlib.pbkdf2_hmac`, which repeats
# the scramble many times to make each guess slow.
#
# To check a PIN we hash the attempt with the stored salt and compare. The comparison uses
# `hmac.compare_digest`, which takes the same time whether the first byte or the last byte
# differs. An ordinary `==` can stop at the first difference, and measuring tiny timing
# differences can leak information (a *timing attack*).
#
# A 4-digit PIN has only 10 000 possibilities, so hashing alone is not enough if a stolen
# hash can be guessed offline. Real systems also lock the account after a few wrong tries and
# keep PIN checks inside special hardware. We add the lockout below.

# %%
def new_salt(rng=None):
    """16 random bytes. Real code uses secrets (as here); a seeded rng is only for repeatable lessons."""
    return rng.bytes(16) if rng is not None else secrets.token_bytes(16)


def hash_pin(pin, salt, iterations=ITER_DEFAULT):
    return hashlib.pbkdf2_hmac("sha256", pin.encode("ascii"), salt, iterations)


def verify_pin(pin, salt, stored, iterations=ITER_DEFAULT):
    return hmac.compare_digest(hash_pin(pin, salt, iterations), stored)


# %% [markdown]
# ## Step 2: the switch
# Accounts, a double-entry list of `entries` (txn_id, account, signed amount), and a `log`.
# The order of checks matches Session 2: authenticate, then look for a duplicate id, then
# validate the amount, then check the balance, then (optionally) ask the fraud screen, and only
# then commit both entries together.
#
# `idempotent=False` switches the duplicate check off. That is the failure case later.

# %%
class Switch:
    MAX_FAILS = 3

    def __init__(self, idempotent=True, screen=None, iterations=ITER_DEFAULT):
        self.idempotent = idempotent
        self.screen = screen
        self.iterations = iterations
        self.accounts = {}
        self.entries = []          # (txn_id, account, signed amount); every txn sums to 0
        self.log = []              # one dict per request the switch decided on
        self.minted = 0            # total money that was put into accounts at opening
        self.replays = 0
        self.pending = {}          # held payments waiting for the customer's confirmation
        self._seen = {}

    def open_account(self, name, pin, balance, rng=None):
        salt = new_salt(rng)
        self.accounts[name] = {"salt": salt, "pin_hash": hash_pin(pin, salt, self.iterations),
                               "balance": balance, "fails": 0}
        self.entries.append((f"open-{name}", "MINT", -balance))
        self.entries.append((f"open-{name}", name, balance))
        self.minted += balance

    def balance(self, name):
        return self.accounts[name]["balance"]

    def pay(self, txn_id, src, dst, amount, pin, now=0.0):
        """Try to move `amount` (whole rupees) from src to dst. Returns a reply dict."""
        acct = self.accounts.get(src)
        if acct is None or dst not in self.accounts:
            return self._finish(txn_id, src, dst, amount, now, "declined", "unknown account")
        if acct["fails"] >= self.MAX_FAILS:
            return self._finish(txn_id, src, dst, amount, now, "declined", "account locked")
        if not verify_pin(pin, acct["salt"], acct["pin_hash"], self.iterations):
            acct["fails"] += 1
            return self._finish(txn_id, src, dst, amount, now, "declined", "wrong pin")
        acct["fails"] = 0
        if self.idempotent and txn_id in self._seen:
            first = self._seen[txn_id]
            self.replays += 1
            if first["fingerprint"] != (src, dst, amount):
                return {"txn_id": txn_id, "status": "declined", "reason": "id reused with different details", "replayed": True}
            return {**first["reply"], "replayed": True}
        if not isinstance(amount, int) or amount <= 0:
            return self._finish(txn_id, src, dst, amount, now, "declined", "bad amount")
        if src == dst:
            return self._finish(txn_id, src, dst, amount, now, "declined", "same account")
        if acct["balance"] < amount:
            return self._finish(txn_id, src, dst, amount, now, "declined", "insufficient balance")
        if self.screen is not None:
            flags = self.screen.check(src, dst, amount, now)
            if flags:
                self.pending[txn_id] = (src, dst, amount, now)
                return self._finish(txn_id, src, dst, amount, now, "held", "fraud flags: " + ",".join(flags))
        self._commit(txn_id, src, dst, amount, now)
        return self._finish(txn_id, src, dst, amount, now, "ok", "")

    def _commit(self, txn_id, src, dst, amount, now):
        """Both entries and both balances together, or nothing."""
        self.entries.append((txn_id, src, -amount))
        self.entries.append((txn_id, dst, amount))
        self.accounts[src]["balance"] -= amount
        self.accounts[dst]["balance"] += amount
        if self.screen is not None:
            self.screen.record(src, dst, amount, now)

    def confirm(self, txn_id):
        """The customer confirmed a held payment (for example by an extra code). Balance is checked again."""
        src, dst, amount, now = self.pending.pop(txn_id)
        if self.accounts[src]["balance"] < amount:
            return {"txn_id": txn_id, "status": "declined", "reason": "insufficient balance", "replayed": False}
        self._commit(txn_id, src, dst, amount, now)
        reply = {"txn_id": txn_id, "status": "ok", "reason": "confirmed", "replayed": False}
        if self.idempotent:
            self._seen[txn_id] = {"fingerprint": (src, dst, amount), "reply": reply}
        return reply

    def _finish(self, txn_id, src, dst, amount, now, status, reason):
        reply = {"txn_id": txn_id, "status": status, "reason": reason, "replayed": False}
        self.log.append({"t": now, "txn_id": txn_id, "src": src, "dst": dst, "amount": amount,
                         "status": status, "reason": reason})
        if self.idempotent and reason not in ("wrong pin", "account locked", "unknown account"):
            self._seen[txn_id] = {"fingerprint": (src, dst, amount), "reply": reply}
        return reply


# %% [markdown]
# ## Step 3: the invariants
# An *invariant* is a statement that must be true after every operation, whatever goes wrong.
# 1. **Money is conserved.** All entries add up to zero, and the sum of customer balances equals
#    the money that was put in.
# 2. **No negative balance.**
# 3. **No double charge.** Each transaction id has at most one debit entry.
#
# Note that a double charge does NOT break invariant 1 (the money simply moves twice), which is
# why invariant 3 has to be checked separately.

# %%
def balances_from_entries(switch):
    totals = Counter()
    for _, account, amount in switch.entries:
        totals[account] += amount
    return totals


def check_invariants(switch):
    totals = balances_from_entries(switch)
    customers = {name: a["balance"] for name, a in switch.accounts.items()}
    debits = Counter(t for t, acct, amt in switch.entries if amt < 0 and acct != "MINT")
    return {
        "money conserved": sum(e[2] for e in switch.entries) == 0 and sum(customers.values()) == switch.minted,
        "balances equal sum of entries": all(totals[n] == b for n, b in customers.items()),
        "no negative balance": all(b >= 0 for b in customers.values()),
        "no double charge": all(c <= 1 for c in debits.values()),
    }


def double_charges(switch):
    """Number of transaction ids that were debited more than once."""
    debits = Counter(t for t, acct, amt in switch.entries if amt < 0 and acct != "MINT")
    return sum(1 for c in debits.values() if c > 1)


# %% [markdown]
# ## Step 4: failure injection (lost requests, lost replies, retries)
# A phone sends a request; the network may lose it (nothing happens), or the switch may process it
# and the *reply* may be lost (the money moved but the phone does not know). A careful phone
# retries with the SAME transaction id. Retrying is only safe if the switch is idempotent.

# %%
def attempt(switch, request, rng, p_req, p_rep, tries):
    """Send `request` up to `tries` times. Returns (reply or None, attempts used)."""
    for k in range(tries):
        if rng.random() < p_req:
            continue                       # request lost: the switch never sees it
        reply = switch.pay(*request)
        if rng.random() < p_rep:
            continue                       # reply lost: it happened, but the phone does not know
        return reply, k + 1
    return None, tries


def run_workload(idempotent, n=300, seed=3, p_req=0.1, p_rep=0.2, tries=3, iterations=1000):
    """n random payments between 10 accounts over a lossy network. Returns (switch, stats)."""
    rng = np.random.default_rng(seed)
    sw = Switch(idempotent=idempotent, iterations=iterations)
    pins = {}
    for i in range(10):
        pins[f"acct{i}"] = f"{int(rng.integers(0, 10000)):04d}"
        sw.open_account(f"acct{i}", pins[f"acct{i}"], 1000, rng)
    unknown = 0
    for k in range(n):
        src, dst = rng.choice(10, size=2, replace=False)
        amount = int(rng.integers(1, 301))
        req = (f"T{k}", f"acct{src}", f"acct{dst}", amount, pins[f"acct{src}"], float(k))
        reply, _ = attempt(sw, req, rng, p_req, p_rep, tries)
        unknown += reply is None
    return sw, {"unknown_outcomes": unknown, "double_charged": double_charges(sw)}


# %% [markdown]
# ## Step 5: how often does a retry double-charge? A formula to check against
# Suppose each attempt reaches the switch with probability a = 1 - p_req, and a reached request
# gets its reply back with probability b = 1 - p_rep. The phone stops at the first reply it
# sees (probability s = a*b per attempt) or after `tries` attempts. Without idempotency every
# attempt that reaches the switch charges once, so the expected number of charges is
#
#     E[charges] = a * (1 - (1 - s)^tries) / s
#
# With idempotency a payment that reaches the switch at least once is charged exactly once, so
# the expected number of charges is 1 - p_req^tries. We check the formula against a simulation.

# %%
def expected_charges(p_req, p_rep, tries):
    a, s = 1 - p_req, (1 - p_req) * (1 - p_rep)
    return a * (1 - (1 - s) ** tries) / s


def prob_charged_at_least_once(p_req, tries):
    return 1 - p_req ** tries


def simulate_charges(p_req, p_rep, tries, n, seed, idempotent):
    """Mean number of charges per payment (light version: no PINs, just the retry logic)."""
    rng = np.random.default_rng(seed)
    total = 0
    for _ in range(n):
        reached = 0
        for _ in range(tries):
            if rng.random() < p_req:
                continue
            reached += 1
            if rng.random() >= p_rep:
                break
        total += min(reached, 1) if idempotent else reached
    return total / n


# %% [markdown]
# ## Step 6: simple fraud rules (defence), measured on synthetic data
# Three rules a switch can run *before* committing:
# * **velocity**: more than `velocity_max` completed payments from one account in `window` minutes;
# * **unusual amount**: more than `amount_mult` times the account's median past amount;
# * **new payee**: a payee never paid before, with amount at least `new_payee_min`.
# A flagged payment is *held* for extra confirmation (it does not happen yet). The data below
# is invented: ordinary customers plus labelled synthetic "account takeover" patterns, made only
# so that we can measure how well the rules work.
#
# Two error rates matter. **False positive rate** = ordinary payments flagged / all ordinary
# payments (annoyed customers). **False negative rate** = fraud payments not flagged / all fraud
# payments (missed fraud). Lowering one usually raises the other.

# %%
class FraudScreen:
    def __init__(self, velocity_max=5, window=10.0, amount_mult=4.0, new_payee_min=1000, min_history=5):
        self.velocity_max, self.window = velocity_max, window
        self.amount_mult, self.new_payee_min, self.min_history = amount_mult, new_payee_min, min_history
        self.hist = {}

    def check(self, src, dst, amount, now):
        h = self.hist.get(src)
        flags = []
        recent = 0 if h is None else sum(1 for t in h["times"][-(self.velocity_max + 1):] if now - t <= self.window)
        if recent + 1 > self.velocity_max:
            flags.append("velocity")
        if h is not None and len(h["amounts"]) >= self.min_history and amount > self.amount_mult * float(np.median(h["amounts"])):
            flags.append("amount")
        if (h is None or dst not in h["payees"]) and amount >= self.new_payee_min:
            flags.append("new_payee")
        return flags

    def record(self, src, dst, amount, now):
        h = self.hist.setdefault(src, {"times": [], "amounts": [], "payees": set()})
        h["times"].append(now)
        h["amounts"].append(amount)
        h["payees"].add(dst)


def make_dataset(seed=7, n_customers=300, days=14, n_attacks=60):
    """Synthetic payments: (minute, src, dst, amount, kind). kind is 'legit' or 'burst:i', 'big:i', 'slow:i'."""
    rng = np.random.default_rng(seed)
    base = rng.choice([100, 200, 400, 800], size=n_customers)
    regular = [rng.choice([j for j in range(n_customers) if j != i], size=5, replace=False) for i in range(n_customers)]
    data = []
    for c in range(n_customers):
        for day in range(days):
            for _ in range(rng.poisson(2.0)):
                t = day * 1440 + float(rng.uniform(480, 1320))
                dst = int(rng.choice(regular[c])) if rng.random() < 0.9 else int(rng.choice([j for j in range(n_customers) if j != c]))
                amount = max(10, int(round(base[c] * rng.lognormal(0.0, 0.5))))
                data.append((t, c, dst, amount, "legit"))
            if rng.random() < 0.05:                 # ordinary bursts: splitting a bill among friends
                t = day * 1440 + float(rng.uniform(480, 1300))
                for j in rng.choice(regular[c], size=int(rng.integers(3, 6)), replace=False):
                    data.append((t, c, int(j), max(10, int(round(base[c] * 0.5 * rng.lognormal(0.0, 0.3)))), "legit"))
                    t += float(rng.uniform(0.5, 1.5))
    kinds = ["burst", "big", "slow"]
    for i in range(n_attacks):
        kind, c, mule = kinds[i % 3], int(rng.integers(0, n_customers)), n_customers + i
        t0 = int(rng.integers(days // 2, days)) * 1440 + float(rng.uniform(480, 1200))
        tag = f"{kind}:{i}"
        if kind == "burst":
            t = t0
            for _ in range(int(rng.integers(8, 13))):
                data.append((t, c, mule, int(rng.integers(300, 801)), tag))
                t += float(rng.uniform(0.5, 2.0))
        elif kind == "big":
            data.append((t0, c, mule, int(round(base[c] * rng.uniform(10, 15))), tag))
        else:
            t = t0
            for _ in range(6):
                data.append((t, c, mule, int(round(base[c] * rng.uniform(0.8, 1.5))), tag))
                t += float(rng.uniform(300, 600))
    data.sort(key=lambda r: r[0])
    return data


def error_rates(flagged, is_fraud):
    """False positive rate and false negative rate from two equal-length boolean lists."""
    flagged, is_fraud = np.asarray(flagged, bool), np.asarray(is_fraud, bool)
    fp, tn = int(np.sum(flagged & ~is_fraud)), int(np.sum(~flagged & ~is_fraud))
    fn, tp = int(np.sum(~flagged & is_fraud)), int(np.sum(flagged & is_fraud))
    return {"fp": fp, "tn": tn, "fn": fn, "tp": tp,
            "fpr": fp / (fp + tn) if fp + tn else 0.0, "fnr": fn / (fn + tp) if fn + tp else 0.0}


def evaluate(data, **rule_args):
    """Run the rules over the data in time order. A held ordinary payment is confirmed by its owner and then
    counts as history; a held fraud payment is never confirmed, so it does not."""
    screen = FraudScreen(**rule_args)
    flagged, fraud, first = [], [], {}
    for t, src, dst, amount, kind in data:
        flags = screen.check(src, dst, amount, t)
        if not flags or kind == "legit":      # a held payment of a real customer is confirmed by them
            screen.record(src, dst, amount, t)
        flagged.append(bool(flags))
        fraud.append(kind != "legit")
        if kind != "legit":
            first[kind] = first.get(kind, False) or bool(flags)
    out = error_rates(flagged, fraud)
    caught = {k: [v for tag, v in first.items() if tag.startswith(k)] for k in ("burst", "big", "slow")}
    out["attacks_caught"] = {k: (sum(v), len(v)) for k, v in caught.items()}
    return out


def screened_run(data, n_customers=300, n_attacks=60, iterations=500):
    """Push the whole dataset through the real Switch with the screen switched on."""
    rng = np.random.default_rng(11)
    sw = Switch(screen=FraudScreen(), iterations=iterations)
    pin = "4821"
    for i in range(n_customers + n_attacks):
        sw.open_account(i, pin, 20000, rng)
    results = Counter()
    for k, (t, src, dst, amount, kind) in enumerate(data):
        status = sw.pay(f"D{k}", src, dst, amount, pin, t)["status"]
        results[status] += 1
        if status == "held" and kind == "legit":      # the real owner confirms; an attacker cannot
            results["confirmed " + sw.confirm(f"D{k}")["status"]] += 1
    return sw, results


# %% [markdown]
# ## Step 7: a stress test for the mini-project
# Imagine the screen is bypassed or too slow (the "slow" pattern slips past it). What is the
# worst a single account can lose in one burst? `rapid_fire_test` sends `n` equal payments one
# after another and reports how much money left the account. Your mini-project: add a daily limit.

# %%
def rapid_fire_test(switch, src, dst, pin, n=40, amount=900, start=600.0, gap=0.25):
    """Send n payments `gap` minutes apart. Returns (payments that succeeded, rupees that left src)."""
    before = switch.balance(src)
    done = sum(switch.pay(f"RF{i}", src, dst, amount, pin, start + i * gap)["status"] == "ok" for i in range(n))
    return done, before - switch.balance(src)


# %% [markdown]
# ## Step 8: run everything and look at the numbers

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # PIN safety
    rng = np.random.default_rng(1)
    s1, s2 = new_salt(rng), new_salt(rng)
    print("same PIN, two salts -> different hashes:", hash_pin("1234", s1, 1000) != hash_pin("1234", s2, 1000))
    print("possible 4-digit PINs:", 10 ** 4)

    # failure injection
    print("\nfailure injection: 300 payments, p_req 0.1, p_rep 0.2, 3 tries")
    for idem in (True, False):
        sw, st = run_workload(idem)
        inv = check_invariants(sw)
        print(f"  idempotent={idem!s:5}  double-charged ids {st['double_charged']:2d}  unknown outcomes {st['unknown_outcomes']:2d}  invariants {inv}")

    # formula versus simulation
    print("\nexpected charges per payment, formula vs simulation (20000 payments)")
    for p_req, p_rep, k in [(0.1, 0.2, 3), (0.1, 0.3, 3), (0.3, 0.3, 4)]:
        print(f"  p_req {p_req} p_rep {p_rep} tries {k}: formula {expected_charges(p_req, p_rep, k):.4f}  "
              f"simulated {simulate_charges(p_req, p_rep, k, 20000, 5, False):.4f}  "
              f"idempotent {simulate_charges(p_req, p_rep, k, 20000, 5, True):.4f} (formula {prob_charged_at_least_once(p_req, k):.4f})")

    # fraud
    data = make_dataset()
    n_fraud = sum(1 for r in data if r[4] != "legit")
    print(f"\nsynthetic data: {len(data)} payments, {n_fraud} labelled fraud, {len(data) - n_fraud} ordinary")
    base = evaluate(data)
    print(f"default rules: FPR {base['fpr']:.3%}  FNR {base['fnr']:.3%}  attacks caught {base['attacks_caught']}")
    sweep = []
    for v in range(2, 12):
        r = evaluate(data, velocity_max=v)
        sweep.append((v, r["fpr"], r["fnr"]))
        print(f"  velocity_max {v:2d}: FPR {r['fpr']:.3%}  FNR {r['fnr']:.3%}")
    rules_only = {}
    for name, args in [("velocity only", dict(amount_mult=1e9, new_payee_min=10 ** 9)),
                       ("amount only", dict(velocity_max=10 ** 6, new_payee_min=10 ** 9)),
                       ("new payee only", dict(velocity_max=10 ** 6, amount_mult=1e9))]:
        r = evaluate(data, **args)
        rules_only[name] = (r["fpr"], r["fnr"])
        print(f"  {name:15s}: FPR {r['fpr']:.3%}  FNR {r['fnr']:.3%}  caught {r['attacks_caught']}")

    sw0 = Switch(iterations=500)
    sw0.open_account("victim", "4821", 50000)
    sw0.open_account("shop", "1111", 0)
    print("\nrapid-fire test, no screen, no daily limit:", rapid_fire_test(sw0, "victim", "shop", "4821"))

    sw, results = screened_run(data)
    print("\nscreened switch over the whole dataset:", dict(results), check_invariants(sw))

    fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
    cases = [0.0, 0.1, 0.2, 0.3, 0.4]
    ax[0].plot(cases, [expected_charges(0.1, q, 3) for q in cases], "o-", label="no idempotency key (formula)")
    ax[0].plot(cases, [simulate_charges(0.1, q, 3, 8000, 9, False) for q in cases], "k.", label="simulation")
    ax[0].plot(cases, [prob_charged_at_least_once(0.1, 3)] * len(cases), "s--", label="with idempotency key")
    ax[0].set_xlabel("probability a reply is lost")
    ax[0].set_ylabel("charges per payment (count)")
    ax[0].set_title("Retries without a key charge too often")
    ax[0].grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    v, fpr, fnr = zip(*sweep)
    ax[1].plot(np.array(fpr) * 100, np.array(fnr) * 100, "o-")
    for vi, x, y in sweep:
        ax[1].annotate(str(vi), (x * 100, y * 100), textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax[1].set_xlabel("false positive rate (% of ordinary payments flagged)")
    ax[1].set_ylabel("false negative rate (% of fraud payments missed)")
    ax[1].set_title("Velocity limit trade-off (labels: payments per 10 min)")
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "failures_and_fraud.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    names = list(rules_only) + ["all three"]
    fnrs = [rules_only[k][1] * 100 for k in rules_only] + [base["fnr"] * 100]
    fprs = [rules_only[k][0] * 100 for k in rules_only] + [base["fpr"] * 100]
    xs = np.arange(len(names))
    ax2.bar(xs - 0.2, fprs, 0.4, label="false positive rate")
    ax2.bar(xs + 0.2, fnrs, 0.4, label="false negative rate")
    ax2.set_xticks(xs)
    ax2.set_xticklabels(names, fontsize=8)
    ax2.set_ylabel("rate (%)")
    ax2.set_title("Each rule alone versus all three")
    ax2.grid(alpha=0.3, axis="y")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "rules_compared.png", dpi=120)

# %% [markdown]
# ## Where this stops
# This switch is one process with one list. Real systems have separate banks, clocks that
# disagree, concurrent requests, hardware security and regulators. Use this repo to understand
# the ideas, never to handle real money.
