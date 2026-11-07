"""Session 3 (Level 3): joins, the cost of a query, transactions and safe queries.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: how fast, how safe, how right
# **A. Real-world problem.** A shop database holds 200,000 rows. One query finds a customer's
# orders in a blink and another makes the page hang. A transfer between two accounts must never
# lose money even if the power fails half-way. And a search box must never let a visitor's text
# become part of the program. This session builds the evidence for each claim.
#
# **Plan.** (1) JOIN checked against nested loops, (2) read the *query plan*, measure a scan and an
# index lookup on 200,000 rows, (3) count B-tree levels, (4) atomic transactions, (5) SQL
# injection and parameters, (6) failure cases: a missing index and a foreign key violation.
# Timings depend on your computer and are illustrative; plans, counts and results are exact.

# %%
import pathlib
import sqlite3
import time

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: JOIN is a nested loop with a condition
# `customers` and `orders` are linked by `cust_id`. An **inner join** pairs every order with its
# customer; a **left join** also keeps customers with no orders (their order columns are NULL,
# Python's `None`). We check the SQL against two plain `for` loops.

# %%
CUSTOMERS = [(1, "Meera", "Pune"), (2, "Ravi", "Nashik"), (3, "Tara", "Pune"), (4, "Uma", "Satara"),
             (5, "Vikram", "Nashik"), (6, "Wasim", "Pune"), (7, "Xena", "Satara"), (8, "Yash", "Pune")]
ORDERS = [(1, 1, 250), (2, 1, 90), (3, 2, 400), (4, 3, 120), (5, 3, 75), (6, 3, 310), (7, 4, 60),
          (8, 5, 500), (9, 2, 45), (10, 1, 180), (11, 6, 220), (12, 4, 95), (13, 5, 130), (14, 6, 35)]
# customers 7 and 8 have no orders


def shop_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("CREATE TABLE customers (cust_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT)")
    conn.execute("""CREATE TABLE orders (order_id INTEGER PRIMARY KEY,
                    cust_id INTEGER NOT NULL REFERENCES customers(cust_id), amount INTEGER NOT NULL)""")
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?)", CUSTOMERS)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?)", ORDERS)
    return conn


def join_sql(conn, kind="INNER"):
    sql = f"""SELECT c.cust_id, c.name, o.order_id, o.amount FROM customers c
              {kind} JOIN orders o ON o.cust_id = c.cust_id ORDER BY c.cust_id, o.order_id"""
    return conn.execute(sql).fetchall()


def join_loops(customers, orders, left=False):
    """The same join with two nested loops and no SQL."""
    out = []
    for c in customers:
        matched = False
        for o in orders:
            if o[1] == c[0]:
                out.append((c[0], c[1], o[0], o[2]))
                matched = True
        if left and not matched:
            out.append((c[0], c[1], None, None))
    return sorted(out, key=lambda r: (r[0], r[2] if r[2] is not None else -1))


# %% [markdown]
# ## Step 2: the cost of a query
# `EXPLAIN QUERY PLAN` asks the database *how* it will answer. "SCAN" means it reads every row;
# "SEARCH ... USING INDEX" means it jumps straight to the matching rows through an **index**, a
# sorted structure kept beside the table (like the index at the back of a book).
# We also count the database's own virtual-machine steps with a progress handler. That count is
# exact and repeatable, unlike a clock.

# %%
def big_table(n=200_000, seed=11):
    """n rows (id, key, val); key is a shuffled copy of 0..n-1 so every key is unique."""
    rng = np.random.default_rng(seed)
    keys = rng.permutation(n)
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE big (id INTEGER PRIMARY KEY, key INTEGER, val INTEGER)")
    rows = zip(range(n), keys.tolist(), rng.integers(0, 1000, n).tolist())
    conn.executemany("INSERT INTO big VALUES (?, ?, ?)", rows)
    conn.commit()
    return conn


LOOKUP = "SELECT id, val FROM big WHERE key = ?"


def plan(conn, sql, params=()):
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return " | ".join(r[3] for r in rows)


def vm_steps(conn, sql, params=()):
    """Number of virtual-machine instructions SQLite runs to answer the query."""
    count = [0]

    def tick():
        count[0] += 1
        return 0

    conn.set_progress_handler(tick, 1)
    conn.execute(sql, params).fetchall()
    conn.set_progress_handler(None, 0)
    return count[0]


def time_lookups(conn, keys, repeats=1):
    """Seconds to run the lookup for every key in `keys` (best of `repeats`)."""
    best = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        for k in keys:
            conn.execute(LOOKUP, (k,)).fetchall()
        dt = time.perf_counter() - t0
        best = dt if best is None else min(best, dt)
    return best


# %% [markdown]
# ## Step 3: why an index is fast, the B-tree idea
# A B-tree node holds up to B keys, so each step down the tree divides the remaining rows by
# about B. The number of levels is the smallest d with B^d >= n, roughly log n / log B. With one
# million rows and 100 keys per node that is 3 levels. Binary search on a sorted list halves the
# range each time, so it needs about log2 n comparisons: 20 for a million.

# %%
def btree_levels(n, keys_per_node):
    """Smallest d with keys_per_node**d >= n, using integers only (no round-off)."""
    d, reach = 0, 1
    while reach < n:
        reach *= keys_per_node
        d += 1
    return max(d, 1)


def simulated_levels(n, keys_per_node):
    """Independent check: search a sorted range, splitting it into `keys_per_node` pieces per level."""
    lo, hi, steps = 0, n, 0
    while hi - lo > 1:
        size = hi - lo
        piece = -(-size // keys_per_node)     # ceiling division
        hi = lo + min(piece, size)
        steps += 1
    return max(steps, 1)


def binary_steps(n):
    """Comparisons binary search needs in the worst case: ceil(log2 n)."""
    d, reach = 0, 1
    while reach < n:
        reach *= 2
        d += 1
    return d


# %% [markdown]
# ## Step 4: transactions, all or nothing
# A transfer is two UPDATEs: take from one account, add to another. If the program dies between
# them, money vanishes. A **transaction** groups statements: `COMMIT` makes them all permanent,
# `ROLLBACK` undoes them all. The table also has `CHECK (balance >= 0)`, so an overdraft is
# rejected by the database itself.

# %%
def make_bank():
    conn = sqlite3.connect(":memory:", isolation_level=None)      # we send BEGIN/COMMIT ourselves
    conn.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0))")
    conn.executemany("INSERT INTO accounts VALUES (?, ?)", [("Asha", 500), ("Bilal", 300), ("Chitra", 200)])
    return conn


def total_money(conn):
    return conn.execute("SELECT SUM(balance) FROM accounts").fetchone()[0]


def balances(conn):
    return dict(conn.execute("SELECT name, balance FROM accounts ORDER BY name").fetchall())


def transfer(conn, src, dst, amount, crash_after_debit=False):
    """Atomic transfer. Returns True if committed, False if rolled back."""
    conn.execute("BEGIN")
    try:
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, src))
        if crash_after_debit:
            raise RuntimeError("power cut between the two updates")
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, dst))
        conn.execute("COMMIT")
        return True
    except (RuntimeError, sqlite3.IntegrityError):
        conn.execute("ROLLBACK")
        return False


def transfer_no_transaction(conn, src, dst, amount, crash_after_debit=False):
    """The same two updates with no BEGIN: each one commits by itself (the dangerous way)."""
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, src))
    if crash_after_debit:
        return False
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, dst))
    return True


# %% [markdown]
# ## Step 5: SQL injection, and the fix
# If a program glues the visitor's text into the SQL string, the visitor's text can change the
# *meaning* of the query. The textbook example below runs on our own throw-away in-memory
# database and only shows the defence: pass values as **parameters** (`?`), which the database
# always treats as data, never as SQL.

# %%
def make_users():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (name TEXT, secret TEXT)")
    conn.executemany("INSERT INTO users VALUES (?, ?)", [("Asha", "red"), ("Bilal", "green"), ("Chitra", "blue")])
    return conn


def lookup_unsafe(conn, name):
    sql = "SELECT name, secret FROM users WHERE name = '" + name + "'"      # BAD: text becomes SQL
    return conn.execute(sql).fetchall()


def lookup_safe(conn, name):
    return conn.execute("SELECT name, secret FROM users WHERE name = ?", (name,)).fetchall()


# %% [markdown]
# ## Step 6: two failure cases
# * A join column with no index: every lookup scans the whole table.
# * A foreign key that points nowhere: SQLite *ignores* foreign keys unless you switch them on
#   with `PRAGMA foreign_keys = ON` in every connection. Switched on, the bad row is rejected.

# %%
def orders_db(n_orders=200_000, n_customers=2_000, seed=5, indexed=False):
    rng = np.random.default_rng(seed)
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE customers (cust_id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("CREATE TABLE orders (order_id INTEGER PRIMARY KEY, cust_id INTEGER, amount INTEGER)")
    conn.executemany("INSERT INTO customers VALUES (?, ?)", [(i, f"C{i}") for i in range(n_customers)])
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?)",
                     zip(range(n_orders), rng.integers(0, n_customers, n_orders).tolist(), rng.integers(1, 500, n_orders).tolist()))
    if indexed:
        conn.execute("CREATE INDEX idx_orders_cust ON orders(cust_id)")
    conn.commit()
    conn.execute("PRAGMA automatic_index = OFF")      # keep the demonstration honest: no hidden helper index
    return conn


CUSTOMER_TOTAL = """SELECT c.name, SUM(o.amount) FROM customers c JOIN orders o ON o.cust_id = c.cust_id
                    WHERE c.cust_id = ? GROUP BY c.cust_id"""


def fk_demo(enforce):
    """Try to loan a book that does not exist. Returns 'rejected' or 'accepted'."""
    conn = sqlite3.connect(":memory:")
    conn.execute(f"PRAGMA foreign_keys = {'ON' if enforce else 'OFF'}")
    conn.execute("CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT)")
    conn.execute("CREATE TABLE loans (loan_id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL REFERENCES books(book_id))")
    conn.execute("INSERT INTO books VALUES (1, 'Godan')")
    try:
        conn.execute("INSERT INTO loans VALUES (1, 99)")
        return "accepted"
    except sqlite3.IntegrityError:
        return "rejected"


# %% [markdown]
# ## Mini-project data: a small canteen
# Six items, eight customers and 40 sales, all synthetic. The reference answers below are
# computed with plain Python. Your job (see the project text): create the tables and write the
# SQL for three reports whose results equal these.

# %%
CANTEEN_ITEMS = [(1, "Samosa", 15), (2, "Tea", 10), (3, "Sandwich", 30), (4, "Juice", 25), (5, "Thali", 60), (6, "Salad", 20)]
CANTEEN_CUSTOMERS = [(1, "Aarav"), (2, "Diya"), (3, "Ishaan"), (4, "Kiara"), (5, "Laksh"), (6, "Myra"), (7, "Neel"), (8, "Pari")]


def canteen_sales(seed=21, n=40):
    """(sale_id, cust_id, item_id, qty). Item 6 (Salad) is never sold."""
    rng = np.random.default_rng(seed)
    return [(i + 1, int(rng.integers(1, 9)), int(rng.integers(1, 6)), int(rng.integers(1, 4))) for i in range(n)]


def canteen_reference(min_spend=200):
    """Three reports in plain Python."""
    price = {i: p for i, _, p in CANTEEN_ITEMS}
    item_name = {i: n for i, n, _ in CANTEEN_ITEMS}
    cust_name = {c: n for c, n in CANTEEN_CUSTOMERS}
    sales = canteen_sales()
    revenue, spend = {}, {}
    for _, c, i, q in sales:
        revenue[i] = revenue.get(i, 0) + q * price[i]
        spend[c] = spend.get(c, 0) + q * price[i]
    report1 = sorted(((item_name[i], r) for i, r in revenue.items()), key=lambda t: (-t[1], t[0]))
    report2 = sorted(((cust_name[c], s) for c, s in spend.items() if s >= min_spend), key=lambda t: (-t[1], t[0]))
    report3 = sorted(item_name[i] for i in item_name if i not in revenue)
    return report1, report2, report3, sum(revenue.values())


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    shop = shop_db()
    print("inner join rows:", len(join_sql(shop)), "| left join rows:", len(join_sql(shop, "LEFT")))
    print("SQL = loops (inner, left):", join_sql(shop) == join_loops(CUSTOMERS, ORDERS),
          join_sql(shop, "LEFT") == join_loops(CUSTOMERS, ORDERS, left=True))

    db = big_table()
    probe = [int(k) for k in np.random.default_rng(1).integers(0, 200_000, 20)]
    print("plan before index:", plan(db, LOOKUP, (5,)))
    scan_steps = vm_steps(db, LOOKUP, (5,))
    t_scan = time_lookups(db, probe)
    db.execute("CREATE INDEX idx_key ON big(key)")
    print("plan after index: ", plan(db, LOOKUP, (5,)))
    idx_steps = vm_steps(db, LOOKUP, (5,))
    t_idx = time_lookups(db, probe)
    print(f"VM steps: scan {scan_steps}, index {idx_steps}")
    print(f"20 lookups: scan {t_scan * 1000:.1f} ms, index {t_idx * 1000:.3f} ms (illustrative)")
    print("levels for 1,000,000 rows, 100 keys per node:", btree_levels(1_000_000, 100),
          "| binary search:", binary_steps(1_000_000))

    bank = make_bank()
    print("before:", balances(bank), "total", total_money(bank))
    print("failed half-way transfer committed?", transfer(bank, "Asha", "Bilal", 100, crash_after_debit=True), balances(bank))
    print("overdraft committed?", transfer(bank, "Asha", "Bilal", 600), balances(bank))
    print("good transfer committed?", transfer(bank, "Asha", "Bilal", 100), balances(bank), "total", total_money(bank))

    users = make_users()
    evil = "x' OR '1'='1"
    print("unsafe rows:", len(lookup_unsafe(users, evil)), "| safe rows:", len(lookup_safe(users, evil)))
    print("foreign key enforced:", fk_demo(True), "| not enforced:", fk_demo(False))

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(["full scan", "index lookup"], [t_scan / len(probe) * 1000, t_idx / len(probe) * 1000], color=["#d9534f", "#2a9d8f"])
    axes[0].set_yscale("log")
    axes[0].set_ylabel("time per lookup (ms, log scale)")
    axes[0].set_title("200,000 rows, illustrative timing")
    ns = np.logspace(2, 7, 60)
    axes[1].plot(ns, [btree_levels(int(n), 100) for n in ns], drawstyle="steps-post", label="B-tree, 100 keys per node")
    axes[1].plot(ns, [binary_steps(int(n)) for n in ns], drawstyle="steps-post", label="binary search")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("rows (rows, log scale)")
    axes[1].set_ylabel("steps to find one row")
    axes[1].set_title("Steps grow like log n; a scan grows like n")
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "scan_vs_index.png", dpi=120)

    r1, r2, r3, total = canteen_reference()
    print("canteen revenue", total, "| top item", r1[0], "| big spenders", len(r2), "| never sold", r3)

# %% [markdown]
# ## Where this stops
# SQLite is a single-file database. Servers such as PostgreSQL add many simultaneous users,
# permissions and replication, but the ideas in this repo (tables, keys, joins, indexes,
# transactions, parameters) carry over unchanged.
