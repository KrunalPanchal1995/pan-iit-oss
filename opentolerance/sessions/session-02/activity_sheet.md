# Activity sheet: opentolerance, Session 2: ISO fits and the worst-case stack

Name: ____________________   Date: ____________

**Objectives**

- Decode a fit such as 25 H7/g6 into tolerance zones for the hole and the shaft.
- Compute the minimum and maximum clearance of a fit and classify it as clearance, transition or interference.
- Choose a fit for a sliding bearing and for a press fit from stated requirements.
- Add tolerances along a chain of parts (worst-case stack-up) and verify it by trying every corner.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Compute the limits and the clearance of the fit 25 H7/g6, then the worst-case gap of a four-part stack: a housing of 40.00 +-0.10 mm holding three plates of 10.00 +-0.05, 12.00 +-0.05 and 15.00 +-0.08 mm.

1. ______________________________  (hint: Hole H7: EI = 0, ES = +21 um, so the hole is 25.000 to 25.021 mm....)
2. ______________________________  (hint: Shaft g6: es = -7 um and the width is IT6 = 13 um, so ei = -7 - 13 = -...)
3. ______________________________  (hint: Smallest clearance = EI - es = 0 - (-7) = 7 um (0.007 mm = 25.000 - 24...)
4. ______________________________  (hint: The minimum is not negative, so 25 H7/g6 is a clearance fit. Check: 41...)
5. ______________________________  (hint: Stack: nominal gap = 40.00 - 10.00 - 12.00 - 15.00 = 3.00 mm. Worst-ca...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is a fit with minimum clearance 0 (such as H7/h6) still called a clearance fit, and what separates a transition fit from an interference fit?

Answer: ______________________________________________


**B. Numerical.** Find the smallest and largest clearance of 25 H7/h6, using IT6 = 13 um, IT7 = 21 um and es = 0 for h. Sanity check: what must their difference be?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the zone figure, how far above the top of the H7 hole zone does the p6 shaft zone start? What does that mean for assembly?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: select a fit from H7/g6, H7/h6, H7/js6 and H7/p6 for (a) a sliding bearing that needs at least 5 um and at most 45 um of clearance and (b) a gear that must stay on its shaft with interference in every build and at most 40 um of it. Give the clearance limits that justify your choice, and say what is wrong with the others.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
