# Coding tasks: Session 4

1. **Easy.** Run `loss_probability(rho)` for rho = -0.8, -0.4, 0, 0.4 and 0.8 and write down how much the loss probability changes for each step of 0.4. Is the change the same size everywhere?
2. **Stretch.** Make the price wobble larger (`p_sd=0.40`) and find, with `implied_rho(p_sd=0.40)` and `loss_probability`, how the loss probability at the demand-line correlation changes. Explain why `implied_rho` raises an error when the demand line explains more than the whole demand spread.
3. **Explain in your own words.** A friend says: "if price and demand are negatively correlated the bakery is hurt, because the correlation is negative". Explain with the picture of the price-demand cloud why that is wrong for the risk of a loss month, and when a negative correlation would not help.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
