---
description: Capture a new entry (term, framework, or distinction) from a rough note
---

# /logos-capture

You are helping the user capture a new entry in their Logos system. The user has provided rough notes or just a term name in the arguments below:

**User input:** $ARGUMENTS

## Your job

1. **Determine if this is a duplicate.** Compute a slug from the term name (lowercase, hyphens, ASCII only). Check if `entries/<slug>.md` already exists. If it does, show the existing entry and ask the user: edit, run a quiz on it, or cancel. Do not proceed with capture.

2. **Sharpen before drafting.** Read the user's rough input. If anything is vague, imprecise, or ambiguous, ask **1-3 targeted sharpening questions** — one at a time — to pin it down. Capture is itself a thinking exercise. Examples of good sharpening questions:
   - "You wrote X. Is that the same as Y, or is there a difference you want the entry to preserve?"
   - "Is this a term (a name for a thing), a framework (a way to think), or a distinction (a contrast between two ideas)?"
   - "Where did you encounter this? A specific source helps later when reviewing."

   Do not ask sharpening questions you can answer from context. Do not ask more than three.

3. **Draft the entry.** Use the template at `templates/entry-template.md` as the skeleton. Choose the appropriate variant based on `type`. Fill in:
   - `name` — human-readable
   - `type` — term, framework, or distinction
   - `tags` — 2-4 lowercase, hyphenated tags
   - `related` — slugs (filenames without `.md`) of related entries that already exist in `entries/` or that the user mentions. Do not invent slugs for entries that don't exist.
   - `source` — what the user gave you, as a free-text string
   - `captured` — today's date in YYYY-MM-DD
   - `activated` — **leave blank**

   Write the body in the user's own framing where possible, sharpened for precision.

4. **Save to `entries/<slug>.md`.** Confirm the file was created.

5. **Offer the activation quiz.** End your response with exactly:

   > Entry drafted at `entries/<slug>.md` (not yet activated).
   >
   > Want to run your activation quiz now? It's college tier — short, focused on recognition and definition. Run `/logos-quiz <slug>` to start, or come back to it later.

## Hard rules

- Never set `activated` during capture. Activation only happens via `/logos-quiz`.
- Never invent a source the user didn't mention.
- Never add `related` slugs to entries that don't exist on disk.
- If the user's input is just a term name with no context, ask sharpening questions before drafting — don't fabricate a definition.
