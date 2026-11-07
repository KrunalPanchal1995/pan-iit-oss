# Activity sheet: opencircuitlab, Session 5: A nonlinear part: the diode and Newton's method

Name: ____________________   Date: ____________

**Objectives**

- Explain why a diode cannot be a fixed entry of G, and write its companion model (a resistor and a current source) from the Shockley law.
- Wrap a Newton loop around the Session 3 solver and stop it on the KCL residual and the voltage change.
- Validate against an independent method (bisection) and against power balance on a small network.
- Recognise the failure cases: the plain loop from 0 V, a poor start, too few passes, a floating part, and a reversed diode.
- Choose a resistor for a diode indicator from the E12 series over a supply range, and judge the 0.7 V rule.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the 5 V, 1 kohm and diode circuit, make one Newton step by hand from the starting guess V_0 = 0.6 V. Find the tangent (g and i_eq), the new diode voltage, and the KCL residual before and after. Compare with the exact answer.

1. ______________________________  (hint: The current at 0.6 V: I = 1e-12 (exp(0.6 / 0.025852) - 1) = 12.01 mA....)
2. ______________________________  (hint: The slope there: g = (I + I_s) / (n V_T) = 0.01201 / 0.025852 = 0.4646...)
3. ______________________________  (hint: The companion source: i_eq = I - g V_0 = 0.01201 - 0.4646 x 0.6 = -0.2...)
4. ______________________________  (hint: The new voltage: V = (V_s / R - i_eq) / (1 / R + g) = (0.005 + 0.2667)...)
5. ______________________________  (hint: The residual before is (0.6 - 5) / 1000 + 12.01 mA = +7.61 mA; after t...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can the diode not be put into the matrix equation G v = i of Session 3 with a fixed conductance, and what exactly does the companion model (a resistor and a current source) replace at each pass?

Answer: ______________________________________________


**B. Numerical.** Do one plain Newton step for the 5 V, 1 kohm circuit from the starting guess 0.5 V instead of 0.6 V. Give g, i_eq, the new diode voltage and the KCL residual before and after. What do you notice, and what does it predict for the number of passes?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 2 the residual of the first four passes is above 1e71 A and only the fifth is below 1 A, yet the loop ends after 7 passes at 4e-16 A. Does this mean the first passes were wrong? What does the residual measure and what is the limiter doing?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a colleague's simulator uses plain Newton from 0 V and reports 'singular matrix' for the 5 V, 1 kohm diode circuit. Propose two repairs, say how you would test them, and name a risk of each.

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
