"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # half adder and full adder, every row
    c = L.Circuit()
    a, b, ci = c.input("a"), c.input("b"), c.input("ci")
    hs, hc = L.half_adder(c, a, b)
    fs, fc = L.full_adder(c, a, b, ci)
    rows = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)])
    w = c.run({"a": rows[:, 0], "b": rows[:, 1], "ci": rows[:, 2]})
    checks.append(("half adder: sum = XOR, carry = AND on all 4 input pairs",
                   np.array_equal(2 * w[hc] + w[hs], rows[:, 0] + rows[:, 1])))
    checks.append(("full adder: 2*carry + sum = a + b + cin on all 8 rows",
                   np.array_equal(2 * w[fc] + w[fs], rows.sum(axis=1))))

    # 4-bit ripple adder, every pair and both carry-ins
    ad = L.build_adder(4)
    A, B = np.meshgrid(np.arange(16), np.arange(16))
    A, B = A.ravel(), B.ravel()
    good = True
    for cin in (0, 1):
        s, co = L.add_bits(ad, A, B, cin)
        total = A + B + cin
        good &= np.array_equal(s, total % 16) and np.array_equal(co, total // 16)
    checks.append(("4-bit ripple adder matches Python for all 256 pairs, carry in 0 and 1", bool(good)))
    checks.append(("a 4-bit adder uses 20 gates (5 per full adder), an 8-bit adder 40",
                   ad["c"].size() == 20 and L.build_adder(8)["c"].size() == 40))

    # two's complement
    checks.append(("two's complement: 4-bit patterns 8 -> -8, 15 -> -1, 7 -> 7, and -3 is 1101",
                   int(L.from_twos(8, 4)) == -8 and int(L.from_twos(15, 4)) == -1 and int(L.from_twos(7, 4)) == 7
                   and L.to_twos(-3, 4) == 13 and format(L.to_twos(-3, 4), "04b") == "1101"))
    flip_plus_one = [(~u + 1) & 15 for u in range(16)]
    checks.append(("negating = flip every bit and add 1, for all 16 patterns (except -8 which maps to itself)",
                   all(int(L.from_twos(flip_plus_one[u], 4)) == -int(L.from_twos(u, 4)) for u in range(16) if u != 8)
                   and flip_plus_one[8] == 8))
    # worked example 6 - 3
    circ = L.build_add_sub(4)
    r, o = L.add_sub(circ, 6, 3, 1)
    checks.append(("worked example: 6 - 3 = 0110 + 1100 + 1 = 10011, keep 4 bits 0011 = 3, no overflow",
                   0b0110 + 0b1100 + 1 == 0b10011 and int(r) == 3 and int(o) == 0 and (0b10011 & 15) == 3))

    # exhaustive add/subtract with overflow vs Python
    S = np.arange(-8, 8)
    SA, SB = [x.ravel() for x in np.meshgrid(S, S)]
    ok = True
    for sub in (0, 1):
        res, ovf = L.add_sub(circ, SA, SB, sub)
        true = SA - SB if sub else SA + SB
        wrapped = ((true + 8) % 16) - 8
        ok &= np.array_equal(res, wrapped) and np.array_equal(ovf, (true != wrapped).astype(int))
        ok &= all(L.python_reference(int(x), int(y), sub, 4) == (int(rr), int(oo)) for x, y, rr, oo in zip(SA, SB, res, ovf))
    checks.append(("4-bit adder-subtractor: result and overflow flag match Python for all 256 signed pairs, add and subtract", bool(ok)))
    r1, o1 = L.add_sub(circ, 7, 1, 0)
    r2, o2 = L.add_sub(circ, -8, 1, 1)
    checks.append(("failure case: 7 + 1 wraps to -8 with overflow flag 1; -8 - 1 wraps to 7 with flag 1",
                   int(r1) == -8 and int(o1) == 1 and int(r2) == 7 and int(o2) == 1))
    r3, o3 = L.add_sub(circ, -8, -8, 0)
    r4, o4 = L.add_sub(circ, 5, -3, 0)
    checks.append(("edge: -8 + -8 overflows to 0; 5 + -3 = 2 does not overflow",
                   int(r3) == 0 and int(o3) == 1 and int(r4) == 2 and int(o4) == 0))
    checks.append(("64 of the 256 signed pairs overflow when adding in 4 bits",
                   int(L.add_sub(circ, SA, SB, 0)[1].sum()) == 64))

    # gate delays
    d = {n: L.carry_delay(L.build_adder(n)) for n in (4, 8, 16)}
    checks.append(("carry-out delay is 9 gate delays for 4 bits, 17 for 8 bits, 33 for 16 bits", d == {4: 9, 8: 17, 16: 33}))
    checks.append(("carry-out delay = 2n + 1 for every width 1 to 32, and the last sum bit takes 2n for n >= 2",
                   all(L.carry_delay(L.build_adder(n)) == 2 * n + 1 for n in range(1, 33))
                   and all(L.sum_delay(L.build_adder(n)) == 2 * n for n in range(2, 33))))
    checks.append(("each extra bit adds exactly 2 gate delays", all(
        L.carry_delay(L.build_adder(n + 1)) - L.carry_delay(L.build_adder(n)) == 2 for n in range(1, 20))))
    checks.append(("data-dependent chain: 127 + 1 passes the carry through 7 stages, 255 + 1 through 8",
                   L.longest_carry_run(127, 1, 8) == 7 and L.longest_carry_run(255, 1, 8) == 8
                   and L.longest_carry_run(0, 0, 8) == 0))

    # ALU, every input pair and every op
    alu = L.build_alu(4)
    UA, UB = np.meshgrid(np.arange(16), np.arange(16))
    UA, UB = UA.ravel(), UB.ravel()
    ok = True
    for op in range(4):
        res, ovf = L.run_alu(alu, UA, UB, op)
        for x, y, rr, oo in zip(UA, UB, res, ovf):
            x, y = int(x), int(y)
            sx, sy = x - 16 if x >= 8 else x, y - 16 if y >= 8 else y
            if op == 0:
                t = sx + sy
                exp = (t % 16, int(not -8 <= t <= 7))
            elif op == 1:
                t = sx - sy
                exp = (t % 16, int(not -8 <= t <= 7))
            elif op == 2:
                exp = (x & y, 0)
            else:
                exp = (x | y, 0)
            ok &= (int(rr), int(oo)) == exp
    checks.append(("4-bit ALU (add, subtract, AND, OR) matches Python for all 256 pairs x 4 operations", bool(ok)))
    checks.append(("the ALU slice uses 59 gates", alu["c"].size() == 59))
    r, o = L.run_alu(alu, 7, 1, 0)
    checks.append(("ALU adds 7 + 1 to pattern 1000 (= -8) and raises overflow", int(r) == 8 and int(o) == 1))

    # seven-segment
    checks.append(("seven-segment: digit 8 lights all 7 segments, digit 1 lights 2, digits 0 to 9 light 49 in total",
                   sum(L.seven_segment(8)) == 7 and sum(L.seven_segment(1)) == 2
                   and sum(sum(L.seven_segment(k)) for k in range(10)) == 49))

    # mini-project: 8-bit adder-subtractor, every pair
    c8 = L.build_add_sub(8)
    S8 = np.arange(-128, 128)
    A8, B8 = [x.ravel() for x in np.meshgrid(S8, S8)]
    ok, counts = True, []
    for sub in (0, 1):
        res, ovf = L.add_sub(c8, A8, B8, sub)
        true = A8 - B8 if sub else A8 + B8
        wrapped = ((true + 128) % 256) - 128
        ok &= np.array_equal(res, wrapped) and np.array_equal(ovf, (true != wrapped).astype(int))
        counts.append(int(ovf.sum()))
    checks.append(("mini-project: 8-bit adder-subtractor matches Python for all 65536 pairs, add and subtract", bool(ok)))
    checks.append(("mini-project: 16384 pairs overflow for add and 16384 for subtract", counts == [16384, 16384]))
    checks.append(("mini-project: the 8-bit adder-subtractor has 49 gates and its overflow flag is ready after 19 gate delays",
                   c8["c"].size() == 49 and c8["c"].depth[c8["overflow"]] == 19))
    widest = max(n for n in range(2, 40)
                 if L.build_add_sub(n)["c"].depth[L.build_add_sub(n)["overflow"]] * 0.5 <= 10.0)
    checks.append(("mini-project: with 0.5 ns per gate and a 10 ns budget the widest adder-subtractor is 8 bits (19 x 0.5 = 9.5 ns; 9 bits needs 10.5 ns)",
                   widest == 8 and 19 * 0.5 == 9.5 and L.build_add_sub(9)["c"].depth[L.build_add_sub(9)["overflow"]] == 21))
    # numbers quoted in the text
    checks.append(("4 bits cover -8 to 7 and 8 bits cover -128 to 127",
                   int(L.from_twos(np.arange(16), 4).min()) == -8 and int(L.from_twos(np.arange(16), 4).max()) == 7
                   and int(L.from_twos(np.arange(256), 8).min()) == -128 and int(L.from_twos(np.arange(256), 8).max()) == 127))
    ad4 = L.build_add_sub(4)
    w = ad4["c"].run({**{f"a{i}": np.array([(7 >> i) & 1]) for i in range(4)}, **{f"b{i}": np.array([(1 >> i) & 1]) for i in range(4)}, "sub": np.array([0])})
    checks.append(("7 + 1: carry into the top bit is 1 and carry out of it is 0, so they differ",
                   int(w[ad4["carry"][2]][0]) == 1 and int(w[ad4["carry"][3]][0]) == 0))
    w2 = ad4["c"].run({**{f"a{i}": np.array([(15 >> i) & 1]) for i in range(4)}, **{f"b{i}": np.array([(1 >> i) & 1]) for i in range(4)}, "sub": np.array([0])})
    checks.append(("-1 + 1 (1111 + 0001) has a carry out of the top bit but no overflow",
                   int(w2[ad4["carry"][3]][0]) == 1 and int(w2[ad4["overflow"]][0]) == 0))
    r5, o5 = L.add_sub(ad4, 5, 7, 1)
    checks.append(("5 - 7: 0101 + 1000 + 1 = 1110 = 14, read as -2, no overflow",
                   0b0101 + 0b1000 + 1 == 14 == 0b1110 and int(r5) == -2 and int(o5) == 0))
    checks.append(("carry delay at 12 bits is 25; widest ripple adder with carry out within 20 ns at 0.5 ns per gate is 19 bits",
                   L.carry_delay(L.build_adder(12)) == 25
                   and max(n for n in range(1, 60) if L.carry_delay(L.build_adder(n)) * 0.5 <= 20) == 19
                   and L.carry_delay(L.build_adder(19)) == 39 and L.carry_delay(L.build_adder(20)) == 41))
    r6, o6 = L.add_sub(c8, 100, 100, 0)
    r7, o7 = L.add_sub(c8, 127, 1, 0)
    r8, o8 = L.add_sub(c8, 45, 19, 0)
    r9, o9 = L.add_sub(c8, -1, 1, 0)
    checks.append(("8 bits: 100 + 100 wraps to -56 (overflow); 127 + 1 = -128 (overflow); 45 + 19 = 64 and -1 + 1 = 0 (no overflow)",
                   (int(r6), int(o6)) == (-56, 1) and (int(r7), int(o7)) == (-128, 1)
                   and (int(r8), int(o8)) == (64, 0) and (int(r9), int(o9)) == (0, 0)))
    checks.append(("carry chain lengths: 45 + 19 passes a carry through 6 stages, 127 + 1 through 7, -1 + 1 (255 + 1) through 8",
                   L.longest_carry_run(45, 19, 8) == 6 and L.longest_carry_run(127, 1, 8) == 7 and L.longest_carry_run(255, 1, 8) == 8))
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
