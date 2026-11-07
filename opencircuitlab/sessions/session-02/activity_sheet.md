# Activity sheet: opencircuitlab, Session 2: Kirchhoff's laws, dividers and the loading effect

Name: ____________________   Date: ____________

**Objectives**

- State Kirchhoff's current law (KCL) at a node and voltage law (KVL) around a loop, and apply both.
- Use the voltage divider and current divider formulas, and say when they are valid.
- Predict how a load pulls down a divider's output (the loading effect).
- Solve a two-loop circuit by hand with simultaneous equations and check it with KCL, KVL and power.
- Design a divider that delivers a target voltage with a given load.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Battery 1 (V1 = 10 V) with R1 = 100 ohm and battery 2 (V2 = 4 V) with R2 = 200 ohm both feed node A; R3 = 300 ohm connects A to ground. Find I1, I2, the voltage V_A, and check with KCL, KVL and power.

1. ______________________________  (hint: Let I1 and I2 flow from the batteries towards A, so R3 carries I1 + I2...)
2. ______________________________  (hint: KVL on loop 2: 4 = 200 I2 + 300 (I1 + I2), that is 300 I1 + 500 I2 = 4...)
3. ______________________________  (hint: Determinant = 400 * 500 - 300 * 300 = 110000. I1 = (10 * 500 - 300 * 4...)
4. ______________________________  (hint: R3 carries I1 + I2 = 0.021818 A, so V_A = 300 * 0.021818 = 6.545 V. I2...)
5. ______________________________  (hint: Checks. KVL loop 2: 4 - 200 * (-0.012727) - 6.545 = 4 + 2.545 - 6.545 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does connecting a load always lower the output of a voltage divider, and when can you safely ignore the load?

Answer: ______________________________________________


**B. Numerical.** A 9 V source feeds R1 = 2 kohm in series with R2 = 1 kohm. Find the unloaded output, then the output with a 1 kohm load across R2. Check both with KVL.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the loading graph for R1 = 1700 ohm and R2 = 3300 ohm, at roughly what load resistance does the output fall to 3.0 V (about 9 percent below the target)? Which direction does the curve move if R2 is made smaller?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the output must be exactly 3.3 V from 5 V with a 4.7 kohm load. Compare R1 = 220 ohm, 470 ohm and 1000 ohm. For each, find R2, the source current and the error if the load is later unplugged. Which do you choose and why?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
