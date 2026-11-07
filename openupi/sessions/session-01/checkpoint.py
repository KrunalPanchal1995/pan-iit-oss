"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    st = L.flow_states(1000, 400, 250)
    checks.append(("there are 7 states: before, then after each of 6 messages", len(st) == 7 and len(L.MESSAGES) == 6))
    checks.append(("worked example: paying 250 ends with payer 750, payee 650, nothing in flight",
                   st[-1] == {"payer": 750, "in_flight": 0, "payee": 650}))
    checks.append(("hand check: after step 3 the 250 is in flight (payer 750, in flight 250, payee 400)",
                   st[3] == {"payer": 750, "in_flight": 250, "payee": 400}))
    checks.append(("before step 3 nothing has moved", st[0] == st[1] == st[2] == {"payer": 1000, "in_flight": 0, "payee": 400}))
    checks.append(("total money is 1400 at every step", all(L.total(s) == 1400 for s in st)))
    checks.append(("conserved() agrees", L.conserved(st)))
    dec = L.flow_states(1000, 400, 1200)
    checks.append(("a payment above the balance is declined: nothing moves, total kept", dec[-1] == dec[0] and L.conserved(dec)))
    exact = L.flow_states(1000, 400, 1000)
    checks.append(("paying exactly the balance works (boundary)", exact[-1]["payer"] == 0 and exact[-1]["payee"] == 1400))
    one_over = L.flow_states(1000, 400, 1001)
    checks.append(("one rupee over the balance is declined", one_over[-1]["payer"] == 1000))
    try:
        L.flow_states(1000, 400, 0)
        zero_rejected = False
    except ValueError:
        zero_rejected = True
    checks.append(("an amount of zero is rejected", zero_rejected))
    checks.append(("every message is between two actors from the cast", all(a in L.ACTORS and b in L.ACTORS for a, b, _ in L.MESSAGES)))
    checks.append(("the apps never hold money: only three number boxes exist", set(st[0]) == {"payer", "in_flight", "payee"}))
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
