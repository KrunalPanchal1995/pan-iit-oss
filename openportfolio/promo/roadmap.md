# Roadmap: the path to the openportfolio Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Shrink the covariance estimate

**You will learn:** Why a blended estimate (sample covariance pulled towards a simple target) is steadier than the raw one.

**You will build:** A function that mixes the sample covariance with a diagonal matrix, and a test over many seeded histories.

**Checkpoint (not met by the shipped code):** Average true risk of the estimated minimum-variance portfolio at T = 24 (1000 histories, seed 11) of at most 0.0955; the shipped estimate gives 0.0982 and the best possible is 0.0914.

**Difficulty:** intermediate

## Session 5: Stress-test the weights

**You will learn:** How to ask what a portfolio does when every correlation jumps to 0.8, and design for both calm and stress.

**You will build:** A stress function and a small search for weights that satisfy a return floor, a calm-risk cap and a stress-risk cap.

**Checkpoint (not met by the shipped code):** Weights with expected return at least 0.07, calm risk at most 0.10 and stressed risk at most 0.12; the shipped Sharpe-best mix has calm risk 0.1007 and stressed risk 0.1367, and the minimum-variance mix earns only 0.0687.

**Difficulty:** intermediate

## Session 6: Equal risk contributions

**You will learn:** Risk contributions as weight times marginal risk, and why the minimum-variance portfolio hides most of its risk in one asset.

**You will build:** A solver for weights whose assets each carry the same share of the risk.

**Checkpoint (not met by the shipped code):** Each of the four assets contributes 25 percent of the risk within 1 point; the shipped minimum-variance portfolio has asset A carrying 72 percent.

**Difficulty:** advanced

## Session 7: Fat tails

**You will learn:** Why bell-curve returns understate bad years, and how to simulate heavier tails with the same mean and risk.

**You will build:** A simulation with returns of the Student t type, scaled to the same standard deviation.

**Checkpoint (not met by the shipped code):** A loss of more than three standard deviations happens at least three times as often as under the normal model in the same number of seeded years.

**Difficulty:** advanced

## The final step

Combine the milestones: a synthetic portfolio built from shrunk estimates, tested for calm and stress, with equal risk contributions and a tail-risk check, drawn on a frontier cloud like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it. Remember it is a learning model with made-up data, not advice.
