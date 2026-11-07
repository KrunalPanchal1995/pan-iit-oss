# Activity sheet: openbeam, Session 3: Solve it numerically: a finite-element beam, validated and refined

Name: ____________________   Date: ____________

**Objectives**

- Assemble and solve a 2-node Euler-Bernoulli finite-element beam with uniform and point loads.
- Validate the solver against exact formulas, including a point load that does not sit on a node.
- Measure mesh convergence and say how fast the errors fall for deflection and moment.
- Run a sensitivity study (E, depth) and name a limit of the theory (shear deformation).
- Use the solver for a footbridge-style check with a self-weight, a deflection limit and a factor of safety.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A simply supported steel beam spans L = 4 m with E I = 200 GPa x 8.0e-6 m^4 = 1.6e6 N m^2. Find the mid-span deflection (a) for a 10 kN centre load, (b) for a uniform load of 5 kN/m, and compare each with the finite-element solver on a 2-element and an 8-element mesh. Then give both loads together.

1. ______________________________  (hint: (a) w = P L^3 / (48 E I) = 10 000 x 64 / (48 x 1.6e6) = 640 000 / 76 8...)
2. ______________________________  (hint: (b) w = 5 q L^4 / (384 E I) = 5 x 5000 x 256 / (384 x 1.6e6) = 6 400 0...)
3. ______________________________  (hint: Run solve_beam: the 2-element mesh gives 8.3333 mm for (a), the 8-elem...)
4. ______________________________  (hint: Both loads act together: deflections add (superposition for a linear e...)
5. ______________________________  (hint: Why still refine the mesh? The moment is a second derivative of w; the...)

Final answer: ____________________

## Questions
**A. Conceptual.** The finite-element deflection is exact at the nodes even with 2 elements, but the bending moment is not. Why?

Answer: ______________________________________________


**B. Numerical.** A simply supported beam of span 5 m, EI = 2.0e6 N m^2 carries a uniform load of 4 kN/m. Find the mid-span deflection and its maximum moment with units, and say what the 4-element solver's moment error against the peak should be.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the log-log convergence plot, the moment error is 2.1% of the peak for n = 8. Estimate it for n = 32 and say what slope the line has.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the footbridge girder (6 m span, 3.5 kN/m, 5 kN at mid-span, steel, flanges 150 x 10 mm, web 6 mm, depths in 10 mm steps) find the lightest passing depth with a factor of safety of 1.5, and then with a factor of safety of 3. Which limit governs and what does it cost in mass?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
