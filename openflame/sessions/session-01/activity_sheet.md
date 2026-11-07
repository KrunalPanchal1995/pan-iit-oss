# Activity sheet: openflame, Session 1: A flame video is a stack of pictures

Name: ____________________   Date: ____________

**Objectives**

- Explain that a video is a stack of frames and each frame is a grid of brightness numbers.
- Turn a frame into a flame mask with a brightness threshold.
- Measure the flame height in pixels and convert it to millimetres with a scale.
- Explain why the chosen threshold changes the measured height.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A ruler beside the flame is 100 px long in the picture and is 50 mm long. The flame in a frame has its half-brightness tip 60 px above the burner row. What height do you measure at threshold 0.5, in pixels and in millimetres? What would threshold 0.2 have given?

1. ______________________________  (hint: Scale = 50 mm / 100 px = 0.5 mm per pixel....)
2. ______________________________  (hint: At threshold 0.5 the tip is at z = h + s ln(1) = 60 px, so the mask re...)
3. ______________________________  (hint: Height = 60 px x 0.5 mm/px = 30 mm....)
4. ______________________________  (hint: At threshold 0.2 (s = 2 px) the tip is at 60 + 2 ln 4 = 60 + 2.77 = 62...)
5. ______________________________  (hint: Sanity check: a candle flame is a few centimetres tall, so 30 mm is pl...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a lower threshold give a taller flame? Is there a 'correct' threshold?

Answer: ______________________________________________


**B. Numerical.** A ruler is 150 px long in the picture and 60 mm long in reality. A flame is 72 px tall at threshold 0.5. How tall is it in mm, and what is the uncertainty if the tip is uncertain by +-1 px?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the threshold figure, what height is measured at thresholds 0.2 and 0.8, and how many millimetres apart are they at 0.5 mm/px?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for a flame with true height 60 px and softness 2 px, which thresholds measure the height within +-1 px of the truth? Pick one and justify your choice, with noise in mind.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
