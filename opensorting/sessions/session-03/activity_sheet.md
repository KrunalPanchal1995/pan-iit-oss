# Activity sheet: opensorting, Session 3: Measuring growth, failure cases and choosing a method

Name: ____________________   Date: ____________

**Objectives**

- Fit slopes on log-log axes to measure how the cost of a sort grows with n.
- Explain and demonstrate quicksort's worst case, and compare three pivot rules.
- Build a hybrid merge/insertion sort and find the best cutoff and the cross-over size.
- Compare with Python's built-in sorted(), check memory use, and handle two failure cases.
- Choose and justify a sorting method for a data pattern from measurements.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Quicksort a sorted list of 200 items with three pivot rules: the first item, the median of three, and a random item (seed 0). Compare comparisons and recursion depth with n(n-1)/2.

1. ______________________________  (hint: With the first item as pivot, each partition splits off one item. The ...)
2. ______________________________  (hint: With the median of three, the pivot is the middle value, so the pieces...)
3. ______________________________  (hint: With a random pivot (seed 0) the code counts 1,625 comparisons and a d...)
4. ______________________________  (hint: Compare: 19,900 / 1,534 is about 13 times more comparisons for the fir...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is a sorted list the worst case for quicksort with the first item as pivot, and why does that also create a risk of crashing, not just of being slow?

Answer: ______________________________________________


**B. Numerical.** The comparisons for insertion sort on a reversed list are 4950 for n = 100 and 19,900 for n = 200. Compute the log-log slope between these two points and say what it tells you.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the log-log figure, which lines are parallel, what are their approximate slopes, and what does the gap between the two groups of lines mean?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: 1000 values contain only 10 distinct numbers (many duplicates). Choose among merge sort, quicksort with a first-item pivot and insertion sort, and justify your choice with costs. What does this tell you about the pivot rule?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
