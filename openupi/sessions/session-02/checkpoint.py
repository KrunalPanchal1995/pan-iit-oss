"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def fresh(L, payer=1000, payee=400):
    led = L.Ledger()
    led.deposit("payer", payer)
    led.deposit("payee", payee)
    return led


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    led = fresh(L)
    checks.append(("balances are sums of entries", led.balance("payer") == 1000 and led.balance("payee") == 400))
    checks.append(("the whole ledger sums to zero after deposits", led.ledger_sum() == 0 and led.customer_total() == 1400))

    # worked example: T1 pay 250, T1 again, T2 pay 900
    r1 = L.pay(led, "T1", "payer", "payee", 250)
    r2 = L.pay(led, "T1", "payer", "payee", 250)
    r3 = L.pay(led, "T2", "payer", "payee", 900)
    checks.append(("worked example: 250, retry of 250, then 900 gives payer 750, payee 650, total 1400",
                   r1["status"] == "ok" and r2["replayed"] and r3["reason"] == "insufficient balance"
                   and led.balance("payer") == 750 and led.balance("payee") == 650 and led.customer_total() == 1400))
    checks.append(("every transaction's entries sum to zero",
                   all(sum(a for t, _, a in led.entries if t == tid) == 0 for tid in {e[0] for e in led.entries})))
    checks.append(("the retry returns the same status as the first reply", r2["status"] == r1["status"] and r2["replayed"] and not r1["replayed"]))

    # atomicity
    a, c = fresh(L), fresh(L)
    for led2, fn in ((c, L.transfer_careless), (a, L.transfer_atomic)):
        try:
            fn(led2, "X", "payer", "payee", 250, crash=True)
        except L.Crash:
            pass
    checks.append(("atomic transfer: a crash leaves the ledger unchanged", a.customer_total() == 1400 and a.ledger_sum() == 0 and a.balance("payer") == 1000))
    checks.append(("careless transfer: a crash destroys 250 rupees", c.customer_total() == 1150 and c.ledger_sum() == -250))
    ok = fresh(L)
    L.transfer_atomic(ok, "Y", "payer", "payee", 250)
    checks.append(("atomic transfer without a crash moves exactly 250", ok.balance("payer") == 750 and ok.balance("payee") == 650))

    # order of checks
    good, bad = fresh(L), fresh(L)
    L.pay(good, "T1", "payer", "payee", 900)
    L.pay(bad, "T1", "payer", "payee", 900)
    again_good = L.pay(good, "T1", "payer", "payee", 900)
    again_bad = L.pay(bad, "T1", "payer", "payee", 900, dup_first=False)
    checks.append(("duplicate check first: retry of a 900 payment says ok (replayed)", again_good["status"] == "ok" and again_good["replayed"]))
    checks.append(("balance check first gives the wrong answer for a retry (the bug)", again_bad["status"] == "declined"))
    checks.append(("a retry never moves money twice", good.balance("payer") == 100 and good.balance("payee") == 1300))

    # each check on its own
    led = fresh(L)
    checks.append(("unauthenticated request is refused and nothing moves",
                   L.pay(led, "A1", "payer", "payee", 10, authenticated=False)["reason"] == "not authenticated" and led.balance("payer") == 1000))
    checks.append(("zero, negative and fractional amounts are refused",
                   [L.pay(led, f"B{i}", "payer", "payee", x)["reason"] for i, x in enumerate((0, -5, 2.5))] == ["bad amount"] * 3))
    checks.append(("over the per-payment limit is refused", L.pay(led, "C1", "payer", "payee", 2001)["reason"] == "over per-payment limit"))
    checks.append(("paying yourself is refused", L.pay(led, "D1", "payer", "payer", 10)["reason"] == "same account"))
    checks.append(("exactly the whole balance is allowed (boundary)", L.pay(led, "E1", "payer", "payee", 1000)["status"] == "ok" and led.balance("payer") == 0))
    checks.append(("one rupee over the balance is refused", L.pay(led, "E2", "payee", "payer", 1401)["reason"] == "insufficient balance"))
    checks.append(("no balance went negative", led.balance("payer") >= 0 and led.balance("payee") >= 0 and led.customer_total() == 1400))

    # retries
    checks.append(("3 retries of 250 with the id check: payer 750", L.retry_demo(250, 3, True) == (750, 650)))
    checks.append(("3 retries of 250 without it: payer 250, payee 1150, total still 1400", L.retry_demo(250, 3, False) == (250, 1150)))
    checks.append(("formula agrees with the real ledger for 1 to 6 retries",
                   all(L.retry_demo(250, k, False) == (L.payer_after(250, k, idempotent=False), 1400 - L.payer_after(250, k, idempotent=False)) for k in range(1, 7))))
    checks.append(("without the id check retries stop when the balance runs out (never negative)", L.payer_after(250, 8, idempotent=False) == 0))
    checks.append(("an amount above the balance is never charged", L.charge_count(1200, 3) == 0 and L.charge_count(1200, 3, idempotent=False) == 0))
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
