# Activity sheet: openstitchdic, Session 1: Why two cameras disagree

Name: ____________________   Date: ____________

**Objectives**

- Explain three ways two cameras can disagree: viewpoint, picture size and shape, and timing.
- Compute how much a sideways distance is squeezed when a camera is turned by an angle.
- Match landmarks between two pictures and find the stretch that brings one onto the other.
- Compute when two frame rates agree and how big the timing gap is in between.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Camera B is turned 40 degrees. A square on the sheet is 100 pixels wide in camera A (looking straight on). How wide does it look sideways in a picture taken at the same scale by B? And how far does a sample moving at 120 px/s travel in the worst timing gap between a 30 fps and a 24 fps camera?

1. ______________________________  (hint: Squeeze = cos 40 = 0.766....)
2. ______________________________  (hint: Width in B at the same scale = 100 * 0.766 = 76.6 pixels....)
3. ______________________________  (hint: Cameras agree every 1/gcd(30, 24) = 1/6 s. Within one cycle the A pict...)
4. ______________________________  (hint: The nearest-B distances for the five A pictures are 0, 8.33, 16.67, 16...)
5. ______________________________  (hint: Distance moved = 120 px/s * (1/60) s = 2.0 px....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can one resize factor not bring camera B's picture onto camera A's picture in this set-up?

Answer: ______________________________________________


**B. Numerical.** A camera is turned 60 degrees to the side. A sideways distance is 100 pixels in a head-on picture. How long does it look? A sample at 90 px/s is paired with a picture 1/60 s away: how far has it moved?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the timing graph (frame rate of B = 24), what is the highest the curve reaches, and what do the red dots tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: camera A runs at 30 fps. Which of these B frame rates keep the worst gap at or below 10 ms: 24, 25, 30, 48, 50, 60? Which would you choose, and what do you give up?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
