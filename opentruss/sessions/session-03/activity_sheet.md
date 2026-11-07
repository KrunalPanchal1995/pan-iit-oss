# Activity sheet: opentruss, Session 3: A stiffness solver for any truss, validated

Name: ____________________   Date: ____________

**Objectives**

- Assemble the global stiffness matrix of any 2D pin-jointed truss from EA/L and direction cosines.
- Apply supports, solve K u = f and recover bar forces and joint deflections.
- Validate the solver with hand results, joint equilibrium and a virtual-work formula.
- Compare Pratt, Howe and Warren shapes, and detect a mechanism from the rank or condition number.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the 8 m Pratt truss (4 panels of 2 m, height 2 m, EA = 80 000 kN for every bar, 10 kN at midspan) find the midspan sag by the unit-load method and compare it with the solver.

1. ______________________________  (hint: Forces for 10 kN (statics): bottom chords +5 kN (4 bars, 2 m), top cho...)
2. ______________________________  (hint: A unit load at midspan gives forces equal to these divided by 10, so F...)
3. ______________________________  (hint: Sum of F^2 L: bottom 4 * 25 * 2 = 200; top 2 * 100 * 2 = 400; end post...)
4. ______________________________  (hint: Deflection: delta = 1165.69 / 10 / 80 000 = 0.001457 m = 1.457 mm....)
5. ______________________________  (hint: The stiffness solver gives the same 1.457 mm at midspan. Doubling the ...)

Final answer: ____________________

## Questions
**A. Conceptual.** In the Pratt truss the diagonals are in tension and in the Howe truss they are in compression, although both carry the same load. Why does it matter for the design which bars are pulled?

Answer: ______________________________________________


**B. Numerical.** Use the unit-load method for the three-bar triangle truss (span 6 m, height 3 m, 10 kN at the apex, EA = 80 000 kN). Give the apex sag in mm, then check with the solver.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the sag against EA graph, why are the three curves hyperbolas (proportional to 1/EA), and what does that tell you about doubling the steel area?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the 12 m footbridge (6 panels, 2 m high, 6 kN/m) is sized by stress alone (150 MPa, 100 mm^2 minimum). The sag limit is 15 mm. For each shape say whether the stress-only design passes, and what the lightest shape is when the limit is enforced by scaling all areas up together.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
