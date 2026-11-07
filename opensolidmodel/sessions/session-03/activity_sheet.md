# Activity sheet: opensolidmodel, Session 3: How a sketch keeps its corners where you told it: a constraint solver

Name: ____________________   Date: ____________

**Objectives**

- Write sketch statements (fixed, distance, horizontal, vertical, perpendicular) as equations that must be zero.
- Explain Newton's method for several unknowns and why it needs a good first guess.
- Count the degrees of freedom of a sketch from the rank of the Jacobian and tell fully constrained from under-constrained.
- Recognise redundant and contradicting statements, and rebuild a parametric L-bracket by solving again.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A triangle has one corner p0 fixed at the origin, p1 on the horizontal axis 4 mm from it, p2 at 3 mm from p0 and 5 mm from p1. Which statements does that make, and where are the points? Then find the area of the L-bracket 50 x 50 x 5 and its mass for 200 mm.

1. ______________________________  (hint: Statements: fix p0 at (0, 0) (2 residuals), p0-p1 horizontal (1), |...)
2. ______________________________  (hint: Newton's method from the rough guess (0, 0), (3, 0.5), (0.5, 2) con...)
3. ______________________________  (hint: A guess with p2 below the axis gives the mirror image p2 = (0, -3):...)
4. ______________________________  (hint: L-bracket: 6 points, 12 coordinates; p0 is fixed (2), five lines ar...)
5. ______________________________  (hint: Area from the corner points by the shoelace formula: 475 mm2, equal...)

Final answer: ____________________

## Questions
**A. Conceptual.** A sketch of three points has p0 fixed, p0-p1 horizontal and the two distances |p0 p1| = 4 and |p0 p2| = 3. How many degrees of freedom are left, and what can you drag?

Answer: ______________________________________________

**B. Numerical.** Why does the solver need a first guess, and what happens if the first guess has the corner p2 below the axis?

Answer: ______________________________________________

**C. Graph and simulation interpretation.** To the 3-4-5 triangle add the statement that the angle at p0 is 90 degrees. What does the solver report, and why is this not an error? Then change |p1 p2| = 5 to 8: what happens?

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: a 60 x 40 mm L-bracket, 200 mm long, must weigh at most 0.8 kg. Find the largest thickness, to 0.01 mm, using area = b t + (h - t) t.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
