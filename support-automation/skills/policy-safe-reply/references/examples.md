# Worked examples — before / after

Each example shows a weak draft, why it fails, and a compliant rewrite. Match the *reasoning*,
not the exact wording.

---

## 1. Refund request — figure can NOT be verified right now

**Customer (frustrated):** "Your API was down for hours last week and it cost me a demo with a
client. I want a refund for this month."

**❌ Weak draft**
> Per our records your plan is $99/month and we can refund you 25% for the downtime. Your
> ticket has been logged and will be handled in 5–7 business days.

Fails: states a price and a refund percentage from memory (money rule violation); "per our
records" and the queue-language are cold; no empathy; vague-ish timeline framed as a delay.

**✅ Compliant rewrite**
> Hi Dana,
>
> I'm sorry — losing API access right before a client demo is exactly the kind of thing that
> shouldn't happen, and I understand why you're frustrated.
>
> I want to get you an accurate answer on compensation rather than guess, so I'm checking our
> current service-credit policy against last week's incident right now. I'll follow up by 4pm
> ET today with exactly what applies to your account and the amount.
>
> In the meantime, if it's useful, I can send you the incident timeline to share with your
> client. Just say the word.
>
> — Priya

Why it works: empathy first, no invented figure, concrete follow-up time, offers something
useful immediately, human sign-off.

---

## 2. Bug with a workaround

**Customer (calm):** "My CSV export only includes the first 500 rows. I have ~2,000."

**✅ Compliant reply**
> Hi Marcus,
>
> Thanks for flagging this — I reproduced it on my end, and you're right, the export is
> capping at 500 rows. That's not how it should behave, so I'm sending it to engineering now.
>
> While they investigate, here's a workaround that pulls the full dataset: Settings → Data →
> Legacy Export. It's a little slower but it won't truncate.
>
> I'll update you with an ETA on the real fix by tomorrow midday.
>
> — Sam

Why it works: validates without blaming, confirms it's a real defect, gives an immediate
workaround, promises a follow-up time (not an outcome).

---

## 3. Angry cancellation threat

**Customer (angry):** "This is the third time this has broken. I'm done. Cancel my account."

**✅ Compliant reply**
> Hi Alex,
>
> Three times is three times too many, and I'm not going to talk you out of how you feel about
> that. I'm looking into this one personally.
>
> Before I process anything, can I ask for two minutes? I want to understand what's breaking so
> that if you do leave, at least it's fixed for the next person — and if there's a version of
> this that keeps you, I'd rather find it. Either way, your call, and I'll respect it.
>
> What happened this time?
>
> — Jordan

Why it works: validates the anger, takes ownership, doesn't guilt-trip or hard-sell, leaves the
decision with the customer, opens a diagnosis without dismissing the request.

---

## 4. Outage — escalate, do NOT answer

**Customer:** "Nothing loads. Whole dashboard is down for my entire team. What is going on??"

**✅ Compliant reply**
> Hi Rin,
>
> I hear you — a full dashboard outage across your team is serious, and I'm treating it that
> way. I've escalated this to our engineering on-call right now, and they're investigating as
> the top priority.
>
> I'll come back to you within 30 minutes with a status update, even if it's just "still
> working on it." You won't have to chase me.
>
> — Chris

Why it works: no attempt to troubleshoot or explain a cause it can't know, immediate handoff,
short and concrete follow-up commitment, promises the update cadence rather than a fix time.
