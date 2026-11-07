# Activity sheet: opencircuitlab, Session 3: Nodal analysis by matrix, Thevenin and the sensor bridge

Name: ____________________   Date: ____________

**Objectives**

- Write KCL at every node as one matrix equation G v = i and build G with the stamp method.
- Validate a solver against hand-solved circuits and against conservation of energy (power supplied equals power dissipated).
- Find a Thevenin equivalent and verify numerically that maximum power transfer happens at R_load = R_th.
- Use the Wheatstone bridge balance condition and a Monte Carlo run to see how 5 percent resistors limit a sensor.
- Recognise the failure cases: a floating node, contradictory sources, and a short circuit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 12 V source feeds R1 = 1 kohm in series with R2 = 2 kohm to ground. Find the Thevenin equivalent seen across R2, then the current, voltage and power in a 1 kohm load, and compare with the maximum power the network can ever deliver. Verify with one nodal equation.

1. ______________________________  (hint: V_th = open-circuit voltage across R2 = 12 * 2 / (1 + 2) = 8 V....)
2. ______________________________  (hint: R_th: switch the source off (replace by a wire); R1 and R2 are then in...)
3. ______________________________  (hint: With a 1 kohm load: I = 8 / (666.7 + 1000) = 4.8 mA, V_load = 4.8 mA *...)
4. ______________________________  (hint: Maximum power: P_max = 8^2 / (4 * 666.7) = 24.0 mW, at R_L = 666.7 ohm...)
5. ______________________________  (hint: Nodal check with the node between the resistors: (v - 12)/1000 + v/200...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a circuit with a node that is not connected to the reference node (a floating node) make G singular, and what does the error mean physically?

Answer: ______________________________________________


**B. Numerical.** For the 12 V, 1 kohm and 2 kohm network of Section E find the load that would receive 20 mW. Is there more than one answer? Check against P_max.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the histogram of 20000 bridges with 5 percent resistors on 5 V, the standard deviation is 72 mV. A 1 percent change of one arm gives a signal of 12.4 mV. What does this tell you about using 5 percent resistors for a sensor, and what would change with 1 percent resistors?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the Pt1000 bridge needs at least 100 mV at 100 degrees C and at most 1 mW in the sensor, with three fixed 1 kohm resistors. Choose the supply voltage, justify it, and say what limits the accuracy at 5 percent tolerance.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
