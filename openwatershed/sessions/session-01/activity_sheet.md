# Activity sheet: openwatershed, Session 1: From rain to river

Name: ____________________   Date: ____________

**Objectives**

- Split rain into water that soaks in and water that runs off.
- Convert a run-off depth rate (mm/h) over an area (km2) into a flow in m3/s.
- Explain how a catchment delays and smooths the water on its way to the river.
- Explain why a short intense storm can give a taller flood than a long gentle one with the same rain depth.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
60 mm of rain falls in 1 h on a 20 km2 catchment with f = 5 mm/h and K = 2 h. Find the run-off flow and the river peak. Then do the same for 60 mm in 6 h.

1. ______________________________  (hint: Intensity i = 60 / 1 = 60 mm/h. Run-off rate = 60 - 5 = 55 mm/h....)
2. ______________________________  (hint: Flow q = 55 * 20 / 3.6 = 305.6 m3/s....)
3. ______________________________  (hint: Peak = 305.6 * (1 - exp(-1/2)) = 305.6 * 0.3935 = 120.2 m3/s....)
4. ______________________________  (hint: 6 h storm: i = 10 mm/h, run-off rate 5 mm/h, q = 5 * 20 / 3.6 = 27.78 ...)
5. ______________________________  (hint: Peak = 27.78 * (1 - exp(-6/2)) = 27.78 * 0.9502 = 26.4 m3/s....)
6. ______________________________  (hint: Run-off volumes: 55 mm gives 1100 thousand m3 and 30 mm gives 600 thou...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can a storm with less total rain sometimes cause a bigger flood than a storm with more rain?

Answer: ______________________________________________


**B. Numerical.** 60 mm of rain falls in 2 h on the 20 km2 catchment (f = 5 mm/h, K = 2 h). Find the river peak and check the units.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of peak against duration (rain fixed at 60 mm), what do the 0 and 10 mm/h curves tell you at D = 6 h? What happens as D gets small?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: land use changes can raise f from 5 to 10 mm/h (for example, more open soil and trees). For the 60 mm, 1 h storm, does that bring the peak below 100 m3/s? What else would you change, and what do you assume?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
