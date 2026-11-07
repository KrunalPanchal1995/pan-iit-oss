# Activity sheet: openohm, Session 2: Resistor networks, power ratings and a design to a limit

Name: ____________________   Date: ____________

**Objectives**

- Compute the equivalent resistance of series and parallel combinations.
- Find the current and the power in every resistor of a network.
- Check each resistor against its power rating.
- Solve a design problem: choose standard E12 values that meet a current and a power limit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 12 V supply feeds a grid of six 180 ohm resistors: two in series per branch, three branches in parallel. Find the total resistance, the current, and the power in each resistor.

1. ______________________________  (hint: One branch is two resistors in series: 180 + 180 = 360 ohm....)
2. ______________________________  (hint: Three equal 360 ohm branches in parallel: R_total = 360 / 3 = 120 ohm....)
3. ______________________________  (hint: Total current I = 12 / 120 = 0.1 A....)
4. ______________________________  (hint: Each branch carries 0.1 / 3 = 0.0333 A....)
5. ______________________________  (hint: Power in each resistor = (0.0333)^2 x 180 = 0.200 W, below the 0.25 W ...)
6. ______________________________  (hint: Check: six resistors x 0.2 W = 1.2 W = V I = 12 x 0.1. The powers add ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does adding a resistor in parallel make the total resistance smaller, even though you added more material?

Answer: ______________________________________________


**B. Numerical.** A 12 V supply feeds a 6 ohm resistor in series with two 12 ohm resistors in parallel. Find the total current, the power in the 6 ohm resistor and the power in each 12 ohm resistor.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the power graph for a single 120 ohm resistor, at what supply voltage does the curve cross the 0.25 W rating? Where does it cross for the 2 x 3 grid of 180 ohm resistors?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with a 12 V supply and 0.25 W resistors, get 50 mA within 5 percent using the fewest E12 resistors. State the network and its checks.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
