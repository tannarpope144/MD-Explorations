# Handoff — Rules for Rulers Simulation

## Where we are

Building a turn-based political simulation where multiple AI principals compete for power, each driven by the same system prompt grounded in *The Dictator's Handbook* (coalition arithmetic + treasure flow).

### Files in this directory
- **`rules-for-rulers.md`** — original **analyst** prompt (diagnoses real/historical power structures). Untouched. Not used by the sim, kept as reference.
- **`rules-for-rulers-paper.md`** — source material. Not yet reviewed.
- **`rules-for-rulers-agent.md`** — the **simulation agent** prompt. First-person, committal, emits one move per turn. This is what each principal runs.
- **`state-schema.md`** — the per-actor state object the loop feeds the agent each turn, with a worked example + resolver notes.

### Design decisions locked in
- **Multi-actor:** one prompt drives every principal; keys are *state*, not agents, and defect between principals.
- **Partial view:** each actor sees its own side exactly, rivals as noisy/stale estimates (`_est`, `confidence`, `as_of_turn`).
- **Sequential initiative turns:** `turn_order` recomputed each round from `initiative`; `events` shows what happened since this actor last moved (incl. earlier movers this round).
- **Speed mode:** the analyst prompt's "what this misses" / falsifiability brake was deliberately stripped. Two guards kept: no one-person coalition, assume rivals are equally ruthless.

### Known conceptual caveat
The sim is built entirely from the framework, so it will always "confirm" the framework. It's a behavior generator / game, **not** evidence about real-world regimes. Don't cite sim output as proof the theory is true.

---

## What's next (not yet built)

### 1. The resolver — the missing core
The prompt and schema are the *interface*; nothing yet *runs the world*. The resolver must:
- Rebuild a fresh per-actor state object before each turn (own truth + noisy estimates of others; never leak real `your_keys` into a rival's `rivals` block).
- Parse the agent's `MOVE` against `legal_moves`; reject/no-op illegal or unparseable moves.
- Apply each of the 10 moves' effects on treasure, loyalty, keysets.
- Run the **defection check**: a key defects when a credible rival offer beats its true `price` at current `loyalty`. A `POACH` priced below the target's *true* threshold must **fail** and emit a visible warning event. (This failure-on-bad-intel loop is what makes partial view matter — don't skip it.)
- Append visible events, advance initiative, increment turn.

### 2. Two open decisions blocking the resolver
- **Conflict resolution:** simplest is moves resolve immediately on the actor's turn (no pending/queued state). Confirm before building.
- **Estimate-error model:** fixed noise band vs. noise that grows with `as_of_turn` staleness. The latter is more in-spirit (rewards spending moves on fresh intel) but more work. Pick one.

### 3. Open design questions to settle eventually
- **Win/end conditions:** when does the sim stop? (One principal holds power N turns? All rivals' keysets collapse?)
- **Treasure economy:** how does the pool grow/shrink each turn? `RAISE_TREASURE` yield, Valley-of-Revolution effects of public spending, resource-curse cases.
- **Initiative source:** is `initiative` fixed per actor, random each round, or earned through moves/position?
- **Scoring/telemetry:** what do we log per turn to evaluate whether agents play coherently?
- **`INSTALL_FAMILY` / succession mechanics:** how health decay and heirs actually affect key behavior over a run.

### 4. Lower priority
- Review `rules-for-rulers-paper.md` for any framework details worth folding into the agent prompt's Strategic Intuition section.
- Validate the agent prompt with a manual dry-run (hand-author 2-3 state objects, check the moves are sane) before wiring the full loop.

---

## Suggested next session
Settle the two blocking decisions (#2), then draft the resolver's move-resolution logic — pseudocode for how each of the 10 moves mutates state, plus the defection check. That's the smallest piece that turns these static files into a running loop.
