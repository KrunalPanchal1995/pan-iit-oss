# Activity sheet: opengps, Session 2: Distance is speed of light times time

Name: ____________________   Date: ____________

**Objectives**

- Compute a pseudorange from a travel time, and a timing error from a range error.
- Linearise the sphere equations by subtracting one from the others and solve the system.
- Explain why three spheres leave two points in 3D and what a fourth range does.
- Solve a design problem: how accurate must a clock be for a given position accuracy?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Three ground beacons B1 = (0, 40), B2 = (120, 40), B3 = (60, 95) km send timed signals to a receiver. It records travel times 158.22, 255.12 and 238.80 microseconds. Find the position by subtracting equations.

1. ______________________________  (hint: Ranges r = c t: 158.22 us gives 47.43 km, 255.12 us gives 76.49 km, 23...)
2. ______________________________  (hint: Subtract equation 1 from equation 2: 2 (120, 0) . (x, y) = (14400 + 16...)
3. ______________________________  (hint: Subtract equation 1 from equation 3: 2 (60, 55) . (x, y) = (3600 + 902...)
4. ______________________________  (hint: Put x = 45: 5400 + 110 y = 8150, so y = 25 km....)
5. ______________________________  (hint: Check with equation 1: sqrt(45^2 + (25 - 40)^2) = sqrt(2250) = 47.43 k...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does subtracting one sphere equation from another make the problem linear, and what do the new equations represent geometrically?

Answer: ______________________________________________


**B. Numerical.** A satellite clock is wrong by 50 nanoseconds. What range error is that? Is it small compared with a 10 m accuracy goal?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the timing-error figure the position-error line is steeper than the range-error line. What does the ratio of slopes tell you, and what could make it larger?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you need the position error below 10 m, and in the toy geometry of the figure the amplification is about 2.14. How accurate (in nanoseconds) must the clock error on one range be? What steadiness over one day (a fraction) does that need?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
