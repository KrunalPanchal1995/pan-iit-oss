# Activity sheet: openfractal, Session 3: A fast renderer: smooth colour, area and the limits of floating point

Name: ____________________   Date: ____________

**Objectives**

- Write a vectorised numpy renderer that iterates all pixels at once and counts its own cost.
- Colour pixels smoothly with the continuous escape count nu = n + 1 - log2(ln|z|).
- Validate the renderer against known points and against an area estimated by Monte Carlo sampling, with an error bar.
- Find where double-precision numbers stop being enough for a deep zoom.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For c = 1, find the integer count n with bailout 256, the escape value z_n, and the smooth count nu by hand.

1. ______________________________  (hint: The orbit of c = 1 is 0, 1, 2, 5, 26, 677, so the first value above 25...)
2. ______________________________  (hint: ln 677 = 6.518....)
3. ______________________________  (hint: log2(6.518) = ln 6.518 / ln 2 = 1.8745 / 0.6931 = 2.7044....)
4. ______________________________  (hint: nu = n + 1 - log2(ln|z|) = 5 + 1 - 2.7044 = 3.296....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the continuous count nu remove the colour bands, and why does it hardly depend on the bailout radius?

Answer: ______________________________________________


**B. Numerical.** A Monte Carlo run with N = 400,000 points gives a fraction p = 0.2631 inside the half-box. Give the area and the error bar. How many points would give an error bar half as large?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the cost graph, why is the curve almost a straight line at a shallow zoom and bends over at a deep zoom?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you want a zoom video that stops at width 1e-13 and uses 200 pixel columns. Show that float64 is enough for the last frame and not for width 1e-15. Then propose what to do for the video to go to 1e-30.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
