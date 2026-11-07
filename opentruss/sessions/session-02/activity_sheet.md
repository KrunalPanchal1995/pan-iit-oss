# Activity sheet: opentruss, Session 2: Equilibrium of every pin: the method of joints and sections

Name: ____________________   Date: ____________

**Objectives**

- Decide whether a truss is determinate from m + r = 2 j.
- Write sum Fx = 0 and sum Fy = 0 for each pin and solve for all bar forces and reactions.
- Use the method of sections to check one bar force without solving the whole truss.
- Choose bar areas for a stress limit and name the buckling concern for compression bars.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A Warren truss spans 6 m with bottom joints every 2 m and equilateral triangles of side 2 m (height 1.732 m): 7 joints, 11 bars, a pin and a roller. A 10 kN load acts down at the top joint at midspan. Find the forces by joints, check one by sections, and size the most loaded bar for 150 MPa.

1. ______________________________  (hint: Determinacy: m + r = 11 + 3 = 14 = 2 j = 14, so statics is enough....)
2. ______________________________  (hint: Reactions: by symmetry 5 kN up at each foot, no horizontal reaction....)
3. ______________________________  (hint: Left foot pin: the bar rising at 60 degrees gives F sin(60) + 5 = 0, s...)
4. ______________________________  (hint: Next pin, the top joint above x = 1 m: the sloping bar going down to x...)
5. ______________________________  (hint: Check by sections: cut at x = 2.5 m. Moments about the top joint at x ...)
6. ______________________________  (hint: Size the most loaded bar (8.66 kN) for 150 MPa: A = 1000 * 8.66 / 150 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** A truss has 12 joints, 21 bars and 3 support reactions. Is it determinate? What would you expect if one bar were removed, and what if one were added?

Answer: ______________________________________________


**B. Numerical.** Double the Warren load to 20 kN. Find the sloping bar forces and the middle bottom chord, and the area the chord needs at 150 MPa. Then round the areas up to 120 mm^2 for the chord and 80 mm^2 for the sloping bars: what are the stresses?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the bar chart of the Warren truss, how many bars are in tension, how many in compression, and which group is the top chord in? Which bar has the largest force?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the 20 kN load use bars of 120 mm^2 for the chord and 80 mm^2 for the other 10 bars, against 120 mm^2 for all 11 bars. Compare the steel volumes (all bars 2 m long) and say what the buckling concern changes.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
