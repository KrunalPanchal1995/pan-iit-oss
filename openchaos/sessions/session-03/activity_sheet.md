# Activity sheet: openchaos, Session 3: Measuring chaos and the limits of forecasting

Name: ____________________   Date: ____________

**Objectives**

- Compare RK4 with a symplectic solver (implicit midpoint) by their energy drift over a long run.
- Estimate the largest Lyapunov exponent from the straight-line growth of the log of a separation, and by the Benettin method.
- Build a flip-time map of release angles and validate it against an energy argument.
- Compute a predictability horizon and say why it grows only logarithmically with the measurement precision.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A lab measures the starting angles of a double pendulum to 1e-6 rad. If lambda = 1.4 per second and we accept an error of 0.1 rad, how long is the forecast good? How much longer if the measurement is a thousand times better?

1. ______________________________  (hint: t_h = ln(Delta / delta0) / lambda = ln(0.1 / 1e-6) / 1.4 = ln(100000) ...)
2. ______________________________  (hint: ln(100000) = 11.513, so t_h = 11.513 / 1.4 = 8.22 s....)
3. ______________________________  (hint: With delta0 = 1e-9: ln(1e8) = 18.421, so t_h = 18.421 / 1.4 = 13.16 s....)
4. ______________________________  (hint: The gain is ln(1000) / 1.4 = 6.908 / 1.4 = 4.93 s: a thousand times be...)
5. ______________________________  (hint: Check with the simulation for the 120 degree release: the Benettin lam...)

Final answer: ____________________

## Questions
**A. Conceptual.** A colleague proposes to forecast a chaotic system for twice as long by buying a measuring device twice as precise. Explain why this does not work and what would be needed instead.

Answer: ______________________________________________


**B. Numerical.** For lambda = 1.2 per second, a start error of 1e-8 rad and an accepted error of 0.5 rad, find the predictability horizon. Give the units and a sanity check.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 2 the straight segment rises from d = 1e-6 at 3.7 s to d = 1e-2 at 10.3 s, while the least-squares fit over that window gives lambda = 1.21 per second and the Benettin method 1.43 per second. Estimate lambda from the two end points, and explain why the three numbers differ.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you want a 15 s forecast within 0.1 rad for the 120 degree release (lambda about 1.43 per second). What start precision does the formula demand? Is it realistic for a rotary encoder of 1e-5 rad resolution? What would you do instead?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
