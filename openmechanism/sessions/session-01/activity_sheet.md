# Activity sheet: openmechanism, Session 1: A reaction network as equations, and what an experiment sees

Name: ____________________   Date: ____________

**Objectives**

- Write a two-step reaction network A -> B -> C as three rate equations.
- Solve the equations with small time steps (Euler's method) and compare with the exact formula.
- Explain why the intermediate B rises, peaks and falls, and find when it peaks.
- Describe what an experiment measures and how noise limits what it can tell you.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
With k1 = 0.5 per s and k2 = 1.5 per s, when does B peak, how large is B then, and what is B at t = 1 s?

1. ______________________________  (hint: Peak time: t* = ln(k2/k1) / (k2 - k1) = ln 3 / 1.0 = 1.0986 s....)
2. ______________________________  (hint: Peak height: B = (k1/k2)^(k2/(k2-k1)) = (1/3)^1.5 = 0.1925 mol/L....)
3. ______________________________  (hint: Check at the peak: A = exp(-0.5 x 1.0986) = 0.577, so feed k1 A = 0.28...)
4. ______________________________  (hint: At t = 1 s: B = 0.5 / 1.0 x (exp(-0.5) - exp(-1.5)) = 0.5 x (0.6065 - ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does B rise first and then fall, even though both reactions run all the time? At which moment is its rate of change zero?

Answer: ______________________________________________


**B. Numerical.** For k1 = 0.4 per s and k2 = 0.8 per s, find the time and height of the peak of B. Check the units and that the answer is sensible.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the concentration graph with k1 = 0.5 and k2 = 1.5, which curve rises fastest at the moment B is at its peak, and why?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you may measure B at one time only. The unknown mechanism is either (k1, k2) = (0.5, 1.5) or (1.5, 0.5), and the measurement noise is 0.01 mol/L. Which time do you choose, and how well will you tell the two apart?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
