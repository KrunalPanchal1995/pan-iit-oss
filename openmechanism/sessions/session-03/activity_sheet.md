# Activity sheet: openmechanism, Session 3: Calibrating a toy mechanism against noisy experiments

Name: ____________________   Date: ____________

**Objectives**

- Write an implicit (trapezoidal) ODE solver for a stiff toy mechanism and validate it against a formula and by halving the step.
- Calibrate two rate-constant scale factors from noisy synthetic ignition delays by Levenberg-Marquardt least squares.
- Read parameter uncertainty and correlation from the Jacobian, and check that the fit recovers a known truth.
- Test how the fit responds to noise level, starting guess and a systematic error, and explain the power-mean objective.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Calibrate from the nominal mechanism (s1 = s2 = 1) using the synthetic data set with seed 1 (truth: s1 = 0.5, s2 = 1.25). Report the fit, its uncertainty, and whether the truth is recovered.

1. ______________________________  (hint: Start: theta = (0, 0), cost 0.5 sum r^2 = 72.5. Levenberg-Marquardt re...)
2. ______________________________  (hint: Scale factors: s1 = exp(-0.634) = 0.53 and s2 = exp(0.207) = 1.23, com...)
3. ______________________________  (hint: Uncertainty from (J^T J)^-1: one-sigma of (ln s1, ln s2) = (0.55, 0.05...)
4. ______________________________  (hint: z-scores = (fit - truth) / sigma: (-0.634 + 0.693) / 0.551 = 0.11 and ...)

Final answer: ____________________

## Questions
**A. Conceptual.** The fitted ln s1 has a one-sigma uncertainty of 0.55 while ln s2 has 0.053. Explain why the data pin k2 down much better, and why the two uncertainties are strongly correlated.

Answer: ______________________________________________


**B. Numerical.** The calibration used 12 experiments and gave a one-sigma uncertainty of 0.053 for ln s2. If you repeat the whole campaign 4 times (48 experiments, same noise), what uncertainty do you expect? What would 4 times less noise give?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the cost-surface picture, what does the long axis of the valley tell you, and where would the one-sigma ellipse of a set of experiments at 1300 and 1400 K only look different?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you have 12 experiments to spend, all with 1 mol/L fuel, and the temperature may be 900 to 1400 K. Compare the shipped design (8 temperatures plus 4 at 2 mol/L) with putting 6 experiments at 900 K and 6 at 1400 K. Which gives the smaller uncertainty of ln s1, and what could go wrong?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
