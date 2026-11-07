# Activity sheet: opensql, Session 2: Ask precise questions, and store every fact once

Name: ____________________   Date: ____________

**Objectives**

- Use ORDER BY, LIMIT, COUNT, SUM, AVG, MIN, MAX, GROUP BY and HAVING, and check each against plain Python.
- Explain primary keys and foreign keys, and see the database reject a broken reference.
- Show the update, insert and delete anomalies of one big table.
- Split a table into third normal form and count what is stored.
- Design the tables of a library and write the overdue-loans query.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A six-row table has marks: Maths 70, 90, 80 and Science 60, 50, 85. Use GROUP BY subject to find each subject's sum and average, and use HAVING AVG(marks) > 70 to keep the strong subjects.

1. ______________________________  (hint: Maths group: 70 + 90 + 80 = 240; COUNT = 3; AVG = 240 / 3 = 80....)
2. ______________________________  (hint: Science group: 60 + 50 + 85 = 195; COUNT = 3; AVG = 195 / 3 = 65....)
3. ______________________________  (hint: HAVING AVG > 70 keeps groups whose average is above 70: Maths (80) sta...)
4. ______________________________  (hint: HAVING is strict, so AVG > 80 would keep nothing, and AVG > 60 would k...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can you not write WHERE AVG(marks) >= 75 to find students whose average is at least 75? What do you write instead?

Answer: ______________________________________________


**B. Numerical.** A shop has 500 orders and 10 customers and sells 3 items. How many cells does the big table store, how many do the three tables store, and what percentage is that?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the line chart with k = 20 customers and 3 items, between which two numbers of orders do the lines cross? What does that tell a designer?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a library lends books to members. Design the tables with keys, and write the query that lists loans that are overdue today (still out and due before today), with the member name, the title and the days late.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
