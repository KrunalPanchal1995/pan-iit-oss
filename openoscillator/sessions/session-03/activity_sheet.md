# Activity sheet: openoscillator, Session 3: The real pendulum: RK4, validation and resonance

Name: ____________________   Date: ____________

**Objectives**

- Simulate the nonlinear pendulum theta'' = -(g/L) sin(theta) - c theta' with the RK4 method.
- Validate a simulation against an analytic limit, energy conservation and a damped envelope.
- Explain and measure how the period grows with amplitude, and where the small-angle formula fails by 1 and 5 percent.
- Draw a resonance curve and read the quality factor Q; recognise when explicit Euler fails.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 1.0 m pendulum is released from 40 degrees. Find its exact period and compare it with the small-angle formula and the series. At which amplitude is the small-angle formula wrong by 5 percent? Validate the simulation, and show what Euler does.

1. ______________________________  (hint: T0 = 2 pi sqrt(1.0 / 9.81) = 2.0061 s....)
2. ______________________________  (hint: Exact (AGM): cos(20 degrees) = 0.9397, AGM(1, 0.9397) = 0.9697, so T =...)
3. ______________________________  (hint: Series: theta0 = 0.6981 rad, theta0^2/16 = 0.0305, 11 theta0^4/3072 = ...)
4. ______________________________  (hint: The small-angle formula is low by (2.0689 - 2.0061) / 2.0689 = 3.04 pe...)
5. ______________________________  (hint: Validation: for a 0.5 degree swing the largest difference between RK4 ...)
6. ______________________________  (hint: Resonance: for zeta = 0.05, w0 = 2 pi rad/s, the RK4 amplitude peak is...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the period of a real pendulum increase with amplitude, while a mass on an ideal spring has a period that does not?

Answer: ______________________________________________


**B. Numerical.** A clock with a pendulum tuned to a 2.000 s period for small swings is driven so that it swings 30 degrees. By what percent is the period longer and how many seconds per day does the clock lose?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the resonance curve for zeta = 0.05 the peak is at Omega / w0 = 0.9975 with height 10. Predict the peak height if the damping doubles to zeta = 0.1, and say what happens to the width of the peak.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you need the pendulum energy to stay within 1 percent over 20 s (60 degrees). Compare RK4 with explicit Euler: which time step and how many steps does each need? Justify.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
