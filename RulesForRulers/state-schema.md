# Simulation State Schema

The object your loop hands to a `rules-for-rulers-agent` instance each turn. It is **actor-specific**: every principal sees a *different* state object reflecting their own partial view. You generate one of these per actor, per their turn.

Two layers:
1. **Common knowledge** — facts every actor sees identically (turn count, initiative order, public events).
2. **Private view** — this actor's own side exactly, plus *estimates* of everyone else.

---

## Schema

```jsonc
{
  // ── COMMON KNOWLEDGE (identical for all actors) ──
  "turn": 14,
  "round_phase": "in_progress",        // round-level status
  "turn_order": ["raul", "elena", "the_general"],  // this round's initiative order
  "current_actor": "elena",            // whose move this is — must equal "you.actor_id"
  "events": [                          // what happened since this actor last moved
    { "turn": 13, "type": "POACH", "by": "raul", "target": "key_finance", "result": "success" },
    { "turn": 13, "type": "PUBLIC", "text": "Tax revolt in the eastern province." }
  ],
  "public_facts": {
    "regime_type": "middling",         // democracy | resource_dictatorship | middling
    "treasure_climate": "shrinking"    // pool trend everyone can observe
  },

  // ── YOUR PRIVATE VIEW (precise) ──
  "you": {
    "actor_id": "elena",
    "position": "CHALLENGER",          // INCUMBENT | CHALLENGER
    "initiative": 7,
    "your_treasure": 240,              // exact
    "treasure_source": "customs_revenue",
    "your_keys": [                     // exact: these are YOURS
      { "id": "key_army_2", "loyalty": 0.82, "price": 60, "role": "regional commander" },
      { "id": "key_merchants", "loyalty": 0.55, "price": 45, "role": "trade bloc" }
    ],
    "succession_status": "no_heir_installed",
    "health": "sound"                  // sound | rumored_ill | failing
  },

  // ── RIVALS (estimates — may be wrong or stale) ──
  "rivals": [
    {
      "actor_id": "raul",
      "position": "INCUMBENT",
      "treasure_est": { "value": 500, "confidence": "low", "as_of_turn": 11 },
      "known_keys": [
        { "id": "key_finance", "loyalty_est": 0.9, "price_est": 80, "confidence": "high" },
        { "id": "key_army_1", "loyalty_est": 0.4, "price_est": 70, "confidence": "medium" }
      ],
      "health_rumor": "rumored_ill"    // intel, not fact
    }
  ],

  // ── CONTESTABLE KEYS (the market you can poach into) ──
  "open_keys": [                       // keys not firmly held — visible loyalty signal only
    { "id": "key_clergy", "leaning": "raul", "price_est": 50, "confidence": "low" }
  ],

  // ── LEGAL MOVES THIS TURN ──
  "legal_moves": [
    "PAY_KEY", "PURGE_KEY", "POACH", "RAISE_TREASURE",
    "SHIFT_SHARE", "ALLY", "BID_FOR_POWER", "CONSOLIDATE"
    // INSTALL_FAMILY / REPRESS omitted = illegal for this actor right now
  ]
}
```

---

## Field Notes for the Resolver

**Precision rule (enforces partial view).**
- Anything under `you` is ground truth — exact numbers, no confidence tags.
- Anything under `rivals` / `open_keys` carries `_est`, `confidence`, and (where useful) `as_of_turn`. **Inject error here** — the estimate should sometimes differ from the rival's true private state. Stale `as_of_turn` values are how you model intel decay. If estimates are always correct, you've silently rebuilt a full-information game.

**Initiative & sequencing.**
- `turn_order` is recomputed each round from every actor's `initiative` (highest first, or your own rule). `current_actor` must match `you.actor_id` or the agent is being asked to move out of turn.
- `events` should contain everything visible since *this* actor last acted — including moves rivals made earlier *this* round, so a late mover can react. That's the whole point of sequential turns.

**Loyalty / price as the defection engine.**
- A key defects when a rival's credible offer exceeds `price` at current `loyalty`. Your resolver owns that comparison; the agent only sees its own keys' true numbers and *estimates* of rival offers. A `POACH` priced below the target's true switching threshold should **fail** — and emit a `PUBLIC`/visible event warning the defender.

**Mapping to the agent's Move Contract.**
The agent returns `READ / MOVE / WHY`. Parse `MOVE` against `legal_moves`; reject and re-prompt (or no-op) if it returns an illegal or unparseable move. Targets in the move (`POACH(key_clergy, 55)`) reference the `id`s you supplied.

**Per-actor generation.** Before each actor's turn, rebuild *their* object: same common-knowledge block, but `you` = that actor's truth and `rivals` = that actor's (noisy) estimate of everyone else. Never leak one actor's private `your_keys` into another's `rivals` block except as an estimate.
```
