# Activity sheet: openkymo, Session 1: One line of pixels, stacked over time

Name: ____________________   Date: ____________

**Objectives**

- Build a kymograph by stacking one row of pixels from every video frame.
- Explain why a moving object makes a slanted stripe and a still object a vertical one.
- Measure the stripe slope in pixels per frame, from two points and from a line fit.
- Read the same motion from a position-against-time graph and from the kymograph.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
In the video of Figure 1 the blob moves at 0.6 px/frame from x0 = 8. Find its column in frames 10 and 30 and the slope between them.

1. ______________________________  (hint: Position in frame 10: 8 + 0.6 * 10 = 14....)
2. ______________________________  (hint: Position in frame 30: 8 + 0.6 * 30 = 26....)
3. ______________________________  (hint: Slope = (26 - 14) / (30 - 10) = 12 / 20 = 0.6 px/frame....)
4. ______________________________  (hint: Sanity check: over 39 frames the blob moves 0.6 * 39 = 23.4 pixels, fr...)

Final answer: ____________________

## Questions
**A. Conceptual.** What does a vertical stripe mean? What would a bright horizontal stripe (the same row lit up in a single frame) mean?

Answer: ______________________________________________


**B. Numerical.** A blob is at column 5 in frame 0 and at column 41 in frame 30. Find its speed in px/frame and check that it stays on a 64 pixel line for 40 frames.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the app, how does the stripe look in the kymograph and how does the line look in the position graph when you triple the speed from 0.3 to 0.9? Which picture shows the faster object as steeper?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the line is 64 pixels long, the blob starts at pixel 8, and you want it to stay on the line for at least 30 frames while you measure. Which speeds are allowed? Why would a very slow blob also be a poor choice?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
