# Activity sheet: opencircuitlab, Session 4: Read a netlist: text in, voltages out

Name: ____________________   Date: ____________

**Objectives**

- Read a value with a scale suffix (k, meg, m, u, ...) and avoid the 1M trap, where M means milli.
- Turn the lines of a netlist into the lists the Session 3 solver needs, and refuse a broken line with its line number.
- Validate the reader against hand results (the two-loop circuit from text) and with a write-and-read round trip on random networks.
- Write a checker that reports every problem in a file at once, with errors for unsolvable files and warnings for suspicious values.
- Recognise the failure cases: unreadable values, repeated names, floating parts, missing ground, and typos that still solve.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A student writes the file `V1 in 0 12`, `R1 in out 10k`, `R2 out 0 1M` and expects a divider that gives about 12 V at `out`. Read the file by hand, give V(out) and the current of V1 as written, then the same for the intended 1meg, and say what the checker reports.

1. ______________________________  (hint: Values: `12` is 12 V, `10k` is 10 000 ohm and `1M` is 0.001 ohm, becau...)
2. ______________________________  (hint: Nodes: `0` is the reference, `in` becomes node 1 and `out` node 2 (ord...)
3. ______________________________  (hint: As written the divider is V(out) = 12 x 0.001 / (10 000 + 0.001) = 1.2...)
4. ______________________________  (hint: With `1meg`: V(out) = 12 x 1 000 000 / 1 010 000 = 11.88 V and the cur...)
5. ______________________________  (hint: The checker reports one warning on line 3: R2 is only 1m ohm (M means ...)

Final answer: ____________________

## Questions
**A. Conceptual.** The checker reports the line `R4 b 0 1M` (1 milliohm) as a warning, not an error, although it is almost certainly a typo for `1meg`. Why is a warning the right level, and give one real part that has a resistance of about a milliohm?

Answer: ______________________________________________


**B. Numerical.** The repaired bridge has V_th = 403.56 mV and R_th = 1080.7 ohm as seen by the meter. A meter should take away at most 0.5 percent of the reading. What input resistance does it need, and which meter from the list 1k, 2k, 5k, ... 100meg is the smallest that works? Give a sanity check.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 2 the same digits 300 give V(A) = 0.036 V with the suffix m, 6.545 V with no suffix and 7.998 V with k. Both wrong suffixes are one letter away from the intended file. Which typo is more dangerous, and why?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you have to write the checker for a classroom where students type netlists by hand. Choose five rules, say which are errors and which are warnings, and name one mistake your checker can never find.

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
