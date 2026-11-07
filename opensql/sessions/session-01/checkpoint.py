"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    conn = L.make_table()
    n = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    checks.append(("the table has 12 rows and 4 columns", n == 12 and len(L.COLUMNS) == 4))
    kept = L.sql_filter(conn, 60, 8)
    checks.append(("marks >= 60 keeps 7 of 12 rows", len(kept) == 7))
    checks.append(("SQL and plain Python give identical rows", kept == L.python_filter(L.ROWS, 60, 8)))
    checks.append(("numpy mask counts the same 7 rows", L.numpy_count(60, 8) == 7))
    names = [r[1] for r in L.sql_filter(conn, 70, 9)]
    checks.append(("worked example: grade >= 9 and marks >= 70 keeps Chitra, Indu, Kavya (3 rows)",
                   names == ["Chitra", "Indu", "Kavya"] and len([r for r in L.ROWS if r[2] >= 9]) == 8))
    checks.append(("a cut-off of 0 keeps every row", len(L.sql_filter(conn, 0)) == 12))
    checks.append(("a cut-off of 101 keeps no rows", L.sql_filter(conn, 101) == []))
    boundary = [r[3] for r in L.sql_filter(conn, 61)]
    checks.append(("the boundary is inclusive: marks 61 is kept by >= 61", 61 in boundary))
    curve = L.count_curve(range(0, 101))
    checks.append(("raising the cut-off never increases the count", all(a >= b for a, b in zip(curve, curve[1:]))))
    checks.append(("grade >= 9 and marks >= 75 keeps exactly 3 rows (the app challenge)", len(L.sql_filter(conn, 75, 9)) == 3))
    checks.append(("grade >= 10 keeps 4 rows", len(L.sql_filter(conn, 0, 10)) == 4))
    checks.append(("grade 10 with marks >= 50 keeps 3 rows, 25 percent of the table", len(L.sql_filter(conn, 50, 10)) == 3 and 100 * 3 / 12 == 25))
    allc = L.count_curve(range(0, 101))
    checks.append(("staircase: 2 rows at cut-off 90, 1 at 95, 0 at 96", allc[90] == 2 and allc[95] == 1 and allc[96] == 0))
    checks.append(("design: cut-offs 77 to 88 keep exactly 3 rows, 76 keeps 4",
                   all(len(L.sql_filter(conn, t)) == 3 for t in range(77, 89)) and len(L.sql_filter(conn, 76)) == 4))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
