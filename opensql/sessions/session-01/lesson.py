"""Session 1 (Level 1): a table is a grid, and a query asks it a question.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a table is a grid, a query asks it a question
# **A. Real-world problem.** A school keeps marks for hundreds of students. The teacher asks
# "who scored at least 60?" or "who is in grade 9 or above and scored at least 70?". Nobody
# wants to read every row. A *database* keeps the rows in a *table* and a *query* asks the
# question for us. All names and marks here are synthetic.
#
# **Plan.** (1) build a table of 12 rows, (2) ask a question in plain Python, (3) ask the same
# question in SQL with Python's built-in `sqlite3` (nothing to install), (4) check that both
# answers are identical, (5) plot how the answer changes with the cut-off.

# %%
import pathlib
import sqlite3

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

COLUMNS = ("id", "name", "grade", "marks")
ROWS = [
    (1, "Asha", 8, 72), (2, "Bilal", 8, 45), (3, "Chitra", 9, 88), (4, "Dev", 9, 61),
    (5, "Esha", 8, 90), (6, "Farid", 10, 55), (7, "Gita", 10, 67), (8, "Hari", 9, 39),
    (9, "Indu", 10, 95), (10, "Jai", 8, 58), (11, "Kavya", 9, 76), (12, "Lalit", 10, 49),
]


# %% [markdown]
# ## Step 1: the table
# A table is a grid. Each **row** is one student, each **column** is one fact about every
# student. In SQL we create it once and then put the rows in. `:memory:` means the database
# lives only in RAM and disappears when the program ends, which is perfect for learning.

# %%
def make_table():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, grade INTEGER, marks INTEGER)")
    conn.executemany("INSERT INTO students VALUES (?, ?, ?, ?)", ROWS)
    conn.commit()
    return conn


# %% [markdown]
# ## Step 2: a question in plain Python
# "Keep the rows whose marks are at least `min_marks` and whose grade is at least `min_grade`."
# A **filter** keeps the rows where the condition is true and drops the others.

# %%
def python_filter(rows, min_marks, min_grade=0):
    return [r for r in rows if r[3] >= min_marks and r[2] >= min_grade]


# %% [markdown]
# ## Step 3: the same question in SQL
#
#     SELECT id, name, grade, marks   -- which columns to show
#     FROM students                   -- which table
#     WHERE marks >= 60 AND grade >= 8   -- the filter
#     ORDER BY id                     -- the order of the answer
#
# The `?` marks are *parameters*: Python fills them in safely (Session 3 shows why that matters).

# %%
def sql_filter(conn, min_marks, min_grade=0):
    sql = "SELECT id, name, grade, marks FROM students WHERE marks >= ? AND grade >= ? ORDER BY id"
    return conn.execute(sql, (min_marks, min_grade)).fetchall()


def numpy_count(min_marks, min_grade=0):
    """A third, independent way: boolean masks on numpy columns. Returns how many rows pass."""
    grade = np.array([r[2] for r in ROWS])
    marks = np.array([r[3] for r in ROWS])
    return int(np.sum((marks >= min_marks) & (grade >= min_grade)))


def count_curve(thresholds, min_grade=0):
    """How many rows pass for each cut-off (the step curve of the second figure)."""
    return [len(python_filter(ROWS, t, min_grade)) for t in thresholds]


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    conn = make_table()
    kept = sql_filter(conn, 60, 8)
    print("SQL answer, marks >= 60:", [r[1] for r in kept], "->", len(kept), "of", len(ROWS))
    print("Python answer matches SQL:", kept == python_filter(ROWS, 60, 8))
    print("numpy count:", numpy_count(60, 8))
    worked = sql_filter(conn, 70, 9)
    print("grade >= 9 and marks >= 70:", [r[1] for r in worked])

    # figure 1: the table with a filter
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.set_xlim(0, 4)
    ax.set_ylim(len(ROWS) + 1, 0)
    ax.axis("off")
    keep_ids = {r[0] for r in kept}
    for j, name in enumerate(COLUMNS):
        ax.text(j + 0.5, 0.5, name, ha="center", va="center", weight="bold")
    for i, row in enumerate(ROWS, start=1):
        hit = row[0] in keep_ids
        ax.add_patch(plt.Rectangle((0, i), 4, 1, color="#2a9d8f" if hit else "#e5e5e5", alpha=0.55 if hit else 0.35))
        for j, v in enumerate(row):
            ax.text(j + 0.5, i + 0.5, str(v), ha="center", va="center", color="black" if hit else "#777")
    ax.set_title(f"WHERE marks >= 60 AND grade >= 8: {len(kept)} of {len(ROWS)} rows kept (green)")
    fig.tight_layout()
    fig.savefig(OUT / "table_filter.png", dpi=120)

    # figure 2: number of rows kept against the cut-off
    ts = np.arange(0, 101)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.step(ts, count_curve(ts, 0), where="post", label="all grades")
    ax2.step(ts, count_curve(ts, 9), where="post", label="grade 9 and above")
    ax2.set_xlabel("cut-off marks (marks)")
    ax2.set_ylabel("rows kept (rows)")
    ax2.set_title("Raising the cut-off keeps fewer rows")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "rows_vs_cutoff.png", dpi=120)

# %% [markdown]
# ## Where this stops
# One table and one filter is the whole of Session 1. Session 2 adds counting, averaging,
# grouping and the question of how to split data into several tables.
