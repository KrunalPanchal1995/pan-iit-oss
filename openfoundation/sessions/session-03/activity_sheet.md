# Activity sheet: openfoundation, Session 3: How far does it sink, and how fast?

Name: ____________________   Date: ____________

**Objectives**

- Compute the immediate elastic settlement of a footing with an influence factor.
- Compute the final settlement of a clay layer and the time curve of consolidation, and check U = 50 and 90 percent against the series.
- Compare the 2:1 spread with Boussinesq stress, and validate the numerics against closed forms.
- Choose footing sizes for a small building so that settlement is even.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 2 m square rigid footing carries 150 kPa on soil with E = 20 MPa and nu = 0.3. Below it a 4 m clay layer (Cc 0.3, e0 0.9) has sigma0 = 100 kPa and dsigma = 50 kPa at mid-layer, c_v = 1.5 m2/year and drains at top and bottom (H_dr = 2 m). Find the elastic settlement, the consolidation settlement, the total, and the times for 50 and 90 percent consolidation.

1. ______________________________  (hint: Elastic: s = 150 * 2 * (1 - 0.3^2) * 0.82 / 20000 = 150 * 2 * 0.91 * 0...)
2. ______________________________  (hint: Consolidation: s_c = 4 * 0.3 / 1.9 * log10(150 / 100) = 0.6316 * 0.176...)
3. ______________________________  (hint: Total = 11.2 + 111.2 = 122.4 mm....)
4. ______________________________  (hint: Time: t = T_v H_dr^2 / c_v. For 50 percent, T_v = 0.197: t50 = 0.197 *...)
5. ______________________________  (hint: For 90 percent, T_v = 0.848: t90 = 0.848 * 4 / 1.5 = 2.26 years. Doubl...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does consolidation take years in clay, and why does halving the drainage path make it much faster?

Answer: ______________________________________________


**B. Numerical.** A clay layer 3 m thick (Cc 0.3, e0 0.9) has sigma0 = 100 kPa and dsigma = 50 kPa at mid-layer. Find the final consolidation settlement.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the consolidation curve with c_v = 1.5 m2/year and H_dr = 2 m, at what times are 50 and 90 percent of the settlement reached?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: two columns carry 250 kN and 1200 kN. The bearing-only footings are 1.40 m and 3.00 m (settlements 6.7 and 14.9 mm). With E = 20 MPa and nu = 0.3, find the smallest width for the big footing in 0.05 m steps so that the two settlements differ by at most 3.5 mm. What does it cost?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
