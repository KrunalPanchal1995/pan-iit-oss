# What you are building toward

Five sorting algorithms receive the same shuffled list and race, drawn as bars, each with live counters for comparisons and moves. The slow methods are still shuffling bars long after merge sort and quicksort have finished. Beside the race, a log-log plot shows how each method's cost grows with the list size. Your goal over the coming sessions: build that race yourself, from the counters of Session 2 to the growth curves of Session 3.

![Target: five algorithms race on the same shuffled list, with live comparison and move counters and a growth plot](media/target.gif)

*Target: five algorithms race on the same shuffled list, with live comparison and move counters and a growth plot*

![Target, one frame: who is finished, who is still shuffling, and the scaling plot](media/target_still.png)

*Target, one frame: who is finished, who is still shuffling, and the scaling plot*

![Why the race is so lopsided: cost against list size on log-log axes, with fitted slopes](media/scaling.png)

*Why the race is so lopsided: cost against list size on log-log axes, with fitted slopes*

![The best method depends on the data pattern: cost of each method on five kinds of input](media/patterns.png)

*The best method depends on the data pattern: cost of each method on five kinds of input*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio (Studio home)](https://krunalpanchal1995.github.io/studio/)
