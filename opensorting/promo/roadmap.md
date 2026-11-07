# Roadmap: the path to the opensorting Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Run-detecting merge sort

**You will learn:** How Timsort-style sorts find ascending runs and merge only the runs.

**You will build:** A natural merge sort that splits the list into runs and merges them, with the same counters.

**Checkpoint (not met by the shipped code):** Fewer than 5,000 comparisons on 2000 items with 10 far swaps (the best shipped method needs 13,565).

**Difficulty:** intermediate

## Session 5: Three-way quicksort

**You will learn:** Partitioning into smaller, equal and larger items so duplicates leave the problem at once.

**You will build:** A quicksort variant with a three-way partition and the same counters.

**Checkpoint (not met by the shipped code):** Fewer than 10,000 comparisons on 1000 items with 10 distinct values (the shipped first-pivot quick sort needs 54,365).

**Difficulty:** intermediate

## Session 6: A quicksort with no bad input

**You will learn:** Introsort: switch to heap sort when the recursion gets too deep, so the worst case is n log n.

**You will build:** A sort that never exceeds twice n log2 n comparisons on any of the five patterns.

**Checkpoint (not met by the shipped code):** At most 2 n log2 n = about 19,932 comparisons on every pattern for n = 1000 (the shipped first-pivot quick sort reaches 499,500).

**Difficulty:** advanced

## Session 7: Beat the comparison limit

**You will learn:** Counting sort and radix sort, which sort integers without comparing items.

**You will build:** A counting sort for integers in a small range, measured with the same step counter.

**Checkpoint (not met by the shipped code):** Fewer than 3 steps per item for 100,000 integers between 0 and 999, a cost no comparison sort in the shipped code can reach.

**Difficulty:** advanced

## Session 8: The live race

**You will learn:** Recording an algorithm as a sequence of events so it can be replayed side by side.

**You will build:** An animation that replays several sorts on the same list with live counters.

**Checkpoint (not met by the shipped code):** The final counters in the animation equal the counts from the lesson functions for the same list.

**Difficulty:** intermediate

## The final step

Combine the milestones: a race of five algorithms on the same list with live counters, a growth plot and a rule for choosing the method. If your result looks like the Target animation, open a pull request and tell us how you did it.
