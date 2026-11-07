"""Session 2 (Level 2): ask precise questions, and store every fact once.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: ask precise questions, and store every fact once
# **A. Real-world problem.** A school has 40 students and three subjects: 120 marks. The head
# teacher wants the best five Science scores, the average per subject, and the students whose
# average is at least 75. Then a shop owner shows a spreadsheet where every order repeats the
# customer's city, and asks: "why did one customer end up in two cities?"
#
# **Plan.** (1) a synthetic school database, (2) SELECT with WHERE, ORDER BY, LIMIT, the
# aggregates and GROUP BY / HAVING, each *checked against plain Python*, (3) the anomalies of
# one big table and the cure (splitting into tables joined by keys), (4) a library design.

# %%
import datetime
import pathlib
import sqlite3

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SUBJECTS = ("Maths", "Science", "English")
CITIES = ("Pune", "Nashik", "Satara", "Kolhapur")


# %% [markdown]
# ## Step 1: a synthetic school database with two linked tables
# `students` has a **primary key** `id`: a value that identifies each row exactly once.
# `scores` has its own primary key and a **foreign key** `student_id` that must point at a real
# student. The data are random numbers from a fixed seed, so every run is identical.

# %%
def school_data(seed=7, n=40):
    rng = np.random.default_rng(seed)
    students = [(i + 1, f"S{i + 1:02d}", int(rng.integers(8, 11)), CITIES[int(rng.integers(0, len(CITIES)))])
                for i in range(n)]
    scores, sid = [], 1
    for s in students:
        for sub in SUBJECTS:
            scores.append((sid, s[0], sub, int(rng.integers(30, 100))))
            sid += 1
    return students, scores


def make_school_db(students, scores):
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, grade INTEGER, city TEXT)")
    conn.execute("""CREATE TABLE scores (
        score_id INTEGER PRIMARY KEY,
        student_id INTEGER NOT NULL REFERENCES students(id),
        subject TEXT NOT NULL,
        marks INTEGER NOT NULL)""")
    conn.executemany("INSERT INTO students VALUES (?, ?, ?, ?)", students)
    conn.executemany("INSERT INTO scores VALUES (?, ?, ?, ?)", scores)
    conn.commit()
    return conn


# %% [markdown]
# ## Step 2: five questions, each answered twice
# * **WHERE**: keep rows that satisfy a condition.
# * **ORDER BY ... LIMIT**: sort, then keep only the first few.
# * **COUNT, SUM, AVG, MIN, MAX**: collapse many rows into one number.
# * **GROUP BY**: one answer row per group (here per subject or per student).
# * **HAVING**: keep only the groups that satisfy a condition (WHERE works on rows *before*
#   grouping, HAVING works on groups *after*).

# %%
SQL = {
    "where": "SELECT student_id FROM scores WHERE subject = 'Maths' AND marks >= 80 ORDER BY student_id",
    "top5": "SELECT student_id, marks FROM scores WHERE subject = 'Science' ORDER BY marks DESC, student_id LIMIT 5",
    "agg": "SELECT COUNT(*), SUM(marks), AVG(marks), MIN(marks), MAX(marks) FROM scores WHERE subject = 'Maths'",
    "group": "SELECT subject, COUNT(*), AVG(marks) FROM scores GROUP BY subject ORDER BY subject",
    "having": "SELECT student_id, AVG(marks) FROM scores GROUP BY student_id HAVING AVG(marks) >= 75 ORDER BY student_id",
}


def run_sql(conn, key):
    return conn.execute(SQL[key]).fetchall()


def reference(key, scores):
    """The same answers computed with plain Python and numpy, never touching SQL."""
    if key == "where":
        return [(s[1],) for s in scores if s[2] == "Maths" and s[3] >= 80]
    if key == "top5":
        sci = sorted((s for s in scores if s[2] == "Science"), key=lambda s: (-s[3], s[1]))
        return [(s[1], s[3]) for s in sci[:5]]
    if key == "agg":
        m = np.array([s[3] for s in scores if s[2] == "Maths"])
        return [(len(m), int(m.sum()), float(m.mean()), int(m.min()), int(m.max()))]
    if key == "group":
        out = []
        for sub in sorted(SUBJECTS):
            m = np.array([s[3] for s in scores if s[2] == sub])
            out.append((sub, len(m), float(m.mean())))
        return out
    if key == "having":
        out = []
        for sid in sorted({s[1] for s in scores}):
            m = np.array([s[3] for s in scores if s[1] == sid])
            if m.mean() >= 75:
                out.append((sid, float(m.mean())))
        return out
    raise KeyError(key)


def same(a, b, tol=1e-9):
    """Compare two lists of tuples, allowing a tiny difference in floating-point numbers."""
    if len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if len(ra) != len(rb):
            return False
        for x, y in zip(ra, rb):
            if isinstance(x, float) or isinstance(y, float):
                if abs(x - y) > tol:
                    return False
            elif x != y:
                return False
    return True


# %% [markdown]
# ### A six-row table you can do by hand
# Three students, two subjects. `GROUP BY subject` makes two groups; `HAVING AVG(marks) > 70`
# keeps only the groups whose average beats 70.

# %%
TINY = [(1, "Maths", 70), (2, "Maths", 90), (3, "Maths", 80), (1, "Science", 60), (2, "Science", 50), (3, "Science", 85)]


def tiny_groups(min_avg=70):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (student_id INTEGER, subject TEXT, marks INTEGER)")
    conn.executemany("INSERT INTO t VALUES (?, ?, ?)", TINY)
    sql = "SELECT subject, SUM(marks), AVG(marks) FROM t GROUP BY subject HAVING AVG(marks) > ? ORDER BY subject"
    return conn.execute(sql, (min_avg,)).fetchall()


# %% [markdown]
# ## Step 3: one big table and its anomalies
# A shop stores every order in a single table. The customer's city and the item's price are
# repeated on every row that mentions them. That repetition causes three **anomalies**:
# * **update**: change a city on one row only and the customer now lives in two cities;
# * **insert**: a new customer with no order cannot be stored (the order columns are required);
# * **delete**: deleting a customer's only order deletes the only record of their city.
#
# **Normalisation** cures them. First normal form (1NF): every cell holds one value. Second
# (2NF): every non-key column depends on the whole key. Third (3NF): no non-key column depends
# on another non-key column. Here `city` depends on `customer` and `price` depends on `item`,
# which are not the key `order_id`: that is the 3NF violation. Fix: one table per entity.

# %%
CUSTOMERS = {1: ("Meera", "Pune"), 2: ("Ravi", "Nashik"), 3: ("Tara", "Pune")}
ITEMS = {1: ("Pen", 10), 2: ("Notebook", 40), 3: ("Bag", 350)}
ORDERS = [(1, 1, 1, 5), (2, 1, 2, 2), (3, 2, 1, 10), (4, 2, 3, 1), (5, 3, 2, 3), (6, 1, 3, 1),
          (7, 3, 1, 4), (8, 2, 2, 6), (9, 1, 1, 2), (10, 3, 3, 1), (11, 2, 1, 1), (12, 1, 2, 1)]
# order = (order_id, customer_id, item_id, quantity)


def big_rows():
    """The flat spreadsheet: (order_id, customer, city, item, price, qty)."""
    return [(o, CUSTOMERS[c][0], CUSTOMERS[c][1], ITEMS[i][0], ITEMS[i][1], q) for o, c, i, q in ORDERS]


def make_big_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE big (order_id INTEGER PRIMARY KEY, customer TEXT NOT NULL, city TEXT NOT NULL,
                    item TEXT NOT NULL, price INTEGER NOT NULL, qty INTEGER NOT NULL)""")
    conn.executemany("INSERT INTO big VALUES (?, ?, ?, ?, ?, ?)", big_rows())
    return conn


