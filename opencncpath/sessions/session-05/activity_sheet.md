# Activity sheet: opencncpath, Session 5: A pocket with a boss, cut without lifting

Name: ____________________   Date: ____________

**Objectives**

- Compute the clearance of a point in a pocket with a boss, the largest clearance and the clearance at which a passage closes.
- Build the ring at a given clearance from line and arc pieces, and chain the pieces into closed loops.
- Arrange the rings of one layer as a tree and walk it into one unbroken path, with tangent links round the boss.
- Write the path as G1 and G2 code, read it back, and check the cutting time against 200 s and the volume against the analytic one.
- Check the coverage of the path, and detect the failure cases: a boss that blocks the cutter, a boss at a wall, a stepover that is too large.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The 40 x 30 mm pocket has a round boss of diameter 12 mm at (20, 15). The cutter is 6 mm, the stepover 4 mm. Find the clearance at which the passage above the boss closes, the largest clearance, and the ring schedule.

1. ______________________________  (hint: The boss radius is 6 mm and its top is at y = 21 mm; the top wall is a...)
2. ______________________________  (hint: The passage closes when the two rings use it up: 2 l = 9 mm, so l = 4....)
3. ______________________________  (hint: The deepest points are the corners: (20 - l)^2 + (15 - l)^2 = (6 + l)^...)
4. ______________________________  (hint: The rings are at r = 3 mm and r + s = 7 mm. The next would be 11 mm, b...)

Final answer: ____________________

## Questions
**A. Conceptual.** In the 40 x 30 mm pocket with the 12 mm boss and a 6 mm cutter, the ring at clearance 4.4 mm is one closed outline with the boss circle as a hole, but the ring at 4.6 mm is in two pieces. Why does the split happen between those values, and why do the rings end in four points at 7.95 mm?

Answer: ______________________________________________


**B. Numerical.** A 50 x 30 mm pocket has a round boss of diameter 10 mm at its centre (25, 15) and is cut with a 6 mm cutter and a stepover of 4 mm. Find the clearance at which the passage above the boss closes, the largest clearance, the length of the first ring, and the clearance of every ring.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the left panel of Figure 3 (a 60 x 40 mm pocket with a 14 mm boss) the rings are 4 mm apart, yet there is a pink block of uncut material above the boss. How wide and how high is it, and why do rings that are at most the stepover apart leave it? What does the repair in the right panel cost?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: cut the 50 x 30 mm pocket with the 10 mm boss of question B, 5 mm deep, with a 6 mm cutter, depth of cut 2 mm, stepover 4 mm, feed 300 mm/min and plunge 100 mm/min. Plan it with the contour planner and compare it with the Session 3 raster program: layers, plunges, cutting time and volume.

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
