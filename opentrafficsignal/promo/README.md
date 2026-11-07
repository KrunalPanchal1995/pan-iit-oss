# What you are building toward

Two identical four-way junctions face the same rush hour: north-south busy, then east-west busy, then north-south again. On the left a fixed timetable, made for the average demand, lets queues pile up whenever the busy direction changes; its average delay climbs to about 22 seconds per car. On the right an adaptive controller watches the queues and moves the green to where the cars are; its average delay stays near 7 seconds. Live counters show cars waiting and the delay so far. Your goal over the coming sessions: build the adaptive half yourself, then give it time-varying demand, turning phases and a second junction.

![Target: fixed timing (left) versus adaptive timing (right) through a swinging rush hour](media/target.gif)

*Target: fixed timing (left) versus adaptive timing (right) through a swinging rush hour*

![Target still: live counters and the running average delay of both junctions](media/target_still.png)

*Target still: live counters and the running average delay of both junctions*

![Numerics course figure: a Burgers shock, the simplest model of the sharp front of a traffic jam](media/burgers_shock.png)

*Numerics course figure: a Burgers shock, the simplest model of the sharp front of a traffic jam*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio: numerical PDEs, the next step towards traffic-flow models (Atlas S34)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S34&ex=1)
