"""Checkpoint for Session 5. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # multiplying on paper
    checks.append(("13 x 11: the partial products are 13, 26, 0 and 104 and they add up to 143 = 10001111",
                   L.partial_products(13, 11, 4) == [13, 26, 0, 104] and sum(L.partial_products(13, 11, 4)) == 143
                   and format(143, "08b") == "10001111"))
    A, B = np.meshgrid(np.arange(16), np.arange(16))
    A, B = A.ravel(), B.ravel()
    checks.append(("adding the partial products gives a x b for all 256 pairs of 4-bit numbers",
                   all(L.shift_and_add(int(a), int(b), 4) == int(a) * int(b) for a, b in zip(A, B))))
    checks.append(("each partial product is 0 or a copy of a shifted: row j is a << j when bit j of b is 1",
                   all(L.partial_products(a, b, 4)[j] == (a << j if (b >> j) & 1 else 0)
                       for a in range(16) for b in range(16) for j in range(4))))
    cols = L.column_addition(7, 3, 4)
    checks.append(("worked example 7 x 3 by columns: ones 1, 2, 2, 1, 0 and carries 0, 0, 1, 1, 1 give product bits 1, 0, 1, 0, 1 = 10101 = 21",
                   [c["ones"] for c in cols[:5]] == [1, 2, 2, 1, 0] and [c["carry_in"] for c in cols[:5]] == [0, 0, 1, 1, 1]
                   and sum(c["bit"] << k for k, c in enumerate(cols)) == 21 == 0b10101))
    ok = all(sum(c["bit"] << k for k, c in enumerate(L.column_addition(int(a), int(b), 4))) == int(a) * int(b) for a, b in zip(A, B))
    checks.append(("column addition (write the last bit, carry the rest) gives the product for all 256 pairs", bool(ok)))
    mx = max(c["carry_out"] for a, b in zip(A, B) for c in L.column_addition(int(a), int(b), 4))
    checks.append(("a carry from one column can be bigger than 1: the largest carry in a 4 x 4 product is 3", mx == 3))

    # the gate-level multiplier
    m4 = L.build_multiplier(4)
    checks.append(("4 x 4 multiplier: every one of the 256 input pairs matches Python's a * b (roadmap checkpoint)",
                   L.mismatches(m4) == 0 and np.array_equal(L.multiply(m4, A, B), A * B)))
    checks.append(("the multiplier has 8 product wires, and the largest product 15 x 15 = 225 = 11100001",
                   len(m4["product"]) == 8 and int(L.multiply(m4, 15, 15)) == 225 == 0b11100001))
    allgood = all(L.mismatches(L.build_multiplier(n)) == 0 for n in (2, 3, 5, 6, 7, 8))
    checks.append(("the same design is right for every pair at n = 2, 3, 5, 6, 7 and 8 (8 x 8 is 65536 pairs)", bool(allgood)))
    checks.append(("a 12-bit multiplier matches Python on 20000 random pairs and the extremes",
                   L.mismatches(L.build_multiplier(12)) == 0))
    broken = dict(m4, product=m4["product"][:7] + [m4["product"][6]])
    checks.append(("a wrong multiplier is caught: copying product bit 6 into bit 7 gives mismatches", L.mismatches(broken) > 0))
    checks.append(("worked examples through the gates: 7 x 3 = 21, 13 x 11 = 143, 6 x 5 = 30",
                   int(L.multiply(m4, 7, 3)) == 21 and int(L.multiply(m4, 13, 11)) == 143 and int(L.multiply(m4, 6, 5)) == 30))

    # properties of the circuit
    P = L.multiply(m4, A, B)
    checks.append(("multiplication is commutative in the circuit too: a x b = b x a on all 256 pairs",
                   np.array_equal(P.reshape(16, 16), P.reshape(16, 16).T)))
    checks.append(("multiplying by 1, 2, 4 or 8 is a shift: the circuit gives a, 2a, 4a, 8a for every a",
                   all(np.array_equal(L.multiply(m4, np.arange(16), b), np.arange(16) << sh) for b, sh in ((1, 0), (2, 1), (4, 2), (8, 3)))))
    checks.append(("31 of the 256 products are zero (a = 0 or b = 0) and 6 equal 12",
                   int((P == 0).sum()) == 31 and int((P == 12).sum()) == 6))

    # size
    checks.append(("4 x 4 multiplier: 64 gates = 36 AND + 20 XOR + 8 OR", m4["c"].size() == 64 and m4["c"].mix() == {"AND": 36, "XOR": 20, "OR": 8}))
    checks.append(("the partial products take 16 AND gates, all ready after one gate delay",
                   sum(1 for _, op, ins in m4["c"].gates[:16] if op == "AND") == 16
                   and all(m4["c"].depth[g[0]] == 1 for g in m4["c"].gates[:16])))
    checks.append(("gate count = 6n^2 - 8n for every width n = 2 to 12 (8: 320 gates)",
                   all(L.build_multiplier(n)["c"].size() == L.gate_count_formula(n) for n in range(2, 13))
                   and L.gate_count_formula(8) == 320))
    ok = True
    for n in range(2, 11):
        mix = L.build_multiplier(n)["c"].mix()
        ok &= mix.get("OR", 0) == n * (n - 2) and mix["XOR"] == n + 2 * n * (n - 2) and mix["AND"] == n * n + n + 2 * n * (n - 2)
    checks.append(("n x n multiplier: n^2 + n + 2n(n-2) AND gates, n + 2n(n-2) XOR and n(n-2) OR gates (n half adders, n(n-2) full adders)", bool(ok)))

    # delay
    checks.append(("4 x 4: product bit delays are 1, 2, 4, 8, 11, 13, 15, 16 gate delays",
                   L.product_delays(m4) == [1, 2, 4, 8, 11, 13, 15, 16]))
    checks.append(("slowest product bit: 16 gate delays at 4 bits and 40 at 8 bits",
                   max(L.product_delays(m4)) == 16 and max(L.product_delays(L.build_multiplier(8))) == 40))
    checks.append(("slowest product bit = 6n - 8 gate delays for n = 3 to 16 (n = 2 gives 3)",
                   all(L.design_row(n)["depth"] == 6 * n - 8 for n in range(3, 17)) and L.design_row(2)["depth"] == 3))
    checks.append(("times at 0.5 ns per gate delay: 4 x 4 takes 8 ns, 8 x 8 takes 20 ns", L.time_ns(16) == 8.0 and L.time_ns(40) == 20.0))

    # compared with the adder of Session 3
    g8, d8 = L.ripple_adder_stats(8)
    checks.append(("an 8-bit ripple adder has 40 gates and 17 gate delays; the 8 x 8 multiplier has 8 times the gates (320) and more than twice the delay (40)",
                   (g8, d8) == (40, 17) and 320 // g8 == 8 and 40 / d8 > 2))
    r4, r8 = L.design_row(4), L.design_row(8)
    checks.append(("doubling the width from 4 to 8 multiplies the gates by 5 (64 to 320) and the delay by 2.5 (16 to 40)",
                   r8["gates"] / r4["gates"] == 5.0 and r8["depth"] / r4["depth"] == 2.5))

    # width of the answer
    checks.append(("an n-bit product needs 2n bits: (2^n - 1)^2 < 2^(2n) for n = 2 to 12, and 15 x 15 = 225 needs all 8 bits of the 4 x 4 product",
                   all((2 ** n - 1) ** 2 < 2 ** (2 * n) for n in range(2, 13)) and 225 >= 128
                   and all(L.design_row(n)["bits"] == 2 * n for n in range(2, 11))))
    checks.append(("180 of the 256 products of 4-bit numbers do not fit in 4 bits; keeping only the low 4 bits turns 225 into 1",
                   int((P > 15).sum()) == 180 and int((P <= 15).sum()) == 76 and L.low_half(225, 4) == 1))
    a8, b8 = np.meshgrid(np.arange(256), np.arange(256))
    too_big = int(((a8 * b8) > 255).sum())
    checks.append(("8 x 8: 63568 of the 65536 products (97.0 %) do not fit in 8 bits", too_big == 63568 and round(100 * too_big / 65536, 1) == 97.0))

    # design budgets
    checks.append(("widest multiplier within 20 gate delays (10 ns) is 4 bits (16 gate delays; 5 bits needs 22); within 40 gate delays (20 ns) it is 8 bits (9 bits needs 46)",
                   L.widest_within(20) == 4 and L.design_row(5)["depth"] == 22 and L.widest_within(40) == 8
                   and L.design_row(9)["depth"] == 46))

    # mini-project: 8 x 8 multiplier
    m8 = L.build_multiplier(8)
    p8 = L.multiply(m8, a8.ravel(), b8.ravel())
    checks.append(("mini-project: the 8 x 8 multiplier matches Python for all 65536 pairs and has 320 gates, 16 product bits and a slowest bit after 40 gate delays (20 ns)",
                   np.array_equal(p8, (a8 * b8).ravel()) and m8["c"].size() == 320 and len(m8["product"]) == 16
                   and max(L.product_delays(m8)) == 40 and L.time_ns(40) == 20.0))
    checks.append(("mini-project: the largest 8 x 8 product is 255 x 255 = 65025 = 1111111000000001, which needs all 16 bits",
                   int(p8.max()) == 65025 == 0b1111111000000001))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson5", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
