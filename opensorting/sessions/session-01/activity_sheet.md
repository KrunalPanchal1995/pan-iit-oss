# Activity sheet: opensorting, Session 1: Sorting cards by hand is an algorithm

Name: ____________________   Date: ____________

**Objectives**

- Describe bubble sort and insertion sort as step-by-step rules anyone could follow.
- Count comparisons and swaps for a small row of cards by hand and in Python.
- Explain why the number of swaps equals the number of pairs in the wrong order.
- Read a bar picture and a graph of steps against how mixed up the row is.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Sort the cards 5 2 4 1 3 with bubble sort and with insertion sort. Count comparisons and swaps for each, and check against the number of pairs in the wrong order.

1. ______________________________  (hint: Pairs in the wrong order: (5,2), (5,4), (5,1), (5,3), (2,1), (4,1), (4...)
2. ______________________________  (hint: Bubble walk 1 compares (5,2) swap, (5,4) swap, (5,1) swap, (5,3) swap:...)
3. ______________________________  (hint: Bubble walk 2 compares (2,4) no swap, (4,1) swap, (4,3) swap: 3 compar...)
4. ______________________________  (hint: Insertion sort: the 2 passes 1 comparison (swap); the 4 needs 2 compar...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do bubble sort and insertion sort need exactly the same number of swaps for the cards 5 2 4 1 3, even though they work differently?

Answer: ______________________________________________


**B. Numerical.** A row of 30 cards is completely reversed (30 down to 1). How many comparisons and swaps does insertion sort need? Check your answer with a formula.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the steps graph for 30 cards, at k = 10 (the first 10 cards reversed), which method needs fewer comparisons and by how many? How many swaps do they need?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a teacher hands you 30 cards that are sorted except that the first 20 are in reverse order. You must pick bubble sort or insertion sort and tell the class how many comparisons to expect. Which do you pick and why? What would you pick if the cards were already sorted?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
