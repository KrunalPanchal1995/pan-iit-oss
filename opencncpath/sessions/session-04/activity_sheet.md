# Activity sheet: opencncpath, Session 4: Offset any convex polygon

Name: ____________________   Date: ____________

**Objectives**

- Offset a convex polygon inwards edge by edge and compute the corner shift d / sin(theta / 2), the new edge lengths and the new area.
- Find the distance at which the offset collapses (the inscribed circle) and the distance at which an edge vanishes first.
- Compute the offset robustly as the intersection of shifted half-planes, and show where the edge-by-edge recipe fails.
- Build the rings and a one-plunge-per-layer path for a hexagonal pocket, write its G-code, read it back and check the removed volume.
- Detect the failure cases: a polygon that is not convex, a negative offset, a cutter that does not fit and a stepover that is too large.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A regular hexagon has side 20 mm. Offset it inwards by 3 mm. Find the corner shift, the new side length, the new area and the distance at which the offset collapses.

1. ______________________________  (hint: The interior angle is 120 degrees, so theta / 2 = 60 degrees....)
2. ______________________________  (hint: The corner shift is d / sin 60 = 3 / 0.8660 = 3.4641 mm....)
3. ______________________________  (hint: The new side is 20 - 3 (cot 60 + cot 60) = 20 - 3 x 1.1547 = 16.5359 m...)
4. ______________________________  (hint: The new area is (3 sqrt 3 / 2) x 16.5359^2 = 710.41 mm^2; the formula ...)
5. ______________________________  (hint: The offset collapses at the apothem 20 / (2 tan 30) = 17.3205 mm; for ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a corner of the offset hexagon move by more than the offset distance, and why does the edge-by-edge recipe work for the hexagon but fail for the trapezoid of Figure 1?

Answer: ______________________________________________


**B. Numerical.** A regular octagon has side 10 mm. Offset it inwards by 2 mm. Find the interior angle, how far the corners move, the new side length, the area of the offset octagon and the distance at which it collapses.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right panel of Figure 1 (and in the app, with the trapezoid and d = 6 mm) the dashed outline has a small hook at the top. What went wrong, and how far from the right-hand wall are the two hook corners? What would a cutter of radius 6 mm do if it followed that outline?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a hexagonal recess for a nut, 24 mm across the flats, 5 mm deep, to be cut with a 6 mm cutter. Plan it: the side length, the number of rings for a stepover of 40 percent of the diameter, the layers, the cutting time (feed 300 mm/min, plunge 100 mm/min), and what the nut will see in the corners.

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
