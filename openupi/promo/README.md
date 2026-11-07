# What you are building toward

An animated message flow: a payer app, a switch and two banks pass messages while the ledgers update and the total stays constant. Scene by scene it shows an ordinary payment, a lost reply that is retried with the same id (charged once, not twice), a rapid-fire burst whose sixth payment is held by the velocity rule, and a large payment to a new payee that lights two fraud flags. Your goal over the coming sessions: build the message flow, the ledgers and the fraud checks yourself, then grow them toward reconciliation and crash recovery.

![Target: message flow with ledgers updating and fraud flags lighting up](media/target.gif)

*Target: message flow with ledgers updating and fraud flags lighting up*

![Target still: a rapid-fire burst held by the velocity rule](media/target_still.png)

*Target still: a rapid-fire burst held by the velocity rule*

![A lost reply: the phone retries with the same id](media/scene_retry.png)

*A lost reply: the phone retries with the same id*

![A large payment to a new payee is held: two flags lit](media/scene_held.png)

*A large payment to a new payee is held: two flags lit*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio: probability (Atlas S24)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S24&ex=1)
- [Math Visual Studio: probability distributions (Atlas S25)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S25&ex=1)
