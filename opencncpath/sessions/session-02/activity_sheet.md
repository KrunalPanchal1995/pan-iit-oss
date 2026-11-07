# Activity sheet: opencncpath, Session 2: G-code, offsets and arcs

Name: ____________________   Date: ____________

**Objectives**

- Write and parse G0 and G1 moves with X, Y, Z in mm and F in mm/min.
- Offset a rectangle inwards (pocket) and outwards (profile) by the cutter radius and verify the sizes numerically.
- Build G2/G3 arcs with I, J centre offsets and verify the endpoint and the radius.
- Plan a rectangular pocket: stepover, lines, layers and time.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Design: clear a 40 x 30 mm pocket, 5 mm deep, with a 6 mm cutter and a 2 mm depth of cut per pass at 300 mm/min. Choose the stepover and the number of passes and estimate the time.

1. ______________________________  (hint: The centre must cover (40 - 6) x (30 - 6) = 34 x 24 mm, so lines run 3...)
2. ______________________________  (hint: Choose the stepover at most 75 percent of the diameter: 4.5 mm. Lines ...)
3. ______________________________  (hint: Layers N = ceil(5 / 2) = 3, each 5 / 3 = 1.667 mm deep....)
4. ______________________________  (hint: One layer: 7 * 34 + 24 = 262 mm; three layers: 786 mm....)
5. ______________________________  (hint: Cutting time = 786 / 300 min = 2.62 min = 157.2 s. Plunge: 5.5 mm / 10...)
6. ______________________________  (hint: Parsing our own G-code gives the same 160.5 s for cutting and plunging...)

Final answer: ____________________

## Questions
**A. Conceptual.** The same start (10, 0) and end (0, 10) with I-10 J0 are used for G3 and for G2. Do they give the same arc? Why does the centre not change?

Answer: ______________________________________________


**B. Numerical.** An arc starts at (20, 0), ends at (0, 20) and is written G3 X0 Y20 I-20 J0. Find the centre, check the end radius and find the arc length.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the time-against-stepover graph, the time is 282.9 s at a stepover of 2 mm and 119.7 s at 6 mm. Why does the curve fall quickly at first and then flatten? Why can the stepover not exceed 6 mm?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: repeat the plan with an 8 mm cutter (stepover at most 75 percent of D, depth of cut 2 mm, 300 mm/min, plunge 100 mm/min). How many lines, how much cutting length and what time? Is it faster than the 6 mm cutter, and what is the catch?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
