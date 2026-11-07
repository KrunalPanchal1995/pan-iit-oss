# Activity sheet: openbreakeven, Session 3: Break-even under mix, steps, uncertainty and time

Name: ____________________   Date: ____________

**Objectives**

- Find the break-even of a business with several products, and show how the sales mix moves it.
- Find every zero crossing of a profit curve with step-fixed costs by scanning numerically.
- Use a seeded Monte Carlo simulation to get the loss probability and profit distribution, and validate it against a formula.
- Rank inputs by their effect on profit, compute payback and net present value, and report when no break-even exists.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The bakery sells loaves (price 3.50, variable cost 1.40) and cakes (price 18, variable cost 9) in the unit mix 80 percent loaves and 20 percent cakes, with F = 1200 dollars. Find the break-even, then find the profit crossings if a second oven (900 dollars more) is needed above 700 loaves, and the chance of a loss when only demand is random (mean 800, standard deviation 150, loaves only).

1. ______________________________  (hint: Weighted margin = 0.8 * 2.10 + 0.2 * 9.00 = 1.68 + 1.80 = 3.48 dollars...)
2. ______________________________  (hint: Break-even units = 1200 / 3.48 = 344.8, which is about 275.9 loaves an...)
3. ______________________________  (hint: Step costs, loaves only: with one oven (fixed 1200) the break-even is ...)
4. ______________________________  (hint: Loss chance with only demand random: q* = 571.43, so z = (571.43 - 800...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can the break-even of a two-product business go down even though the fixed cost and all prices stay the same?

Answer: ______________________________________________


**B. Numerical.** A 6000 dollar oven and fit-out earns 480 dollars of cash each month. Find the simple payback month, the discounted payback month at 12 percent a year, and the NPV over 24 months at that rate.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the Monte Carlo histogram, which part of the picture is the loss probability, and what would happen to it if demand became more uncertain (a larger standard deviation) with the same mean?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the owner may choose the 600, 800 or 1000 loaf oven and a price from 3.00 to 5.00 dollars in 0.25 steps. A choice passes if the loss probability is at most 5 percent, the payback at most 12 months and the margin of safety at least 20 percent. Use `evaluate` to recommend one choice and explain the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