def cities_of(conn, customer):
    return sorted(r[0] for r in conn.execute("SELECT DISTINCT city FROM big WHERE customer = ?", (customer,)))


def update_anomaly(conn):
    """Move Meera on ONE row only: she now has two cities."""
    conn.execute("UPDATE big SET city = 'Mumbai' WHERE order_id = 1")
    return cities_of(conn, "Meera")


def insert_anomaly(conn):
    """A new customer who has not ordered yet cannot be stored: item and price are required."""
    try:
        conn.execute("INSERT INTO big (customer, city) VALUES ('Uma', 'Satara')")
        return False
    except sqlite3.IntegrityError:
        return True


def delete_anomaly(conn):
    """Delete Ravi's orders... then Ravi's city is gone. Returns how many rows still mention Ravi."""
    conn.execute("DELETE FROM big WHERE customer = 'Ravi'")
    return conn.execute("SELECT COUNT(*) FROM big WHERE customer = 'Ravi'").fetchone()[0]


def make_3nf_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL)")
    conn.execute("CREATE TABLE items (item_id INTEGER PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL)")
    conn.execute("""CREATE TABLE orders (order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                    item_id INTEGER NOT NULL REFERENCES items(item_id),
                    qty INTEGER NOT NULL)""")
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?)", [(k,) + v for k, v in CUSTOMERS.items()])
    conn.executemany("INSERT INTO items VALUES (?, ?, ?)", [(k,) + v for k, v in ITEMS.items()])
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", ORDERS)
    return conn


REJOIN = """SELECT o.order_id, c.name, c.city, i.name, i.price, o.qty
            FROM orders o JOIN customers c ON c.customer_id = o.customer_id
                          JOIN items i ON i.item_id = o.item_id ORDER BY o.order_id"""


def count_cells(conn, tables):
    """Cells stored = rows x columns, summed over the tables."""
    total = 0
    for t in tables:
        rows = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        cols = len(conn.execute(f"PRAGMA table_info({t})").fetchall())
        total += rows * cols
    return total


def cells_big(n):
    """The big table has 6 columns per order."""
    return 6 * n


def cells_normalised(n, k, m=3):
    """n orders x 4 columns, k customers x 3 columns, m items x 3 columns."""
    return 4 * n + 3 * k + 3 * m


