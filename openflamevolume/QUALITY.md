# Quality checklist

Every session in this repo is released only when all ten checks hold.

| # | Check (from the master list) | How this repo meets it |
|---|---|---|
| 1 | Learning objectives and prerequisites are stated clearly | Every session README starts with both |
| 2 | Equations, units, assumptions and variable definitions are correct | Section B of each session; reviewed before release |
| 3 | Graphs have labelled axes, units, legends and sensible scales | Every app draws labelled axes with units; every graph is run at the minimum, default and maximum of each control before release |
| 4 | Changing an input correctly updates every dependent output | Every slider is swept and checked for dead controls before release |
| 5 | Numerical results match hand calculations or trusted references | Section E worked example is re-checked by each `checkpoint.py` |
| 6 | Edge cases, zero and extreme inputs are handled | Every control is run at min, default and max and NaN or Infinity is rejected before release |
| 7 | The visual model is clearly distinguished from real behaviour | Every session and app carries the simplified-model notice; Section E compares model with experiment |
| 8 | Worked examples, answers and hints have been reviewed | Section F has a hint and step-by-step solution for each question; independent review before release |
| 9 | Controls are accessible and work on mobile and desktop | Labelled sliders, keyboard focus, responsive layout, light and dark mode |
| 10 | Safety limits and professional-design constraints are stated | Simplified-model notice in every session and app |
