# Activity sheet: openheartflow, Session 3: Elastic arteries: the two-element Windkessel model

Name: ____________________   Date: ____________

**Objectives**

- Write the Windkessel equation C dP/dt = Q_in(t) - P/R and explain each term.
- Solve it with your own RK4 code and read systolic, diastolic, pulse and mean pressure from the wave.
- Validate the solver against the exact diastolic decay and the mean-flow balance, and measure its order of accuracy.
- Show the effect of stiffer arteries, heart rate and the parameters, and recognise the failure case.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For R = 1.214 mmHg s/mL, C = 1.251 mL/mmHg, heart rate 70 and stroke volume 70 mL, find the time constant, the factor by which the pressure falls during diastole, the end-of-beat pressure when the pressure at the end of ejection is 119.3 mmHg, and the mean pressure from the mean-flow balance.

1. ______________________________  (hint: Beat length T = 60/70 = 0.857 s; systole T_s = 0.3 T = 0.257 s; diasto...)
2. ______________________________  (hint: Time constant tau = R C = 1.214 x 1.251 = 1.519 s....)
3. ______________________________  (hint: Fall factor in diastole = exp(-0.600 / 1.519) = 0.674....)
4. ______________________________  (hint: The simulation gives P = 119.3 mmHg at the end of ejection, so the pre...)
5. ______________________________  (hint: The pressure dips to the minimum of 80.0 mmHg a hair after the next ej...)
6. ______________________________  (hint: Mean inflow = 70 x 70 / 60 = 81.67 mL/s, so the mean pressure = R x me...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the arterial pressure not drop to zero in diastole when the heart is not pushing? Why does a stiffer artery change the pulse pressure but not the mean pressure?

Answer: ______________________________________________


**B. Numerical.** With R = 1.214, a heart rate of 60 beats per minute and a stroke volume of 70 mL, find the mean pressure from the mean-flow balance. Compare with the 70 beats case (99.1 mmHg).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the stiffness figure the three waves have pulse pressures 20.1, 40.0 and 78.9 mmHg for C = 2.5, 1.251 and 0.626. What pattern do you see, and what is the mean pressure in each case?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose R and C so that the model has a mean pressure of 90 mmHg and a pulse pressure close to 30 mmHg at 70 beats per minute and 70 mL. Report the systolic and diastolic values. This is an illustrative exercise, not a target for any person.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
