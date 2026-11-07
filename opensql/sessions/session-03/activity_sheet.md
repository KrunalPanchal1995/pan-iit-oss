# Activity sheet: opensql, Session 3: How fast, how safe, how right

Name: ____________________   Date: ____________

**Objectives**

- Write inner and left JOINs and check them against nested loops.
- Read EXPLAIN QUERY PLAN and measure a scan against an index lookup on 200,000 rows.
- Compute B-tree depth for a given number of rows and keys per node.
- Use a transaction so a failed transfer changes nothing.
- Show why string-built queries are unsafe and fix them with parameters.
- Explain two failure cases: a missing index on a join column, and a foreign key violation.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A table has 1,000,000 rows and each B-tree node holds 100 keys. How many levels does an index lookup need, how many comparisons does binary search need, and how many rows might a scan read?

1. ______________________________  (hint: Levels: find the smallest d with 100^d >= 1,000,000. 100^1 = 100, 100^...)
2. ______________________________  (hint: Binary search halves the range each time: 2^19 = 524,288 < 1,000,000 <...)
3. ______________________________  (hint: A scan reads the rows one by one: up to 1,000,000....)
4. ______________________________  (hint: One more row (1,000,001) already needs 4 levels, because 100^3 is exac...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a parameterised query (WHERE name = ?) stop SQL injection, while gluing the name into the string does not?

Answer: ______________________________________________


**B. Numerical.** A table has 50,000,000 rows. How many levels does a B-tree with 200 keys per node need, and how many comparisons does binary search need?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the right-hand chart, how many levels does the B-tree need at 1,000,000 rows, and at 1,000,001 rows? Why is the curve a staircase?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the 200,000-row orders table gets 50 lookups per second by customer and 1 new order per second. Should cust_id be indexed? Name one benefit, one cost and one more place you would add an index.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
