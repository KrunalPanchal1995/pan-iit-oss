# Activity sheet: opencncpath, Session 1: A cutter follows a path

Name: ____________________   Date: ____________

**Objectives**

- Explain that a CNC machine moves a cutter, like a plotter moves a pen, along a list of coordinates.
- Find the path of the cutter centre for a square pocket: the wall moved inwards by one cutter radius.
- Predict the island that one lap leaves in the middle.
- Compute the time of a path from its length and the feed.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 20 mm square pocket is cut with a 4 mm cutter at 120 mm/min. Find the centre path, its length, the time for one lap and the island that is left.

1. ______________________________  (hint: Radius r = 4 / 2 = 2 mm. The centre path is the square from 2 mm to 18...)
2. ______________________________  (hint: Length L = 4 * 16 = 64 mm....)
3. ______________________________  (hint: Time = 64 / 120 min = 0.533 min = 32.0 s....)
4. ______________________________  (hint: Island side = 20 - 4 * 2 = 12 mm: a 12 mm square in the middle is not ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the cutter centre have to follow a path one radius inside the wall, and why does one lap of a big pocket leave an island?

Answer: ______________________________________________


**B. Numerical.** A 30 mm square pocket is cut with a 6 mm cutter at 150 mm/min. Find the path length, the time for one lap and the island side.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the time graph the curve falls as the feed rises. If the feed is halved from 120 to 60 mm/min for the 64 mm path, what happens to the time? What does the curve shape say?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose a cutter diameter and a feed to clear a 20 mm pocket in one lap, with no island, in under 20 s. Is there a limit on the feed?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
