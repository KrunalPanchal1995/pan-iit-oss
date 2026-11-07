# Activity sheet: opensorting, Session 2: Five algorithms, one step counter

Name: ____________________   Date: ____________

**Objectives**

- Write bubble, selection, insertion, merge and quick sort in plain Python with a comparison and move counter.
- Test that a sort is correct: ordered output, same items, input unchanged.
- Measure best, average and worst-case inputs and match the counts to n(n-1)/2 and n log2 n.
- Explain why n log2 n beats n(n-1)/2 for large n, and test whether a sort is stable.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A list has n = 1,000,000 items. Compare n(n-1)/2 comparisons with n log2 n comparisons. How many times more is the first? How long does each take at 1 billion steps per second?

1. ______________________________  (hint: n(n-1)/2 = 1,000,000 * 999,999 / 2 = 499,999,500,000 comparisons, abou...)
2. ______________________________  (hint: log2 1,000,000 = 19.93, so n log2 n = 19,931,569 comparisons, about 2....)
3. ______________________________  (hint: Ratio = 499,999,500,000 / 19,931,569 = 25,086, about 25,000 times more...)
4. ______________________________  (hint: At 1e9 steps per second: 499,999,500,000 / 1e9 = 500 seconds, about 8 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Two programs sort the same 1,000,000 records and give identical answers. Why can the more efficient algorithm be hugely faster on this large dataset, even though both are correct?

Answer: ______________________________________________


**B. Numerical.** Predict how many comparisons insertion sort needs on a reversed list of 100 items, and how many item shifts. Then say what the answer would be for a sorted list of 100 items.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the bar figure for 128 items, selection sort has the same height for sorted, random and reversed input, while insertion sort does not. Explain this, and give the numbers for n = 1000 sorted and reversed.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a log file of 1000 lines is nearly sorted by time, with 10 neighbouring lines swapped at random. Choose between insertion sort, merge sort and quick sort (first item as pivot) and justify your choice with step counts.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
