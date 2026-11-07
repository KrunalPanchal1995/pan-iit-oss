# Activity sheet: openkymo, Session 2: Slope to metres per second, and how fast the camera must be

Name: ____________________   Date: ____________

**Objectives**

- Convert a stripe slope in pixels per frame into metres per second using pixel size and frame rate.
- Estimate the slope from image gradients with the structure tensor and read its coherence.
- Relate the slope to the stripe angle, tan(angle) = v.
- Solve the design problem: choose the frame rate (or pixel size) so that the shift per frame stays small enough.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A stripe has the slope 0.8 px/frame. The camera records 200 fps and one pixel covers 1.5 mm. Find the speed in m/s and the angle of the stripe from the time axis.

1. ______________________________  (hint: Pixel size in metres: 1.5 mm / 1000 = 0.0015 m....)
2. ______________________________  (hint: Speed = 0.8 px/frame * 0.0015 m/px * 200 frames/s = 0.24 m/s....)
3. ______________________________  (hint: Angle = arctan(0.8) = 38.7 degrees from the time axis (45 degrees woul...)
4. ______________________________  (hint: Unit check: (px/frame) * (m/px) * (frames/s) = m/s....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the stripe direction equal the direction perpendicular to the main eigenvector, and why is v = -nt / nx with a minus sign?

Answer: ______________________________________________


**B. Numerical.** A stripe has slope 0.45 px/frame, the pixels are 0.8 mm wide and the camera runs at 500 fps. Find the speed in m/s and check the units.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the shift-per-frame graph for 0.5 m/s, at what frame rate does the 2 mm/px curve reach 0.5 px/frame, and what about the 4 mm/px curve? What does a coarser pixel buy you, and what does it cost?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a camera is fixed at 240 fps and the object moves at 0.8 m/s. What is the smallest pixel size (mm/px) that keeps the shift at 0.5 px/frame or less? How long must the line be to hold the stripe for 40 frames at that shift? State the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
