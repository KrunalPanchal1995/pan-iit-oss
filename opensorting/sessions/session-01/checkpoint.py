"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    cards = [5, 2, 4, 1, 3]
    b = L.bubble_sort(cards)
    i = L.insertion_sort(cards)
    checks.append(("worked example: bubble sort of 5 2 4 1 3 gives 1 2 3 4 5 with 10 comparisons and 7 swaps",
                   b == ([1, 2, 3, 4, 5], 10, 7)))
    checks.append(("worked example: insertion sort of 5 2 4 1 3 takes 9 comparisons and 7 swaps",
                   i == ([1, 2, 3, 4, 5], 9, 7)))
    checks.append(("5 2 4 1 3 has 7 pairs in the wrong order, equal to the swaps", L.inversions(cards) == 7))
    checks.append(("the input list is not changed", cards == [5, 2, 4, 1, 3]))

    rev = list(range(30, 0, -1))
    checks.append(("reversed 30 cards: 435 = 30*29/2 comparisons and swaps for both methods",
                   L.bubble_sort(rev)[1:] == (435, 435) and L.insertion_sort(rev)[1:] == (435, 435)))
    srt = list(range(1, 31))
    checks.append(("sorted 30 cards: 29 comparisons and 0 swaps for both methods",
                   L.bubble_sort(srt)[1:] == (29, 0) and L.insertion_sort(srt)[1:] == (29, 0)))
    checks.append(("empty list and one card need 0 steps",
                   L.bubble_sort([]) == ([], 0, 0) and L.insertion_sort([7]) == ([7], 0, 0)))

    row = L.prefix_reversed(30, 10)
    checks.append(("30 cards with the first 10 reversed: 45 inversions, bubble 245 comparisons, insertion 65",
                   L.inversions(row) == 45 and L.bubble_sort(row)[1] == 245 and L.insertion_sort(row)[1] == 65))
    row20 = L.prefix_reversed(30, 20)
    checks.append(("first 20 reversed: 190 swaps and 20*19/2 = 190 inversions",
                   L.bubble_sort(row20)[2] == 190 == L.inversions(row20) == 20 * 19 // 2))
    checks.append(("first 20 of 30 reversed: bubble 390 comparisons, insertion 200",
                   L.bubble_sort(row20)[1] == 390 and L.insertion_sort(row20)[1] == 200))
    hand = [7, 3, 11, 1, 9, 5, 12, 2, 10, 4, 8, 6]
    checks.append(("12-card hand: 32 inversions, bubble 56 comparisons, insertion 41 comparisons, both 32 swaps",
                   L.inversions(hand) == 32 and L.bubble_sort(hand) == (sorted(hand), 56, 32)
                   and L.insertion_sort(hand) == (sorted(hand), 41, 32)))
    checks.append(("prefix_reversed(5, 3) is 3 2 1 4 5", L.prefix_reversed(5, 3) == [3, 2, 1, 4, 5]))
    checks.append(("prefix_reversed with k = 0 or 1 changes nothing",
                   L.prefix_reversed(6, 0) == L.prefix_reversed(6, 1) == [1, 2, 3, 4, 5, 6]))
    checks.append(("is_sorted works", L.is_sorted([1, 2, 2, 3]) and not L.is_sorted([2, 1])))
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
