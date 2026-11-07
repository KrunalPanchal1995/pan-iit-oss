# Activity sheet: openbeam, Session 4: A load that moves: the envelope of shear and moment

Name: ____________________   Date: ____________

**Objectives**

- Compute reactions, shear and bending moment for a group of point loads at any position on a simply supported span.
- Build the envelope (the worst shear and moment at every section) by sweeping the group across the span.
- Check the sweep against two independent routes: influence lines, and the "equal distance from mid-span" rule for the worst position.
- Explain why designing for one axle, or for all axles at mid-span, gives the wrong answer.
- Use the envelope to choose the lightest girder that passes a stress and a deflection limit.

## Before you start: predict
In your own words, what do you think will happen to the peak moment when you move the two axles further apart in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Two axles of 10 kN, 3 m apart, cross a simply supported span of L = 12 m. Find the largest bending moment and where it happens, then compare it with both axles at mid-span and one axle at mid-span.

1. ______________________________  (hint: The resultant is 20 kN, halfway between the axles, 1.5 m from each.)
2. ______________________________  (hint: Worst position: an axle and the resultant at equal distances from mid-span, so the rear axle is d/4 = 0.75 m left of mid-span: x = 5.25 m, front axle 8.25 m.)
3. ______________________________  (hint: R_A = 10 x (12 - 5.25)/12 + 10 x (12 - 8.25)/12 = 8.75 kN and R_B = 11.25 kN.)
4. ______________________________  (hint: M under the rear axle = 8.75 x 5.25 = 45.94 kN m; under the front axle 11.25 x 3.75 = 42.19 kN m.)
5. ______________________________  (hint: Shortcuts: both at mid-span 2 x 10 x 12 / 4 = 60 kN m, one axle 30 kN m. The answer lies between them.)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the envelope of bending moment under two moving axles lie below the moment you get with both axles at mid-span, and above the moment with just one axle at mid-span?

Answer: ______________________________________________


**B. Numerical.** Two axles of 20 kN, 4 m apart, cross a simply supported span of L = 10 m. Find the largest bending moment, the rear axle position at which it happens, and the largest shear. Check with the hand formula.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the spacing figure for two 10 kN axles on a 12 m span, read the peak moment at d = 2 m, and say where the curve becomes flat and why.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the 12 m girder of the mini-project (flanges 150 x 10 mm, web 6 mm, deck 3 kN/m, factor of safety 1.5, deflection limit L/360). What is the lightest passing depth when you use the true envelope, and what does the "both axles at mid-span" shortcut cost in mass? Does the "one axle" shortcut produce a safe girder?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
