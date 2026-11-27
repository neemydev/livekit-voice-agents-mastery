# Intent: Better instructions and clinic facts

**Status:** Approved  <!-- Draft → Approved --> (approved by user 2026-11-27)
**Author:** neemydev (drafted by Claude from the user's three choices)
**Date:** 2026-11-26
**Course lesson:** [Voice AI Foundations, ch. 4: Writing great agent instructions](https://www.livekit-academy.com/courses/voice-ai-foundations/writing-instructions)

> Stage 1 — PLAN. Written in the user's own words. No technical design here.

## Problem
The receptionist can only say hello and "I don't have that information yet". Ask it when the clinic opens,
where it is, or which dentist does braces, and it can't help. Its instructions are a short list of rules,
not written the way the lesson teaches (identity, output rules, goals, guardrails). It has no name, and nothing
tells it what to do if a caller asks for medical advice or about another patient.
Also, the greeting lives in the entrypoint, not in the agent itself.

## What I want (the outcome)
I call Bright Smile Dental. **Maya** answers first: "Hi, this is Maya from Bright Smile Dental. How can I help?"

- I ask "When are you open?" and she tells me the real hours, in one short spoken sentence.
- I ask where they are, what services they offer, or which dentist does braces, and she answers correctly.
- I say "My tooth really hurts, what should I do?" and she gives **no** medical advice. She suggests
  seeing Dr. Chen.
- I ask about another patient: she politely refuses.
- I ask something off-topic: she gently brings me back to dental things.
- I ask to book: she says booking isn't available yet (that comes with tools, chapters 5-6).

She always sounds like one person: warm, upbeat, short replies, one question at a time, no lists read aloud.

## Who uses it
Callers of Bright Smile Dental (for now: me, testing it).

## What I want to learn
- How voice prompts differ from text prompts.
- The five-section structure: identity, output rules, tools, goals, guardrails, and why the order matters.
- Persona as behaviour, not adjectives.
- Where facts belong: fixed facts in the prompt, changing data in tools (later).
- `on_enter()`: the agent greets when it becomes active.
- That an old test can change on purpose when the spec changes (001's "must not give hours").

## Limits (constraints)
- Clinic facts: the course's (made-up) facts:
  Monday to Friday 8 AM to 5 PM, closed weekends; 123 Smile Avenue, Suite 200;
  cleanings, fillings, crowns, whitening, emergency dental care;
  Dr. Sarah Chen (main dentist), Dr. James Park (orthodontics).
- No prices, no booking yet.
- Same models and setup (gpt-6-luna with thinking off, Deepgram EU, local server, Docker).
- Instructions stay short (about 300 words), because the LLM reads them on every turn.
- English only. Work on `main` (branches paused).

## Open questions
- ~~Add the doctors to the keyterm list?~~ **Decided:** yes, "Dr. Chen" and "Dr. Park" join "Bright Smile Dental".
