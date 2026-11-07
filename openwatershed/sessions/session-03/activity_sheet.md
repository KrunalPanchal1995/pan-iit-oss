# Activity sheet: openwatershed, Session 3: The unit hydrograph, urbanisation and a detention pond

Name: ____________________   Date: ____________

**Objectives**

- Build a flood hydrograph from rain bursts by discrete convolution with a triangular unit hydrograph.
- Check that the unit hydrograph conserves water and that np.convolve agrees with a loop.
- Quantify how urbanisation (curve number 70 to 90, shorter Tc) changes the peak and its timing.
- Route a flood through a channel (Muskingum) and a detention pond (level-pool routing) and verify water balance.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the 12 km2 catchment, find the unit hydrograph for Tc = 2 h and D = 0.5 h, then the peaks before (CN 70, Tc 2.0 h) and after (CN 90, Tc 1.2 h) urbanisation, and the pond that restores the old peak.

1. ______________________________  (hint: Tp = 0.5/2 + 0.6 * 2.0 = 1.45 h. Qp = 0.208 * 12 / 1.45 = 1.72 m3/s pe...)
2. ______________________________  (hint: Effective rain of the 90 mm storm: 26.3 mm at CN 70 (the first hour of...)
3. ______________________________  (hint: Convolve each burst with the UH and add: before, the peak is 32.3 m3/s...)
4. ______________________________  (hint: After (CN 90, Tc 1.2 h) the peak is 94.6 m3/s at 3.0 h: 2.9 times high...)
5. ______________________________  (hint: Route the urbanised flood through a pond with an orifice that passes 3...)
6. ______________________________  (hint: Checks: the outflow peak is 32.3 m3/s at 4.5 h, the water balance clos...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the flood hydrograph equal the sum of shifted copies of the unit hydrograph, and what two assumptions make that valid?

Answer: ______________________________________________


**B. Numerical.** A catchment has A = 8 km2 and Tc = 1.5 h; the burst length is D = 0.5 h. Find Tp and the UH peak per mm. Check the 0.208 factor.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the urbanisation figure, by how much do the peak and its time change, and which of the two changes (CN or Tc) matters more for the peak?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can build the pond 1 m, 2 m or 3 m deep, with the orifice always passing 32.3 m3/s at the full depth. How does the required volume change, and what does a 1 m deep pond need in surface area? What trade-offs would you weigh?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
