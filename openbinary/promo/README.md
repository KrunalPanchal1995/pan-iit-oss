# What you are building toward

An 8-bit adder runs three sums. Switches flip, and the carry ripples one full adder at a time, lighting its wire as it goes: 45 + 19 = 64 sends a carry through six stages, 127 + 1 sends a carry through seven stages and raises the overflow flag (the answer wraps to -128), and -1 + 1 = 0 sends a carry through all eight stages. A chart shows how the worst-case delay grows with the number of bits (17 gate delays at 8 bits). Your goal over the coming sessions: build that adder yourself, then make it fast.

![Target: an 8-bit adder where the carry ripples through eight full adders](media/target.gif)

*Target: an 8-bit adder where the carry ripples through eight full adders*

![Target, one frame: carry wires lit part-way along the chain, with the delay chart](media/target_still.png)

*Target, one frame: carry wires lit part-way along the chain, with the delay chart*

![How long the carry chain is for every pair of 8-bit numbers: usually short, but the worst case sets the speed](media/carry_chains.png)

*How long the carry chain is for every pair of 8-bit numbers: usually short, but the worst case sets the speed*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio (open the Studio and explore the Atlas)](https://krunalpanchal1995.github.io/studio/)
