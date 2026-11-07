"""Checkpoint for Session 2. Prints PASS or FAIL."""
import sqlite3

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    students, scores = L.school_data()
    db = L.make_school_db(students, scores)
    checks.append(("40 students and 120 scores", len(students) == 40 and len(scores) == 120))
    for key in L.SQL:
        checks.append((f"SQL query '{key}' equals the plain Python computation",
                       L.same(L.run_sql(db, key), L.reference(key, scores))))
    agg = L.run_sql(db, "agg")[0]
    checks.append(("Maths aggregates: count 40, sum 2607, average 65.175, min 30, max 98",
                   agg[0] == 40 and agg[1] == 2607 and abs(agg[2] - 65.175) < 1e-9 and agg[3] == 30 and agg[4] == 98))
    checks.append(("11 Maths scores of at least 80 and 8 students averaging at least 75",
                   len(L.run_sql(db, "where")) == 11 and len(L.run_sql(db, "having")) == 8))
    checks.append(("ORDER BY ... LIMIT 5 returns 5 rows in falling order",
                   len(L.run_sql(db, "top5")) == 5 and [r[1] for r in L.run_sql(db, "top5")] == sorted([r[1] for r in L.run_sql(db, "top5")], reverse=True)))

    # worked example: six-row table by hand: Maths 70+90+80 = 240, average 80; Science 60+50+85 = 195, average 65
    g = L.tiny_groups(70)
    checks.append(("worked example: HAVING AVG > 70 keeps only Maths (sum 240, average 80)",
                   len(g) == 1 and g[0][0] == "Maths" and g[0][1] == 240 and abs(g[0][2] - 80.0) < 1e-12))
    g60 = L.tiny_groups(60)
    checks.append(("worked example: Science has sum 195 and average 65, so AVG > 60 keeps both subjects",
                   len(g60) == 2 and g60[1][0] == "Science" and g60[1][1] == 195 and abs(g60[1][2] - 65.0) < 1e-12))
    checks.append(("edge: HAVING is strict, so AVG > 80 keeps nothing", L.tiny_groups(80) == []))

    # primary key and foreign key
    try:
        db.execute("INSERT INTO scores VALUES (1000, 999, 'Maths', 50)")
        fk_ok = False
    except sqlite3.IntegrityError:
        fk_ok = True
    checks.append(("a score for a student that does not exist is rejected (foreign key)", fk_ok))
    try:
        db.execute("INSERT INTO students VALUES (1, 'dup', 8, 'Pune')")
        pk_ok = False
    except sqlite3.IntegrityError:
        pk_ok = True
    checks.append(("a second student with id 1 is rejected (primary key)", pk_ok))

    # anomalies and 3NF
    big = L.make_big_db()
    checks.append(("update anomaly: one-row change leaves Meera with two cities",
                   L.cities_of(big, "Meera") == ["Pune"] and L.update_anomaly(big) == ["Mumbai", "Pune"]))
    checks.append(("insert anomaly: a customer with no order is rejected", L.insert_anomaly(L.make_big_db())))
    checks.append(("delete anomaly: removing Ravi's orders removes every trace of him", L.delete_anomaly(L.make_big_db()) == 0))
    nf = L.make_3nf_db()
    checks.append(("3NF tables joined give back the big table exactly", nf.execute(L.REJOIN).fetchall() == L.big_rows()))
    cb = L.count_cells(L.make_big_db(), ["big"])
    cn = L.count_cells(nf, ["customers", "items", "orders"])
    checks.append(("12 orders: 72 cells in the big table, 66 cells in three tables",
                   cb == 72 == L.cells_big(12) and cn == 66 == L.cells_normalised(12, 3)))
    checks.append(("with 500 orders and 10 customers 3NF stores 2039 cells against 3000, under 70 percent",
                   L.cells_normalised(500, 10) == 2039 and L.cells_big(500) == 3000 and L.cells_normalised(500, 10) < 0.7 * L.cells_big(500)))
    nf.execute("UPDATE customers SET city = 'Mumbai' WHERE customer_id = 1")
    cities = {r[0] for r in nf.execute("SELECT c.city FROM orders o JOIN customers c ON c.customer_id = o.customer_id WHERE c.name = 'Meera'")}
    checks.append(("3NF: one UPDATE moves Meera everywhere, no contradiction possible", cities == {"Mumbai"}))

    grp = {r[0]: r[2] for r in L.run_sql(db, "group")}
    checks.append(("average marks by subject: English 63.4, Maths 65.175, Science 66.175",
                   abs(grp["English"] - 63.4) < 1e-9 and abs(grp["Maths"] - 65.175) < 1e-9 and abs(grp["Science"] - 66.175) < 1e-9))
    checks.append(("worked example: 500 orders, 10 customers: 3000 against 2039 cells = 68.0 percent",
                   round(100 * L.cells_normalised(500, 10) / L.cells_big(500), 1) == 68.0))
    checks.append(("crossover with 20 customers: big table smaller at 34 orders (204 v 205), 3NF smaller at 35 (210 v 209)",
                   L.cells_big(34) == 204 and L.cells_normalised(34, 20) == 205 and L.cells_big(35) == 210 and L.cells_normalised(35, 20) == 209))
    per = [sum(1 for o in L.ORDERS if o[1] == c) for c in L.CUSTOMERS]
    checks.append(("average orders per customer is n / k = 12 / 3 = 4", sum(per) / len(per) == 4.0 == len(L.ORDERS) / len(L.CUSTOMERS)))

    # library design
    lib = L.make_library_db()
    got = L.overdue_sql(lib)
    checks.append(("overdue loans from SQL equal the datetime computation", got == L.overdue_python()))
    checks.append(("two loans are overdue today: Anita 4 days and Dinesh 25 days",
                   [(r[1], r[3]) for r in got] == [("Anita", 4), ("Dinesh", 25)]))
    checks.append(("edge: a loan due today (2026-03-10) is not yet overdue; a day later it is",
                   9 not in [r[0] for r in got] and 9 in [r[0] for r in L.overdue_sql(lib, "2026-03-11")]))
    checks.append(("a loan returned late is not 'currently overdue'", 3 not in [r[0] for r in got]))
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
