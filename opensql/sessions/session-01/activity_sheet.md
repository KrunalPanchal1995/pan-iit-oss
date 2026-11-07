# Activity sheet: opensql, Session 1: A table is a grid, a query asks it a question

Name: ____________________   Date: ____________

**Objectives**

- Describe a table as rows (records) and columns (fields).
- Read and write a SELECT ... FROM ... WHERE query.
- Predict how many rows a filter keeps, and check it against plain Python.
- Read a graph of rows kept against the cut-off.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Using the 12-row table, which students are in grade 9 or above and scored at least 70? How many rows are in grade 9 or above to begin with?

1. ______________________________  (hint: Rows with grade >= 9: Chitra (9), Dev (9), Farid (10), Gita (10), Hari...)
2. ______________________________  (hint: Of those, marks >= 70: Chitra 88 yes, Dev 61 no, Farid 55 no, Gita 67 ...)
3. ______________________________  (hint: Three rows pass: Chitra, Indu, Kavya....)
4. ______________________________  (hint: SQL: SELECT name FROM students WHERE grade >= 9 AND marks >= 70 ORDER ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Does running a SELECT query change the table? Why does the order of rows in an answer need an ORDER BY?

Answer: ______________________________________________


**B. Numerical.** How many rows have grade 10 and marks of at least 50? What percentage of the whole table is that?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the staircase graph for all grades, how many rows are kept at a cut-off of 90, and what is the first whole-number cut-off that keeps 0 rows?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a scholarship interview should include exactly the top 3 students out of 12 (25 percent) by marks. Choose a cut-off for 'marks >= cut-off'. Which cut-offs work, and which one would you pick?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
