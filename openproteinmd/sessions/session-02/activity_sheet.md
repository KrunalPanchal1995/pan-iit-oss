# Activity sheet: openproteinmd, Session 2: Velocity Verlet: a time step you can trust

Name: ____________________   Date: ____________

**Objectives**

- Write one velocity-Verlet step and explain its three parts (half kick, drift, half kick).
- Measure energy conservation and compare it with an exact answer.
- Compute the kinetic temperature of a chain from its velocities, counting degrees of freedom correctly.
- Choose a time step from the rule: energy error about (omega dt)^2 / 4 and stability only if omega dt < 2.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A bond has omega = 10 per tau. What is the largest time step that keeps the Verlet energy error below 1 percent? What is the stability limit?

1. ______________________________  (hint: Rule: error is about (omega dt)^2 / 4. We need (omega dt)^2 / 4 < 0.01...)
2. ______________________________  (hint: So (omega dt)^2 < 0.04 and omega dt < 0.2, which gives dt < 0.2 / 10 =...)
3. ______________________________  (hint: Stability needs omega dt < 2, so dt < 2 / 10 = 0.2 tau, ten times larg...)
4. ______________________________  (hint: Check by running it: the largest energy error over 20 periods is 0.009...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a poor integrator such as explicit Euler make the energy climb, while Verlet only makes it wobble?

Answer: ______________________________________________


**B. Numerical.** A 6-bead chain in 2D has zero total momentum and a total kinetic energy of 3.0 epsilon. What is its kinetic temperature? How many degrees of freedom did you use?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the spring numbers (energy error 0.0025 at dt = 0.01 and 0.0625 at dt = 0.05, with omega = 10), what is the slope on a log-log plot and what does it tell you about halving the time step?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for a stiffer chain with K = 400 the fastest vibration has omega about 2 sqrt(K) = 40 per tau (an estimate from a harmonic chain). Choose the largest time step with energy error below 1 percent, and say what you give up.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
