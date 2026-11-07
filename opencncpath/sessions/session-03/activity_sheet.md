# Activity sheet: opencncpath, Session 3: Pocketing strategies and a simulation that checks them

Name: ____________________   Date: ____________

**Objectives**

- Compare raster (zigzag) and contour-parallel pocketing by length, time and leftover.
- Compute the ridge height left by a ball-end cutter, h = r - sqrt(r^2 - (s/2)^2), and check it on a simulated height-map.
- Use MRR = width x depth x feed and chip load f_z = F / (N z), and check the removed volume by simulation.
- Detect the failure cases: inside corners, uncut strips, a wrong-direction offset and a cutter too big for a slot.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A ball-end cutter of radius 3 mm makes parallel passes 2 mm apart. Find the ridge height, then the largest stepover that keeps the ridge at 0.05 mm or less, and check by simulation.

1. ______________________________  (hint: h = 3 - sqrt(3^2 - 1^2) = 3 - sqrt(8) = 3 - 2.828 = 0.1716 mm....)
2. ______________________________  (hint: For h = 0.05 mm: s = 2 sqrt(2 * 3 * 0.05 - 0.05^2) = 2 sqrt(0.2975) = ...)
3. ______________________________  (hint: Use s = 1.0 mm (a convenient value below the limit): h = 3 - sqrt(9 - ...)
4. ______________________________  (hint: The height-map simulation of 5 passes at 2 mm gives 0.1716 mm (and 0.0...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a bigger stepover finish a job faster but leave more material behind? Why does the contour-parallel path with stepover equal to the diameter still leave cusps in the corners?

Answer: ______________________________________________


**B. Numerical.** A cutter has 2 teeth, runs at 8000 rev/min and feeds at 480 mm/min. Find the chip load. Then find the MRR for a_e = 3 mm, a_p = 1.5 mm and F = 400 mm/min.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the corner-leftover graph, read the leftover area for a cutter radius of 3 mm and of 5 mm. What happens when the radius doubles, and what does that say about choosing a cutter?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a ball-end cutter of radius 4 mm must finish a 40 x 30 mm face with a ridge of at most 0.02 mm at 600 mm/min. Choose a stepover (rounded down to 0.01 mm), count the lines and estimate the time. Lines run along the 40 mm side, plus 30 mm of side-steps in total.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
