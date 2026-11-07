# Roadmap: the path to the opensql Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Composite and covering indexes

**You will learn:** How an index on two columns can answer a range query and its sort without a temporary sort.

**You will build:** A query tuned with the right composite index, with before-and-after plans.

**Checkpoint (not met by the shipped code):** For a range query on key ordered by val on the 200,000-row table, EXPLAIN QUERY PLAN shows no 'USE TEMP B-TREE FOR ORDER BY' line (the shipped single-column index shows one).

**Difficulty:** intermediate

## Session 5: Window functions and running totals

**You will learn:** Computing a running total per customer inside SQL.

**You will build:** A canteen report with a running revenue column per customer.

**Checkpoint (not met by the shipped code):** The SQL running total equals numpy cumsum of the same sales for every customer; the shipped code has no window function.

**Difficulty:** intermediate

## Session 6: Messy spreadsheet to third normal form

**You will learn:** Finding the dependencies in a flat file and splitting it step by step.

**You will build:** A script that loads a 1,000-row flat order file and builds customers, items and orders tables.

**Checkpoint (not met by the shipped code):** The joined tables reproduce the flat file exactly while storing at most 40 percent of its cells (the shipped 12-order example stores 66 of 72 cells).

**Difficulty:** intermediate

## Session 7: Concurrency and the write-ahead log

**You will learn:** Why two writers can interfere, and what locks and journal modes do.

**You will build:** Several threads transferring money at the same time against one file database.

**Checkpoint (not met by the shipped code):** Four threads making 500 transfers each leave the total unchanged and every transfer accounted for; the shipped code has one connection only.

**Difficulty:** advanced

## Session 8: A tiny B-tree and the query visualiser

**You will learn:** Building the index structure yourself and animating a query being answered.

**You will build:** Your own B-tree with insert and search, drawn step by step, plus a visualiser like the Target.

**Checkpoint (not met by the shipped code):** Insert 100,000 shuffled keys with 100 keys per node, find every key, and report a depth of at most 3 (the shipped code only computes the depth formula).

**Difficulty:** advanced

## The final step

Combine the milestones: a visualiser that takes a SELECT with a WHERE and a JOIN on a small table, animates the filter and the join, shows the plan, and races a scan against your own B-tree. If your result looks like the Target animation, open a pull request and tell us how you did it.
