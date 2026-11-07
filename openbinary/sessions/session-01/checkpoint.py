"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("place values of 4 switches are 8, 4, 2, 1", L.place_values(4) == [8, 4, 2, 1]))
    checks.append(("worked example: 13 is switches 1101 = 8 + 4 + 0 + 1",
                   L.to_bits(13) == [1, 1, 0, 1] and L.from_bits([1, 1, 0, 1]) == 13 and 8 + 4 + 0 + 1 == 13))
    checks.append(("every number 0 to 15 survives to_bits then from_bits",
                   all(L.from_bits(L.to_bits(n)) == n for n in range(16))))
    checks.append(("all 16 patterns of 4 switches are different",
                   len({tuple(L.to_bits(n)) for n in range(16)}) == 16 and L.count_patterns(4) == 16))
    checks.append(("4 switches count up to 15, 8 switches up to 255", L.largest(4) == 15 and L.largest(8) == 255))
    checks.append(("each extra switch doubles the patterns (10 switches: 1024)",
                   L.count_patterns(5) == 2 * L.count_patterns(4) and L.count_patterns(10) == 1024))
    checks.append(("7 is 0111 and 8 is 1000: counting 7 to 8 flips all four switches",
                   L.to_bits(7) == [0, 1, 1, 1] and L.to_bits(8) == [1, 0, 0, 0]
                   and sum(a != b for a, b in zip(L.to_bits(7), L.to_bits(8))) == 4))
    checks.append(("the lamp string for 13 is ##.# (lamps on, on, off, on)", L.lamps(13) == "##.#"))
    checks.append(("exactly 6 of the numbers 0 to 15 have two lamps on (4 choose 2)",
                   sum(L.lamps_on(n) == 2 for n in range(16)) == 6))
    checks.append(("edge: 15 + 1 wraps to 0 on 4 switches", L.add_one(15) == 0 and L.add_one(7) == 8))
    try:
        L.to_bits(16)
        too_big = False
    except ValueError:
        too_big = True
    checks.append(("edge: 16 does not fit in 4 switches", too_big))
    checks.append(("counting table has 16 rows from 0000 to 1111",
                   len(L.count_table()) == 16 and L.count_table()[0][1] == "...." and L.count_table()[15][1] == "####"))
    checks.append(("worked example part 2: 12 is 1100 (8 + 4), and 1011 reads as 11",
                   L.to_bits(12) == [1, 1, 0, 0] and 8 + 4 == 12 and L.from_bits([1, 0, 1, 1]) == 11))
    checks.append(("5 switches make 32 patterns", L.count_patterns(5) == 32))
    two_lamps = [n for n in range(16) if L.lamps_on(n) == 2]
    checks.append(("numbers with two lamps on are 3, 5, 6, 9, 10, 12; lamp counts 0 to 4 occur 1, 4, 6, 4, 1 times",
                   two_lamps == [3, 5, 6, 9, 10, 12]
                   and [sum(L.lamps_on(n) == k for n in range(16)) for k in range(5)] == [1, 4, 6, 4, 1]
                   and max(range(16), key=L.lamps_on) == 15))
    checks.append(("design: 100 seats need 7 lamps (6 give 64 patterns, 7 give 128)",
                   L.count_patterns(6) == 64 < 100 <= L.count_patterns(7) == 128))
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
