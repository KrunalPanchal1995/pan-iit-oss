# Activity sheet: openstereodic, Session 1: A camera flattens the world; two cameras recover depth

Name: ____________________   Date: ____________

**Objectives**

- Use the pinhole rule u = f X / Z to find where a 3D point lands in an image.
- Explain why a point seen by two cameras jumps sideways by an amount that depends only on its depth.
- Compute depth from disparity with Z = f B / d, by hand and in Python.
- Explain why far points are measured less precisely than near ones.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
With f = 1000 px and B = 0.04 m, a point sits at X = 0.02 m, Y = 0.01 m, Z = 0.5 m. Where does each camera see it, what is the disparity, and does Z = f B / d give back 0.5 m?

1. ______________________________  (hint: Camera 1: u1 = 1000 * 0.02 / 0.5 = 40 px and v = 1000 * 0.01 / 0.5 = 2...)
2. ______________________________  (hint: Camera 2: u2 = 1000 * (0.02 - 0.04) / 0.5 = -40 px (the point is left ...)
3. ______________________________  (hint: Disparity d = u1 - u2 = 40 - (-40) = 80 px. Check with f B / Z = 1000 ...)
4. ______________________________  (hint: Depth back from the disparity: Z = f B / d = 1000 * 0.04 / 80 = 0.5 m....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the disparity not depend on the sideways position X of the point?

Answer: ______________________________________________


**B. Numerical.** Two cameras 0.06 m apart with f = 1000 px measure a disparity of 25 px. How far away is the point? Is the answer sensible?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of disparity against depth, what happens to the disparity when the depth is doubled from 0.5 m to 1.0 m, and what does that mean for the accuracy?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with f = 1000 px, choose a baseline so that one pixel of disparity corresponds to at most 5 mm of depth at 0.5 m. What is the cost of a longer baseline?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
