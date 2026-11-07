# Roadmap: the path to the openloan Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: All-in cost with extra charges

**You will learn:** How fees and insurance paid up front raise the true yearly cost of a loan.

**You will build:** A function returning the effective annual rate of a loan with a percentage fee and a fixed insurance amount, both deducted from the money received.

**Checkpoint (not met by the shipped code):** For 300000 units, 60 months, 10.5 percent reducing, a 1 percent fee and 2000 units of insurance, the all-in effective annual rate is about 11.83 percent (the shipped fee-only value is 11.50 percent).

**Difficulty:** intermediate

## Session 5: Step-up EMI

**You will learn:** Graduated payments that grow each year, and why a lower start costs more in total.

**You will build:** A solver for the first-year EMI when the payment rises 5 percent every 12 months and the balance must end at zero.

**Checkpoint (not met by the shipped code):** For 200000 units at 12 percent over 60 months the first-year EMI is about 4072.70 and total interest about 70051.02 (the shipped fixed-EMI loan has interest 66933.37).

**Difficulty:** intermediate

## Session 6: Prepayment penalty optimiser

**You will learn:** When a fee on early repayment cancels part of the saving.

**You will build:** A search over lump-sum months with a 2 percent penalty on the lump sum.

**Checkpoint (not met by the shipped code):** For a 50000 lump sum on the 200000 loan with a 2 percent penalty, report the net saving by month; the net saving after month 1 is about 31313.54 (the shipped no-penalty value is 32313.54).

**Difficulty:** intermediate

## Session 7: Rate path engine

**You will learn:** A rate that rises in steps and an EMI recomputed at every reset.

**You will build:** A simulator that takes a list of rates and recomputes the EMI every 6 months.

**Checkpoint (not met by the shipped code):** For 100000 units over 36 months starting at 10 percent and rising 0.25 points every 6 months, total interest is about 16831.27 and the final balance is zero (the shipped constant-rate loan costs 16161.87).

**Difficulty:** advanced

## Session 8: Reproduce the Target

**You will learn:** Animating the interest/principal stack, the prepayment kink and the flat-versus-reducing comparison.

**You will build:** A 48-frame animation with three linked panels, saved as a GIF under 3 MB.

**Checkpoint (not met by the shipped code):** A GIF of at most 60 frames and at most 3 MB whose last frame shows a flat 8 percent true rate near 14.5 percent next to 8.0 percent for reducing.

**Difficulty:** advanced

## The final step

Combine the milestones into a loan comparison tool: the user enters offers (reducing or flat, with fees, step-ups or a rate path), and the tool prints the EMI, total cost, effective rate and prepayment savings and draws the Target pictures. If your result looks like the Target animation, open a pull request and tell us how you did it. This is education, never financial advice.
