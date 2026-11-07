# Activity sheet: openunits, Session 3: A toy trajectory and a units-checked wrapper

Name: ____________________   Date: ____________

**Objectives**

- Explain, with well-established facts, how a lbf*s versus N*s mismatch affected the Mars Climate Orbiter.
- Simulate a toy trajectory correction and compute the miss distance caused by a unit factor of 4.448222.
- Validate the simulation against a closed-form formula and test its sensitivity to mass, impulse and number of firings.
- Write and use a numpy-only units-checked wrapper, and say exactly which errors it catches and which it cannot.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 600 kg toy spacecraft makes 12 firings of 0.2 lbf*s on days 10, 23, 35, ... 150 (mean day 80). The software reads the numbers as N*s. Find the miss distance at day 180 by hand and compare with the simulation.

1. ______________________________  (hint: Mean firing day is 80, so the average drift time is 180 - 80 = 100 day...)
2. ______________________________  (hint: Per firing the true dv is 0.2 * 4.448222 / 600 = 0.0014827 m/s; the pr...)
3. ______________________________  (hint: Difference per firing: 0.0011494 m/s. For 12 firings: 0.013793 m/s....)
4. ______________________________  (hint: Miss = 0.013793 m/s * 8.64 million s = 119 170 m = 119.17 km....)
5. ______________________________  (hint: The simulation gives the same 119.17 km, and the actual path is 4.4482...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a dimension check not catch a lbf*s number read as N*s? What kind of design would catch it?

Answer: ______________________________________________


**B. Numerical.** Eight firings of 0.5 lbf*s each (on days 10, 30, ... 150) are read as N*s on a 600 kg craft. What is the miss at day 180?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the miss-versus-firings graph, what is the shape of the curve and what does doubling the spacecraft mass do to it?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with 12 firings of 0.2 lbf*s on a 600 kg craft the miss must stay below 5 km. How wrong may the software's conversion factor be? Propose two checks that would have prevented the bug.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
