"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # generate, propagate, kill
    kinds = {(a, b): L.stage_kind(a, b) for a in (0, 1) for b in (0, 1)}
    checks.append(("stage kinds: 0,0 kills; 0,1 and 1,0 propagate; 1,1 generates",
                   kinds == {(0, 0): "kill", (0, 1): "propagate", (1, 0): "propagate", (1, 1): "generate"}))
    ok = True
    for a in (0, 1):
        for b in (0, 1):
            for cin in (0, 1):
                g, p = a & b, a ^ b
                ok &= ((g | (p & cin)) == (a + b + cin) // 2) and ((p ^ cin) == (a + b + cin) % 2)
    checks.append(("carry out = g OR (p AND c) and sum = p XOR c match a + b + c on all 8 rows", bool(ok)))
    c = L.Circuit()
    a_in = [c.input(f"a{i}") for i in range(4)]
    b_in = [c.input(f"b{i}") for i in range(4)]
    p_w, g_w = L.generate_propagate(c, a_in, b_in)
    checks.append(("generate and propagate take 2 gates per stage and are ready after 1 gate delay in every stage",
                   c.size() == 8 and all(c.depth[w] == 1 for w in p_w + g_w)))

    # carry equations
    checks.append(("c1 and c2 written out: c1 = g0 + p0 cin; c2 = g1 + p1 g0 + p1 p0 cin",
                   L.carry_equation(0) == "c1 = g0 + p0 cin" and L.carry_equation(1) == "c2 = g1 + p1 g0 + p1 p0 cin"))
    checks.append(("c4 = g3 + p3 g2 + p3 p2 g1 + p3 p2 p1 g0 + p3 p2 p1 p0 cin",
                   L.carry_equation(3) == "c4 = g3 + p3 g2 + p3 p2 g1 + p3 p2 p1 g0 + p3 p2 p1 p0 cin"))
    checks.append(("the equation for the carry out of stage 15 has 17 terms (16 generates and the carry in)",
                   L.carry_equation(15).count(" + ") == 16))

    # every carry, every 6-bit pair: source rule matches the true carry, and exactly one term fires when there is a carry
    n = 6
    good_src, one_term, expect_none = True, True, True
    for a in range(2 ** n):
        for b in range(2 ** n):
            for cin in (0, 1):
                src = L.carry_sources(a, b, n, cin)
                p = [((a >> i) ^ (b >> i)) & 1 for i in range(n)]
                g = [((a >> i) & (b >> i)) & 1 for i in range(n)]
                for i in range(n):
                    low = 2 ** (i + 1)
                    true_carry = ((a % low) + (b % low) + cin) // low
                    good_src &= (src[i] is not None) == bool(true_carry)
                    fired = sum(1 for j in range(i + 1) if g[j] and all(p[k] for k in range(j + 1, i + 1)))
                    fired += int(cin and all(p[k] for k in range(i + 1)))
                    one_term &= fired == true_carry
    checks.append(("all 6-bit pairs and both carry-ins: the carry equations give the true carry out of every stage", bool(good_src)))
    checks.append(("a carry has exactly one source: at most one term of its equation is 1, and none when there is no carry", bool(one_term)))
    checks.append(("worked example 11 + 5: p = 1110, g = 0001, the carry out of stage 3 comes from stage 0, sum 0000 and carry 1",
                   [(11 >> i & 1) ^ (5 >> i & 1) for i in range(4)] == [0, 1, 1, 1]
                   and [(11 >> i & 1) & (5 >> i & 1) for i in range(4)] == [1, 0, 0, 0]
                   and L.carry_sources(11, 5, 4) == [0, 0, 0, 0] and 11 + 5 == 16))
    checks.append(("127 + 1 in 8 bits: the carry from stage 0 passes through to stage 6 and stops (no carry out); 255 + 1 gives a carry out from stage 0",
                   L.carry_sources(127, 1, 8) == [0] * 7 + [None] and L.carry_sources(255, 1, 8) == [0] * 8))
    checks.append(("a carry in of 1 with a = 255, b = 0 travels the whole way: every carry comes from the carry in",
                   L.carry_sources(255, 0, 8, 1) == [-1] * 8))

    # correctness of every design
    allgood = all(L.mismatches(L.build_design(name, w)) == 0 for name in L.DESIGNS for w in range(1, 9))
    checks.append(("ripple, flat and prefix adders match Python for every pair and both carry-ins at every width 1 to 8", bool(allgood)))
    checks.append(("16-bit flat and prefix adders match Python on 20000 random pairs plus corner cases, both carry-ins",
                   L.mismatches(L.build_flat(16)) == 0 and L.mismatches(L.build_prefix(16)) == 0))
    checks.append(("32-bit ripple, flat and prefix adders match Python on 20000 random pairs plus corner cases",
                   all(L.mismatches(L.build_design(name, 32)) == 0 for name in L.DESIGNS)))
    checks.append(("a wrong adder is caught: dropping the carry in makes mismatches non-zero",
                   _broken_is_caught(L)))

    # roadmap checkpoint: carry-out depth at 16 bits
    d16 = {name: L.carry_delay(L.build_design(name, 16)) for name in L.DESIGNS}
    checks.append(("16 bits: ripple carry out needs 33 gate delays, the two lookahead adders at most 12 (flat 9, prefix 11)",
                   d16 == {"ripple": 33, "flat": 9, "prefix": 11} and max(d16["flat"], d16["prefix"]) <= 12))

    # tables of gates and delays
    rows = {(r["design"], r["n"]): r for r in L.design_table((4, 8, 16, 32))}
    checks.append(("ripple: 20, 40, 80, 160 gates and carry delays 9, 17, 33, 65 at 4, 8, 16, 32 bits",
                   [rows[("ripple", n)]["gates"] for n in (4, 8, 16, 32)] == [20, 40, 80, 160]
                   and [rows[("ripple", n)]["carry_depth"] for n in (4, 8, 16, 32)] == [9, 17, 33, 65]))
    checks.append(("flat lookahead: 42, 180, 1000, 6608 gates and carry delays 6, 7, 9, 11",
                   [rows[("flat", n)]["gates"] for n in (4, 8, 16, 32)] == [42, 180, 1000, 6608]
                   and [rows[("flat", n)]["carry_depth"] for n in (4, 8, 16, 32)] == [6, 7, 9, 11]))
    checks.append(("parallel prefix: 29, 77, 197, 485 gates and carry delays 7, 9, 11, 13",
                   [rows[("prefix", n)]["gates"] for n in (4, 8, 16, 32)] == [29, 77, 197, 485]
                   and [rows[("prefix", n)]["carry_depth"] for n in (4, 8, 16, 32)] == [7, 9, 11, 13]))
    checks.append(("prefix gate count = 2n + 2 + 3 x (combines) + n for every width 1 to 32",
                   all(L.prefix_gate_count(n) == L.build_prefix(n)["c"].size() for n in range(1, 33))))
    checks.append(("last sum bit: 8 / 10 / 12 gate delays at 8 / 16 / 32 bits for flat and for prefix at 16 and 32",
                   rows[("flat", 8)]["sum_depth"] == 8 and rows[("flat", 16)]["sum_depth"] == 10
                   and rows[("flat", 32)]["sum_depth"] == 12 and rows[("prefix", 16)]["sum_depth"] == 10
                   and rows[("prefix", 32)]["sum_depth"] == 12))

    # growth with width
    pre = [L.carry_delay(L.build_prefix(w)) for w in (2, 4, 8, 16, 32)]
    checks.append(("prefix: each doubling of the width adds exactly 2 gate delays (5, 7, 9, 11, 13 for 2 to 32 bits)",
                   pre == [5, 7, 9, 11, 13] and all(b - a == 2 for a, b in zip(pre, pre[1:]))))
    flat = [L.carry_delay(L.build_flat(w)) for w in (2, 4, 8, 16, 32)]
    rip = [L.carry_delay(L.build_ripple(w)) for w in (8, 16, 32)]
    checks.append(("flat: 4, 6, 7, 9, 11 gate delays at 2, 4, 8, 16, 32 bits (at most 2 more per doubling); ripple roughly doubles: 17, 33, 65",
                   flat == [4, 6, 7, 9, 11] and all(0 < b - a <= 2 for a, b in zip(flat, flat[1:])) and rip == [17, 33, 65]))
    checks.append(("flat carry delay never goes down as the width grows from 1 to 32",
                   all(L.carry_delay(L.build_flat(w + 1)) >= L.carry_delay(L.build_flat(w)) for w in range(1, 32))))
    checks.append(("flat lookahead is far dearer in gates: 6608 / 1000 > 6 when the width doubles, against 2 for ripple and about 2.5 for prefix",
                   rows[("flat", 32)]["gates"] / rows[("flat", 16)]["gates"] > 6
                   and rows[("ripple", 32)]["gates"] / rows[("ripple", 16)]["gates"] == 2
                   and 2.4 < rows[("prefix", 32)]["gates"] / rows[("prefix", 16)]["gates"] < 2.5))
    bound = math.ceil(math.log2(2 * 16 + 1))
    checks.append(("lower bound: a carry out that depends on 33 inputs needs at least 6 levels of two-input gates, and every design is above it",
                   bound == 6 and all(d >= bound for d in d16.values())))

    # speed and cost at 32 bits
    checks.append(("32 bits: prefix is 5.0 times faster than ripple (65 / 13) for 3.03 times the gates (485 / 160)",
                   65 / 13 == 5.0 and round(485 / 160, 2) == 3.03
                   and rows[("ripple", 32)]["carry_depth"] / rows[("prefix", 32)]["carry_depth"] == 5.0))
    checks.append(("times at 0.5 ns per gate delay: 16 bits ripple 16.5 ns, prefix 5.5 ns",
                   L.time_ns(33) == 16.5 and L.time_ns(11) == 5.5))

    # design choice
    ch = L.choose(32, 15, 1000)
    checks.append(("32 bits, at most 15 gate delays and at most 1000 gates: only the prefix adder qualifies (13 delays, 485 gates)",
                   [r["design"] for r in ch] == ["prefix"] and ch[0]["carry_depth"] == 13 and ch[0]["gates"] == 485))
    checks.append(("with a 10000-gate allowance flat lookahead qualifies too, but prefix is still the cheaper; with at most 10 gate delays none qualifies",
                   [r["design"] for r in L.choose(32, 15, 10000)] == ["prefix", "flat"] and L.choose(32, 10, 10000) == []))
    checks.append(("16 bits, at most 12 gate delays and at most 300 gates: prefix only (flat has 1000 gates)",
                   [r["design"] for r in L.choose(16, 12, 300)] == ["prefix"]))
    checks.append(("widest ripple adder within 15 gate delays is 7 bits; within 20 it is 9 bits (2n + 1 <= budget)",
                   L.widest_within("ripple", 15) == 7 and L.widest_within("ripple", 20) == 9
                   and L.carry_delay(L.build_ripple(8)) == 17))
    checks.append(("a 15-gate-delay budget holds at every width up to 32 bits for both lookahead adders (flat 11, prefix 13)",
                   L.widest_within("flat", 15) == 32 and L.widest_within("prefix", 15) == 32))

    # data-dependent chains
    checks.append(("the worst case needs the full chain: 255 + 1 in 8 bits holds a carry in all 8 stages; 0 + 0 in none",
                   L.longest_carry_run(255, 1, 8) == 8 and L.longest_carry_run(0, 0, 8) == 0))
    m8 = L.mean_longest_run(8)
    m16 = L.mean_longest_run(16)
    checks.append(("a typical sum is much shorter than the worst case: the mean longest carry run is 3.04 over all 8-bit pairs and about 5 for 16-bit pairs",
                   round(m8, 2) == 3.04 and 4.5 < m16 < 6.0))

    # challenge in the app
    ok_w = [w for w in (2, 4, 8, 16, 32)
            if L.carry_delay(L.build_ripple(w)) > 20 and L.carry_delay(L.build_prefix(w)) <= 20]
    checks.append(("app challenge: the smallest width where ripple needs more than 20 gate delays but prefix stays within 20 is 16 bits",
                   ok_w[0] == 16 and L.carry_delay(L.build_ripple(8)) == 17 and L.carry_delay(L.build_ripple(16)) == 33))

    # mini-project
    big = L.build_prefix(32)
    checks.append(("mini-project: the 32-bit prefix adder matches Python on 200000 random pairs plus corner cases, both carry-ins",
                   L.mismatches(big, trials=200000, seed=11) == 0))
    checks.append(("mini-project: 13 gate delays for the carry out is 6.5 ns at 0.5 ns per gate, inside the 7.5 ns budget; ripple needs 32.5 ns",
                   L.time_ns(13) == 6.5 and L.time_ns(13) <= 7.5 and L.time_ns(65) == 32.5))
    return checks


def _broken_is_caught(L):
    """Build a ripple adder whose carry in is tied to 0 and confirm the test notices."""
    c, a, b, cin = L.new_inputs(4)
    zero = c.gate("XOR", cin, cin)           # always 0
    sums, carries, carry = [], [], zero
    for i in range(4):
        s, carry = L.full_adder(c, a[i], b[i], carry)
        sums.append(s)
        carries.append(carry)
    broken = {"c": c, "n": 4, "a": a, "b": b, "cin": cin, "sum": sums, "carry": carries}
    return L.mismatches(broken) > 0


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
