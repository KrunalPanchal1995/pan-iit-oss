"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # joins against nested loops
    shop = L.shop_db()
    inner, left = L.join_sql(shop), L.join_sql(shop, "LEFT")
    checks.append(("inner join equals nested loops", inner == L.join_loops(L.CUSTOMERS, L.ORDERS)))
    checks.append(("left join equals nested loops", left == L.join_loops(L.CUSTOMERS, L.ORDERS, left=True)))
    checks.append(("14 inner rows and 16 left rows: customers 7 and 8 have no orders",
                   len(inner) == 14 and len(left) == 16 and [r for r in left if r[2] is None] == [(7, "Xena", None, None), (8, "Yash", None, None)]))

    # plan, operation counts and timing
    db = L.big_table()
    n = db.execute("SELECT COUNT(*) FROM big").fetchone()[0]
    p_before = L.plan(db, L.LOOKUP, (5,))
    steps_before = L.vm_steps(db, L.LOOKUP, (5,))
    probe = [int(k) for k in np.random.default_rng(1).integers(0, 200_000, 20)]
    t_scan = L.time_lookups(db, probe)
    expected = [db.execute(L.LOOKUP, (k,)).fetchall() for k in probe]
    db.execute("CREATE INDEX idx_key ON big(key)")
    p_after = L.plan(db, L.LOOKUP, (5,))
    steps_after = L.vm_steps(db, L.LOOKUP, (5,))
    t_idx = L.time_lookups(db, probe, repeats=3)
    checks.append(("the table has 200,000 rows", n == 200_000))
    checks.append(("plan before the index is a SCAN of the whole table", p_before.startswith("SCAN") and "INDEX" not in p_before))
    checks.append(("plan after the index is a SEARCH USING INDEX", p_after.startswith("SEARCH") and "USING INDEX" in p_after))
    checks.append(("the index returns the same rows as the scan", [db.execute(L.LOOKUP, (k,)).fetchall() for k in probe] == expected))
    checks.append(("operation count: the scan needs more than 100 times the steps of the index lookup",
                   steps_before > 100 * steps_after > 0))
    checks.append(("operation count: the scan grows with the table, over 200,000 steps", steps_before > 200_000))
    checks.append(("timing (illustrative, generous): scan is at least 10 times slower than the index", t_scan > 10 * t_idx))

    # B-tree levels
    checks.append(("worked example: 1,000,000 rows with 100 keys per node need 3 levels; binary search needs 20",
                   L.btree_levels(1_000_000, 100) == 3 and L.binary_steps(1_000_000) == 20))
    checks.append(("exact powers have no round-off: 10,000 rows need 2 levels, 10,001 rows need 3",
                   L.btree_levels(10_000, 100) == 2 and L.btree_levels(10_001, 100) == 3))
    checks.append(("200,000 rows with 100 keys per node need 3 levels; with 450 keys per node, 2",
                   L.btree_levels(200_000, 100) == 3 and L.btree_levels(200_000, 450) == 2))
    same = all(L.btree_levels(m, b) == L.simulated_levels(m, b) for m in (1, 2, 100, 101, 5000, 200_000, 1_000_000) for b in (10, 100, 450))
    checks.append(("the formula agrees with a step-by-step simulated search", same))
    checks.append(("a one-row table needs 1 level (edge case)", L.btree_levels(1, 100) == 1))

    checks.append(("the index lookup takes fewer than 100 steps", steps_after < 100))
    checks.append(("1,000,001 rows need 4 levels; 50,000,000 rows with 200 keys per node need 4 levels, binary search 26",
                   L.btree_levels(1_000_001, 100) == 4 and L.btree_levels(50_000_000, 200) == 4 and L.binary_steps(50_000_000) == 26))

    # transactions
    bank = L.make_bank()
    checks.append(("accounts hold 1000 in total", L.total_money(bank) == 1000))
    ok = L.transfer(bank, "Asha", "Bilal", 100, crash_after_debit=True)
    checks.append(("failed half-way transfer rolls back: balances unchanged, total still 1000",
                   (not ok) and L.balances(bank) == {"Asha": 500, "Bilal": 300, "Chitra": 200} and L.total_money(bank) == 1000))
    ok = L.transfer(bank, "Asha", "Bilal", 600)
    checks.append(("overdraft is rejected by CHECK and rolled back", (not ok) and L.total_money(bank) == 1000 and L.balances(bank)["Asha"] == 500))
    ok = L.transfer(bank, "Asha", "Bilal", 100)
    checks.append(("worked example: committed transfer of 100 gives Asha 400, Bilal 400, total 1000",
                   ok and L.balances(bank) == {"Asha": 400, "Bilal": 400, "Chitra": 200} and L.total_money(bank) == 1000))
    bad = L.make_bank()
    L.transfer_no_transaction(bad, "Asha", "Bilal", 100, crash_after_debit=True)
    checks.append(("without a transaction the same crash loses 100 (total 900)", L.total_money(bad) == 900))

    # injection
    users = L.make_users()
    evil = "x' OR '1'='1"
    checks.append(("a normal name finds one row both ways", len(L.lookup_unsafe(users, "Asha")) == 1 and len(L.lookup_safe(users, "Asha")) == 1))
    checks.append(("textbook injection string returns all 3 rows when glued into the SQL", len(L.lookup_unsafe(users, evil)) == 3))
    checks.append(("the parameterised query treats it as a name and returns 0 rows", L.lookup_safe(users, evil) == []))
    try:
        L.lookup_unsafe(users, "O'Brien")
        broke = False
    except Exception:
        broke = True
    checks.append(("a harmless apostrophe breaks the glued query but not the parameterised one",
                   broke and L.lookup_safe(users, "O'Brien") == []))

    # failure cases
    checks.append(("foreign key violation is rejected when enforcement is on", L.fk_demo(True) == "rejected"))
    checks.append(("with enforcement off the orphan loan is silently accepted", L.fk_demo(False) == "accepted"))
    slow, fast = L.orders_db(), L.orders_db(indexed=True)
    ps, pf = L.plan(slow, L.CUSTOMER_TOTAL, (7,)), L.plan(fast, L.CUSTOMER_TOTAL, (7,))
    checks.append(("join column without index: the plan scans orders", "SCAN o" in ps))
    checks.append(("join column with index: the plan searches orders by index", "SEARCH o USING" in pf and "idx_orders_cust" in pf))
    ids = [3, 77, 150, 1999, 0, 500, 1200, 64]
    a = [slow.execute(L.CUSTOMER_TOTAL, (i,)).fetchall() for i in ids]
    b = [fast.execute(L.CUSTOMER_TOTAL, (i,)).fetchall() for i in ids]
    py = {}
    for _, c, amt in slow.execute("SELECT order_id, cust_id, amount FROM orders"):
        py[c] = py.get(c, 0) + amt
    checks.append(("indexed and unindexed joins give the same totals, equal to plain Python",
                   a == b and all(r[0][1] == py[i] for r, i in zip(a, ids))))

    def clock(conn):
        import time
        t0 = time.perf_counter()
        for i in ids:
            conn.execute(L.CUSTOMER_TOTAL, (i,)).fetchall()
        return time.perf_counter() - t0
    checks.append(("timing (illustrative, generous): the unindexed join is at least 5 times slower", clock(slow) > 5 * min(clock(fast) for _ in range(3))))

    rng_sort = L.plan(db, "SELECT id, val FROM big WHERE key BETWEEN 10 AND 500 ORDER BY val")
    checks.append(("a single-column index still needs a temporary sort for a range query ordered by another column",
                   "USE TEMP B-TREE FOR ORDER BY" in rng_sort and "USING INDEX idx_key" in rng_sort))

    # canteen reference
    r1, r2, r3, total = L.canteen_reference()
    checks.append(("canteen: 40 sales, total revenue 2455 rupees, Thali earns most (900)",
                   len(L.canteen_sales()) == 40 and total == 2455 and r1[0] == ("Thali", 900) and sum(v for _, v in r1) == total))
    checks.append(("canteen: 6 customers spend at least 200 rupees; only Salad is never sold",
                   len(r2) == 6 and r3 == ["Salad"]))
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
