# Activity sheet: opensculpt, Session 1: A shape is a function: signed distance

Name: ____________________   Date: ____________

**Objectives**

- Explain what a signed distance is and why negative means inside.
- Compute the signed distance from a point to a circle and to a box.
- Join two shapes with min and read the result from a picture and from a graph.
- Estimate an area by counting grid cells that are inside.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A circle has radius 1 and centre (0, 0). A box has centre (2, 0) and half-sizes (0.5, 0.5). Find the signed distance of the point (1.2, 0.3) to each shape and to their union.

1. ______________________________  (hint: Circle: |p - c| = sqrt(1.2^2 + 0.3^2) = sqrt(1.53) = 1.237, so d = 1.2...)
2. ______________________________  (hint: Box: q = (|1.2 - 2| - 0.5, |0.3 - 0| - 0.5) = (0.3, -0.2)....)
3. ______________________________  (hint: The positive parts of q are (0.3, 0), of length 0.3, and max(qx, qy) =...)
4. ______________________________  (hint: Union = min(0.237, 0.300) = 0.237. The value is positive, so the point...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we use a negative value for points inside a shape, rather than just the distance to the surface?

Answer: ______________________________________________


**B. Numerical.** A circle of radius 2 is centred at the origin. What is the signed distance of the point (3, 4)? Is it inside?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the profile graph along the line y = 0.3, between which x values is the union inside? Why are there two separate stretches?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the box has centre (2, 0) and half-sizes (0.5, 0.5). Choose the radius of a circle centred at the origin so that the two shapes just touch, then so that they overlap. Which is better for a real part and why?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
