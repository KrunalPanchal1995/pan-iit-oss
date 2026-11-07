# Activity sheet: openchaos, Session 1: Two almost identical starts drift apart

Name: ____________________   Date: ____________

**Objectives**

- Explain why a single pendulum is predictable and what that means for two nearly identical starts.
- Simulate a single and a double pendulum with the Runge-Kutta 4 rule.
- Measure how a start difference of 1e-8 rad grows in each system.
- Read a log-scale graph and say how fast a gap grows.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 1 m pendulum swings through a small angle. Find its swing time from the formula and compare it with the simulation.

1. ______________________________  (hint: The formula is T = 2 pi sqrt(L / g) with L = 1 m and g = 9.81 m/s^2....)
2. ______________________________  (hint: L / g = 1 / 9.81 = 0.10194 s^2, and its square root is 0.31928 s....)
3. ______________________________  (hint: T = 2 pi x 0.31928 = 2.0061 s....)
4. ______________________________  (hint: The simulation with a 2 degree release, measured from the time the pen...)
5. ______________________________  (hint: Sanity check: a pendulum about one metre long ticks roughly once every...)

Final answer: ____________________

## Questions
**A. Conceptual.** A friend says: the double pendulum moves randomly, so no equation can describe it. Explain what is right and what is wrong in that sentence.

Answer: ______________________________________________


**B. Numerical.** Find the swing time of a pendulum 0.25 m long with the formula T = 2 pi sqrt(L / g). Is it more or less than the 1 m pendulum, and by what factor?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the gap graph, the double pendulum's gap grows from 3.2e-4 rad at 10 s to 0.62 rad at 15 s. By what factor does it grow in those 5 s, and what is the growth rate per second?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you may measure the starting angle with a protractor of precision 1e-3 rad. Using a growth rate of 1.5 per second, how long can you forecast to within 0.1 rad? What precision would 10 s need? State your assumption.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
