"""Checkpoint for Session 3. Prints PASS or FAIL."""
import hashlib

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # --- PIN storage ---
    rng = np.random.default_rng(0)
    s1, s2 = L.new_salt(rng), L.new_salt(rng)
    h1, h2 = L.hash_pin("1234", s1, 1000), L.hash_pin("1234", s2, 1000)
    checks.append(("same PIN with two salts gives two different hashes", h1 != h2 and len(h1) == 32))
    checks.append(("hand check: hash equals hashlib.pbkdf2_hmac directly", h1 == hashlib.pbkdf2_hmac("sha256", b"1234", s1, 1000)))
    checks.append(("right PIN verifies, wrong PIN does not", L.verify_pin("1234", s1, h1, 1000) and not L.verify_pin("1235", s1, h1, 1000)))
    import hmac
    real, calls = hmac.compare_digest, []
    hmac.compare_digest = lambda x, y: (calls.append(1), real(x, y))[1]
    try:
        L.verify_pin("1234", s1, h1, 1000)
    finally:
        hmac.compare_digest = real
    checks.append(("PIN comparison goes through hmac.compare_digest (constant time)", len(calls) == 1))

    sw = L.Switch(iterations=500)
    sw.open_account("a", "4821", 1000, rng)
    sw.open_account("b", "1111", 400, rng)
    checks.append(("the plain PIN is not stored anywhere in the account", "4821" not in repr(sw.accounts["a"])))

    # --- lockout ---
    for _ in range(3):
        sw.pay("bad", "a", "b", 10, "0000")
    locked = sw.pay("t-locked", "a", "b", 10, "4821")
    checks.append(("account locks after 3 wrong PINs (even the right PIN is refused)", locked["reason"] == "account locked"))
    sw2 = L.Switch(iterations=500)
    sw2.open_account("a", "4821", 1000, rng)
    sw2.open_account("b", "1111", 400, rng)
    sw2.pay("x1", "a", "b", 10, "0000")
    sw2.pay("x2", "a", "b", 10, "0000")
    ok = sw2.pay("x3", "a", "b", 10, "4821")
    sw2.pay("x4", "a", "b", 10, "0000")
    sw2.pay("x5", "a", "b", 10, "0000")
    again = sw2.pay("x6", "a", "b", 10, "4821")
    checks.append(("a right PIN resets the wrong-PIN counter", ok["status"] == "ok" and again["status"] == "ok"))

    # --- payment rules and edge cases ---
    sw3 = L.Switch(iterations=500)
    sw3.open_account("a", "4821", 1000, rng)
    sw3.open_account("b", "1111", 400, rng)
    r1 = sw3.pay("T1", "a", "b", 250, "4821")
    r2 = sw3.pay("T1", "a", "b", 250, "4821")
    checks.append(("hand check: pay 250 then retry the same id: a=750, b=650, one debit",
                   r1["status"] == "ok" and r2["replayed"] and sw3.balance("a") == 750 and sw3.balance("b") == 650
                   and L.double_charges(sw3) == 0))
    clash = sw3.pay("T1", "a", "b", 999, "4821")
    checks.append(("same id with different details is refused", clash["status"] == "declined" and sw3.balance("a") == 750))
    exact = sw3.pay("T2", "a", "b", 750, "4821")
    checks.append(("paying exactly the whole balance works (boundary)", exact["status"] == "ok" and sw3.balance("a") == 0))
    broke = sw3.pay("T3", "a", "b", 1, "4821")
    checks.append(("with balance 0 even 1 rupee is declined", broke["reason"] == "insufficient balance"))
    bad = [sw3.pay(f"B{i}", "b", "a", amt, "1111")["reason"] for i, amt in enumerate((0, -5, 2.5))]
    checks.append(("zero, negative and fractional amounts are refused", bad == ["bad amount"] * 3))
    checks.append(("paying yourself is refused", sw3.pay("S1", "b", "b", 5, "1111")["reason"] == "same account"))
    checks.append(("an unknown account is refused, not a crash", sw3.pay("U1", "zz", "b", 5, "1111")["reason"] == "unknown account"))
    inv = L.check_invariants(sw3)
    checks.append(("all invariants hold after these payments", all(inv.values())))

    # --- failure injection ---
    good, st_good = L.run_workload(True)
    bad_sw, st_bad = L.run_workload(False)
    checks.append(("idempotent switch under lost replies: every invariant holds", all(L.check_invariants(good).values()) and st_good["double_charged"] == 0))
    inv_bad = L.check_invariants(bad_sw)
    checks.append(("failure case: without idempotency keys some ids are charged twice", st_bad["double_charged"] > 0 and not inv_bad["no double charge"]))
    checks.append(("a double charge still conserves money (so it needs its own invariant)", inv_bad["money conserved"] and inv_bad["no negative balance"]))

    # --- formula versus simulation ---
    f = L.expected_charges(0.1, 0.2, 3)
    sim = L.simulate_charges(0.1, 0.2, 3, 20000, 5, False)
    checks.append((f"formula matches simulation for charges per payment (formula {f:.4f}, simulated {sim:.4f})", abs(f - sim) < 0.02))
    checks.append(("with no loss at all a payment is charged exactly once", abs(L.expected_charges(0.0, 0.0, 3) - 1.0) < 1e-12))
    checks.append(("with one try the charge count is the arrival probability", abs(L.expected_charges(0.1, 0.2, 1) - 0.9) < 1e-12))

    # --- fraud rules ---
    flagged = [True] * 30 + [False] * 970 + [True] * 40 + [False] * 10
    labels = [False] * 1000 + [True] * 50
    r = L.error_rates(flagged, labels)
    checks.append(("worked example: 30 of 1000 ordinary flagged and 40 of 50 fraud flagged gives FPR 3% and FNR 20%",
                   abs(r["fpr"] - 0.03) < 1e-12 and abs(r["fnr"] - 0.20) < 1e-12))
    scr = L.FraudScreen()
    for k in range(4):
        scr.record("c", "p", 100, k * 100.0)
    checks.append(("amount rule stays quiet with too little history", "amount" not in scr.check("c", "p", 5000, 1000.0)))
    scr.record("c", "p", 100, 500.0)
    checks.append(("amount rule fires once there is history", "amount" in scr.check("c", "p", 5000, 1000.0)))
    checks.append(("a known payee below the limit is not flagged as new", scr.check("c", "p", 100, 1000.0) == []))
    checks.append(("a new payee with a large amount is flagged", "new_payee" in scr.check("c", "q", 1500, 1000.0)))

    data = L.make_dataset()
    again = L.make_dataset()
    checks.append(("synthetic data is reproducible from the seed", data == again))
    res = L.evaluate(data)
    caught = res["attacks_caught"]
    checks.append(("default rules catch every burst and every big payment attack", caught["burst"][0] == caught["burst"][1] and caught["big"][0] == caught["big"][1]))
    checks.append(("limit of the rules: most slow attacks are missed", caught["slow"][0] <= caught["slow"][1] // 4))
    checks.append(("false positive rate on ordinary payments is below 5%", res["fpr"] < 0.05))
    lo, hi = L.evaluate(data, velocity_max=2), L.evaluate(data, velocity_max=11)
    checks.append(("trade-off: a stricter velocity limit raises false positives and lowers misses", lo["fpr"] > hi["fpr"] and lo["fnr"] < hi["fnr"]))

    sw4, results = L.screened_run(data)
    held_ids = set(sw4.pending)
    entry_ids = {e[0] for e in sw4.entries}
    checks.append(("screened switch over the whole dataset keeps all invariants", all(L.check_invariants(sw4).values())))
    checks.append(("held payments leave no ledger entries until confirmed", not (held_ids & entry_ids) and len(held_ids) > 0))

    sw5 = L.Switch(screen=L.FraudScreen(), iterations=500)
    sw5.open_account("a", "4821", 5000, rng)
    sw5.open_account("b", "1111", 0, rng)
    held = sw5.pay("H1", "a", "b", 2000, "4821")
    sw5.pay("H2", "a", "b", 4000, "4821", 1.0)
    conf = sw5.confirm("H1")
    checks.append(("a held payment becomes ok only after confirmation", held["status"] == "held" and conf["status"] == "ok" and sw5.balance("a") == 3000))

    # --- the lever left for the mini-project ---
    sw6 = L.Switch(iterations=500)
    sw6.open_account("victim", "4821", 50000)
    sw6.open_account("shop", "1111", 0)
    done, lost = L.rapid_fire_test(sw6, "victim", "shop", "4821")
    checks.append((f"without a daily limit a rapid-fire burst drains {lost} rupees in {done} payments (your mini-project fixes this)", done == 40 and lost == 36000))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
