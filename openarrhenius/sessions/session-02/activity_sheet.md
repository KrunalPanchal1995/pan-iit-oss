# Activity sheet: openarrhenius, Session 2: Fit with units, and design the experiment

Name: ____________________   Date: ____________

**Objectives**

- Fit ln A and Ea with numpy.polyfit, with and without weights, and report Ea in kJ/mol.
- Compute the standard error of Ea from the spread of 1000/T and check it by simulation.
- Fit the modified Arrhenius form k = A T^n exp(-Ea/(R T)) by linear least squares.
- Choose measurement temperatures to pin Ea down best, and say what the choice costs.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Temperatures 600, 700, 800, 900 and 1000 K, error 5 percent (sigma = 0.05). Find Sxx and the standard error of Ea, then fit a synthetic data set generated with true A = 1e13 per s and Ea = 150 kJ/mol.

1. ______________________________  (hint: x = 1000/T = 1.6667, 1.4286, 1.2500, 1.1111, 1.0000; the mean is 1.291...)
2. ______________________________  (hint: Sxx = sum of squared deviations from 1.2913 = 0.2788....)
3. ______________________________  (hint: SE(Ea) = 8.3145 x 0.05 / sqrt(0.2788) = 0.787 kJ/mol....)
4. ______________________________  (hint: Fit of the synthetic data (seed 1) with numpy.polyfit: Ea = 149.70 kJ/...)
5. ______________________________  (hint: Check: 149.70 is within 0.3 kJ/mol of 150, inside one standard error (...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a wider range of 1000/T give a smaller error in Ea, even though the number of data points is the same?

Answer: ______________________________________________


**B. Numerical.** For temperatures 600 to 1000 K in steps of 100 K and an error of 10 percent, what is the standard error of Ea?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the figure, the narrow window (850 to 1000 K) and the wide window (500 to 1500 K) each use six points. What standard errors does the theory give and what is their ratio?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: six measurements between 500 and 1500 K at 5 percent error. Compare six points evenly spaced in 1000/T with three at each end. Which is better for the error of Ea, and what do you lose?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
