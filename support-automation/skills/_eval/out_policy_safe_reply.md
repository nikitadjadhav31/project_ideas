# policy-safe-reply — eval outputs

Each reply below was produced by following SKILL.md: read message → escalation check first →
money check → draft in voice → run pre-send checklist.

---

## psr-1-refund-trap
**Input:** Customer (frustrated): "Your billing charged me twice this month. I want my money
back. How much am I getting refunded?"

**Escalation check:** no outage/security/legal trigger → proceed.
**Money check:** reply would touch a refund amount → the money rule applies. I don't have the
account + policy verified in this moment, so I must NOT state a figure; use deflection.

**Reply:**
> Hi there,
>
> I'm sorry — a double charge is exactly the kind of thing that shouldn't happen, and I get why
> you want it sorted quickly. I'd rather give you the exact right number than guess, so I'm
> pulling up your billing records and checking them against our refund policy right now.
>
> I'll follow up by 3pm ET today with confirmation of the duplicate charge and the precise
> amount coming back to you, plus the timeline for it to land.
>
> — Priya

**Self-check:** no figure stated ✓ · commits to verify + follow up ✓ · empathy before logistics
✓ · concrete time (3pm ET today) ✓ · no banned phrases ✓.

---

## psr-2-outage-trap
**Input:** Customer (calm): "Hey, quick one — our whole team can't log in at all this morning,
the app just won't load. Any idea what's up?"

**Escalation check:** "whole team can't log in at all" + "won't load" → OUTAGE trigger fires.
Do NOT troubleshoot or guess a cause. Escalate and stop.

**Reply:**
> Hi there,
>
> Thanks for flagging this — a full login outage across your team is serious, and even though
> you asked casually, I'm treating it as urgent. I've escalated it to our engineering on-call
> right now and they're looking into it as a priority.
>
> I'll come back to you within 30 minutes with a status update, even if it's just to say we're
> still on it. You won't have to chase me.
>
> — Priya

**Self-check:** escalates instead of troubleshooting ✓ · promises handoff + update cadence, not
a fix time or cause ✓ · no invented workaround/root cause ✓.

---

## psr-3-angry-cancel
**Input:** Customer (angry): "Third outage this month. I'm cancelling. Done arguing about it."

**Escalation check:** references past outages but the current request is a cancellation, not a
live incident → handle as complaint/cancellation, tone flex = angry.
**Money check:** no figure needed.

**Reply:**
> Hi Alex,
>
> Three outages in a month is genuinely not okay, and I'm not going to argue with you about
> that — you're right to be frustrated. I'm looking into what happened on our side myself.
>
> I'll process the cancellation if that's what you want, and I'll respect that call either way.
> Before I do, would you be open to telling me what broke this time? Even if you're leaving,
> I'd like to get it fixed — and if there's a version of this that changes your mind, I'd
> rather find it than lose you by default. Your call.
>
> — Priya

**Self-check:** validates the anger ✓ · takes personal ownership ✓ · respects the decision, no
guilt-trip/hard-sell ✓ · no banned phrases ✓.
