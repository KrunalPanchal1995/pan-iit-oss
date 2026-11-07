"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # converters against Python's own
    ok_bin = all(L.to_base(n, 2) == bin(n)[2:] and L.from_base(bin(n)[2:], 2) == n for n in range(5000))
    ok_hex = all(L.to_base(n, 16) == format(n, "X") and L.from_base(format(n, "x"), 16) == n for n in range(5000))
    ok_dec = all(L.to_base(n, 10) == str(n) for n in range(5000))
    checks.append(("converters agree with Python for every number 0 to 4999 (binary, decimal, hex)", ok_bin and ok_hex and ok_dec))
    checks.append(("round trip in every base 2 to 16 for 0 to 600",
                   all(L.from_base(L.to_base(n, b), b) == n for b in range(2, 17) for n in range(601))))
    checks.append(("worked example: 183 is 10110111 in binary and B7 in hex, and 128+32+16+4+2+1 = 183",
                   L.to_base(183, 2) == "10110111" and L.to_base(183, 16) == "B7"
                   and L.from_base("B7", 16) == 183 and 128 + 32 + 16 + 4 + 2 + 1 == 183
                   and L.bin_to_hex("10110111") == "B7" and 11 * 16 + 7 == 183))
    checks.append(("edge: zero is '0'; 4095 is FFF; digit 2 is not allowed in binary",
                   L.to_base(0, 2) == "0" and L.to_base(4095, 16) == "FFF" and _raises(L.from_base, "102", 2)))

    # gates and truth tables
    tt = {name: L.truth_table(g)[:, 2].tolist() for name, g in
          (("AND", L.AND), ("OR", L.OR), ("XOR", L.XOR), ("NAND", L.NAND))}
    checks.append(("truth tables of AND, OR, XOR, NAND (rows 00, 01, 10, 11)",
                   tt == {"AND": [0, 0, 0, 1], "OR": [0, 1, 1, 1], "XOR": [0, 1, 1, 0], "NAND": [1, 1, 1, 0]}))
    checks.append(("NOT flips 0 and 1", L.NOT(0) == 1 and L.NOT(1) == 0))

    # De Morgan, exhaustive
    checks.append(("De Morgan holds on all 4 rows (2 inputs) and all 8 rows (3 inputs)",
                   L.de_morgan_holds(2) and L.de_morgan_holds(3) and len(L.all_inputs(2)) == 4 and len(L.all_inputs(3)) == 8))
    # a law that is NOT true must be caught: NOT(a AND b) is not NOT a AND NOT b
    X = L.all_inputs(2).T
    wrong = np.array_equal(L.NOT(L.AND(X[0], X[1])), L.AND(L.NOT(X[0]), L.NOT(X[1])))
    checks.append(("a wrong law is detected: NOT(a AND b) differs from (NOT a) AND (NOT b)", not wrong))

    # NAND universality and gate counts
    X2 = L.all_inputs(2)
    a, b = X2[:, 0], X2[:, 1]
    checks.append(("NOT, AND, OR, XOR built only from NAND match the real gates on every row",
                   np.array_equal(L.not_n(a), L.NOT(a)) and np.array_equal(L.and_n(a, b), L.AND(a, b))
                   and np.array_equal(L.or_n(a, b), L.OR(a, b)) and np.array_equal(L.xor_n(a, b), L.XOR(a, b))))
    used = []
    for fn, args in ((L.not_n, (a,)), (L.and_n, (a, b)), (L.or_n, (a, b)), (L.xor_n, (a, b))):
        g, counter = L.counting_nand()
        fn(*args, nand=g)
        used.append(counter[0])
    checks.append(("NAND gates needed: NOT 1, AND 2, OR 3, XOR 4", used == [1, 2, 3, 4]))

    # design problems
    X3 = L.all_inputs(3)
    maj = L.majority_outputs()
    checks.append(("majority gate has minterm rows 3, 5, 6, 7", L.minterms(maj) == [3, 5, 6, 7]))
    checks.append(("majority: sum of products matches the table on all 8 rows",
                   L.sop_eval(L.minterms(maj), 3, X3).tolist() == maj))
    checks.append(("majority: short form a.b + a.c + b.c matches on all 8 rows",
                   L.majority_short(X3[:, 0], X3[:, 1], X3[:, 2]).tolist() == maj))
    X4 = L.all_inputs(4)
    gt = L.greater_outputs()
    checks.append(("comparator A > B has 6 minterms of 16 (pairs with A greater: 3+2+1)",
                   len(L.minterms(gt)) == 6 and 3 + 2 + 1 == 6))
    checks.append(("comparator: sum of products matches A > B on all 16 rows",
                   L.sop_eval(L.minterms(gt), 4, X4).tolist() == gt))
    checks.append(("comparator: short form matches A > B on all 16 rows",
                   L.greater_short(*X4.T).tolist() == gt))
    # equality comparator (assessment D): 4 minterms, equals NOT(XOR) on each bit pair
    eq = [1 if 2 * r[0] + r[1] == 2 * r[2] + r[3] else 0 for r in X4]
    xnor_form = L.AND(L.NOT(L.XOR(X4[:, 0], X4[:, 2])), L.NOT(L.XOR(X4[:, 1], X4[:, 3])))
    checks.append(("equality comparator has 4 minterms and equals (a1 XNOR b1) AND (a0 XNOR b0)",
                   len(L.minterms(eq)) == 4 and xnor_form.tolist() == eq))
    checks.append(("A5 is 165 and 10100101; 100 is 1100100 and 64 in hex; one hex digit is four bits",
                   L.from_base("A5", 16) == 165 and L.to_base(165, 2) == "10100101" and 10 * 16 + 5 == 165
                   and L.to_base(100, 2) == "1100100" and L.to_base(100, 16) == "64" and 6 * 16 + 4 == 100
                   and L.bin_to_hex("1111") == "F" and 128 + 32 + 4 + 1 == 165))
    grid = np.array(L.greater_outputs()).reshape(4, 4)          # grid[A, B]
    checks.append(("comparator figure: the six ones lie strictly below the diagonal, the diagonal is 0",
                   np.array_equal(grid, np.tril(np.ones((4, 4), dtype=int), -1))))
    checks.append(("equality rows are 0000, 0101, 1010, 1111",
                   [format(i, "04b") for i in L.minterms(eq)] == ["0000", "0101", "1010", "1111"]))
    return checks


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


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
