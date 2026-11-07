"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("H2O has 2 H and 1 O", L.parse_formula("H2O") == {"H": 2, "O": 1}))
    checks.append(("Ca(OH)2 has 1 Ca, 2 O and 2 H", L.parse_formula("Ca(OH)2") == {"Ca": 1, "O": 2, "H": 2}))
    checks.append(("C6H12O6 has 6 C, 12 H and 6 O", L.parse_formula("C6H12O6") == {"C": 6, "H": 12, "O": 6}))
    r, p = [(2, "H2"), (1, "O2")], [(2, "H2O")]
    checks.append(("worked example: 2 H2 + O2 -> 2 H2O has 4 H and 2 O on each side",
                   L.side_counts(r) == {"H": 4, "O": 2} == L.side_counts(p) and L.is_balanced(r, p)))
    checks.append(("H2 + O2 -> H2O is not balanced: 2 O on the left, 1 on the right",
                   L.imbalance([(1, "H2"), (1, "O2")], [(1, "H2O")]) == {"H": 0, "O": 1}))
    sol = L.balance_search(["H2", "O2"], ["H2O"])
    checks.append(("search finds 2, 1 -> 2", sol == ((2, 1), (2,))))
    sol = L.balance_search(["CH4", "O2"], ["CO2", "H2O"])
    checks.append(("search balances methane combustion as 1, 2 -> 1, 2", sol == ((1, 2), (1, 2))))
    checks.append(("doubling every coefficient keeps the equation balanced (hand check)",
                   L.is_balanced(list(zip(L.scale((2, 1), 2), ["H2", "O2"])), list(zip(L.scale((2,), 2), ["H2O"])))))
    checks.append(("an impossible equation (H2 -> O2) has no solution", L.balance_search(["H2"], ["O2"]) is None))
    bad = 0
    for f in ("", "H2O)", "(H2O", "2H", "h2o", "H$"):
        try:
            L.parse_formula(f)
        except ValueError:
            bad += 1
    checks.append(("malformed formulas raise ValueError", bad == 6))
    checks.append(("Fe2(SO4)3 has 2 Fe, 3 S, 12 O", L.parse_formula("Fe2(SO4)3") == {"Fe": 2, "S": 3, "O": 12}))
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