# %% [markdown]
# ## Step 4: a design problem, the library
# Books, members and loans. A member borrows many books over time and a book is borrowed by many
# members over time, so the link between them gets its own table, `loans`, holding two foreign
# keys. A loan with `returned_on` empty (NULL) is still out. The overdue query: still out, and the
# due date is before today.

# %%
TODAY = "2026-03-10"
BOOKS = [(1, "Wings of Fire"), (2, "Malgudi Days"), (3, "Gitanjali"), (4, "Discovery of India"), (5, "Godan"), (6, "Panchatantra")]
MEMBERS = [(1, "Anita"), (2, "Bharat"), (3, "Chetna"), (4, "Dinesh")]
LOANS = [  # (loan_id, book_id, member_id, loaned_on, due_on, returned_on)
    (1, 1, 1, "2026-02-01", "2026-02-15", "2026-02-14"),
    (2, 2, 1, "2026-02-20", "2026-03-06", None),
    (3, 3, 2, "2026-02-10", "2026-02-24", "2026-03-01"),
    (4, 1, 3, "2026-03-01", "2026-03-15", None),
    (5, 4, 2, "2026-02-25", "2026-03-11", None),
    (6, 5, 4, "2026-01-30", "2026-02-13", None),
    (7, 2, 3, "2026-02-05", "2026-02-19", "2026-02-19"),
    (8, 6, 1, "2026-03-10", "2026-03-24", None),
    (9, 3, 4, "2026-02-24", "2026-03-10", None),
]
OVERDUE_SQL = """SELECT l.loan_id, m.name, b.title, CAST(julianday(?) - julianday(l.due_on) AS INTEGER) AS days_late
                 FROM loans l JOIN books b ON b.book_id = l.book_id JOIN members m ON m.member_id = l.member_id
                 WHERE l.returned_on IS NULL AND l.due_on < ? ORDER BY l.loan_id"""


def make_library_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL)")
    conn.execute("CREATE TABLE members (member_id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
    conn.execute("""CREATE TABLE loans (loan_id INTEGER PRIMARY KEY,
                    book_id INTEGER NOT NULL REFERENCES books(book_id),
                    member_id INTEGER NOT NULL REFERENCES members(member_id),
                    loaned_on TEXT NOT NULL, due_on TEXT NOT NULL, returned_on TEXT)""")
    conn.executemany("INSERT INTO books VALUES (?, ?)", BOOKS)
    conn.executemany("INSERT INTO members VALUES (?, ?)", MEMBERS)
    conn.executemany("INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?)", LOANS)
    return conn


def overdue_sql(conn, today=TODAY):
    return conn.execute(OVERDUE_SQL, (today, today)).fetchall()


def overdue_python(today=TODAY):
    """Independent check with the datetime module. ISO dates (YYYY-MM-DD) compare correctly as text too."""
    t = datetime.date.fromisoformat(today)
    book = dict(BOOKS)
    member = dict(MEMBERS)
    out = []
    for loan_id, b, m, _, due, ret in LOANS:
        d = datetime.date.fromisoformat(due)
        if ret is None and d < t:
            out.append((loan_id, member[m], book[b], (t - d).days))
    return out


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    students, scores = school_data()
    db = make_school_db(students, scores)
    for key in SQL:
        a, b = run_sql(db, key), reference(key, scores)
        print(f"{key:7s} rows={len(a):3d} SQL equals Python: {same(a, b)}")
    print("Maths aggregates (count, sum, avg, min, max):", run_sql(db, "agg")[0])
    print("tiny table, groups with average above 70:", tiny_groups(70), "| above 60:", tiny_groups(60))

    big = make_big_db()
    print("Meera's cities before:", cities_of(big, "Meera"), "after one-row update:", update_anomaly(big))
    print("insert anomaly raised:", insert_anomaly(make_big_db()), "| rows left after deleting Ravi's orders:", delete_anomaly(make_big_db()))
    nf = make_3nf_db()
    print("3NF join equals big table:", nf.execute(REJOIN).fetchall() == big_rows())
    print("cells big:", count_cells(make_big_db(), ["big"]), " cells 3NF:", count_cells(nf, ["customers", "items", "orders"]))
    print("overdue loans:", overdue_sql(make_library_db()))

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    subj = run_sql(db, "group")
    axes[0].bar([r[0] for r in subj], [r[2] for r in subj], color="#2a9d8f")
    axes[0].set_ylabel("average marks (marks)")
    axes[0].set_title("GROUP BY subject: AVG(marks)")
    axes[0].set_ylim(0, 100)
    axes[0].grid(axis="y", alpha=0.3)
    ns = np.arange(10, 1001, 10)
    axes[1].plot(ns, [cells_big(n) for n in ns], label="one big table (6 columns)")
    axes[1].plot(ns, [cells_normalised(n, 20) for n in ns], label="3NF, 20 customers, 3 items")
    axes[1].set_xlabel("orders stored (orders)")
    axes[1].set_ylabel("cells stored (cells)")
    axes[1].set_title("Splitting the table stores fewer cells")
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "queries_and_cells.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Every query here reads a few hundred rows, so speed does not matter yet. Session 3 uses larger
# tables to show when it does, and adds transactions, indexes and the safety of queries.
