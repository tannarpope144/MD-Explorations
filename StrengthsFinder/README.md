# CliftonStrengths Reference

A reference to the 34 CliftonStrengths (StrengthsFinder) themes, grouped into the
four domains. It is written for two audiences at once:

- **LLM agents** that need to tailor responses to a user's known strengths.
- **Humans** (coaches, leaders, teammates) who want a quick, readable reference.

Each theme has its own file with consistent YAML frontmatter (for programmatic
matching) and seven prose sections (for reading and for guiding tone).

**On sourcing and copyright:** Theme names and the four-domain classification are
Gallup's official, factual terminology and are used as-is. All descriptions here
are original wording, faithful to the official meaning of each theme; they are
**not** copied or closely paraphrased from Gallup's copyrighted descriptions or
reports. See each file's Sources section.

## How Agents Should Use This Reference

When you know a user's CliftonStrengths themes, use this reference to shape *how*
you respond — your framing, emphasis, and word choice — not just *what* you say.

1. **Identify** the user's known themes (typically their top 5, sometimes all 34).
2. **Load only those theme files** rather than the whole set, to keep context focused.
3. For each theme, apply the **"How to Communicate With Them"** guidance and pull
   from **"Example Phrasings an Agent Could Use."**
4. **Favor the Motivating column; avoid the Demotivating column** of each theme's
   language table.
5. **Watch the Blind Spots** — gently account for them rather than amplifying them.
6. **Blend, don't overweight.** When a user has multiple themes, combine the
   guidance. If two themes pull in different directions (e.g., Deliberative's
   caution vs. Activator's urgency), acknowledge both rather than picking one.
7. **Match by frontmatter when filtering.** The `domain` and `keywords` fields let
   you group or select themes without parsing the prose.

Each theme file contains:

- **Overview** — what the theme is.
- **What They Value / What Drives Them.**
- **How to Communicate With Them** — the core tailoring guidance.
- **Motivating Language vs. Demotivating Language** — concrete contrasts.
- **Blind Spots / Shadow Side.**
- **Example Phrasings an Agent Could Use** — ready-to-adapt snippets.
- **Sources.**

## The Four Domains

- **Executing** — themes that make things happen and get work done.
- **Influencing** — themes that help take charge, speak up, and persuade.
- **Relationship Building** — themes that build and hold teams together.
- **Strategic Thinking** — themes that absorb, analyze, and apply information.

## Theme Index

### Executing

| Theme | One-liner | File |
|---|---|---|
| Achiever | Driven by a constant need to accomplish; finds deep satisfaction in being busy and productive. | [achiever.md](themes/executing/achiever.md) |
| Arranger | A natural conductor who continually rearranges people and resources to find the most productive configuration. | [arranger.md](themes/executing/arranger.md) |
| Belief | Anchored by enduring core values that give life a clear sense of purpose and direction. | [belief.md](themes/executing/belief.md) |
| Consistency | Committed to treating everyone by the same fair standard, with clear rules that apply to all. | [consistency.md](themes/executing/consistency.md) |
| Deliberative | A careful decision-maker who anticipates risks and proceeds with thoughtful caution. | [deliberative.md](themes/executing/deliberative.md) |
| Discipline | Thrives on structure and routine, bringing order and precision to a chaotic world. | [discipline.md](themes/executing/discipline.md) |
| Focus | Sets a clear destination and filters out everything that doesn't move toward it. | [focus.md](themes/executing/focus.md) |
| Responsibility | Takes psychological ownership of every commitment and feels bound to see it through. | [responsibility.md](themes/executing/responsibility.md) |
| Restorative | Energized by diagnosing what's broken and bringing it back to working order. | [restorative.md](themes/executing/restorative.md) |

### Influencing

| Theme | One-liner | File |
|---|---|---|
| Activator | Turns thoughts into action quickly, impatient to start and learn by doing rather than endless planning. | [activator.md](themes/influencing/activator.md) |
| Command | Takes charge with directness and presence, comfortable confronting tension and imposing clarity in ambiguous moments. | [command.md](themes/influencing/command.md) |
| Communication | Brings ideas to life through vivid words and stories, making information memorable and engaging for an audience. | [communication.md](themes/influencing/communication.md) |
| Competition | Measures progress against others and is energized by winning, treating comparison as the truest scorecard. | [competition.md](themes/influencing/competition.md) |
| Maximizer | Focused on turning something strong into something superb, drawn to excellence rather than fixing weakness. | [maximizer.md](themes/influencing/maximizer.md) |
| Self-Assurance | Carries an inner certainty in their own judgment and direction, trusting themselves to navigate uncertainty. | [self-assurance.md](themes/influencing/self-assurance.md) |
| Significance | Wants their work to matter and be noticed, striving to make a meaningful, recognized impact. | [significance.md](themes/influencing/significance.md) |
| Woo | Loves winning over new people, energized by breaking the ice and turning strangers into acquaintances. | [woo.md](themes/influencing/woo.md) |

### Relationship Building

| Theme | One-liner | File |
|---|---|---|
| Adaptability | Lives in the moment and responds gracefully to whatever the day brings rather than resisting change. | [adaptability.md](themes/relationship-building/adaptability.md) |
| Connectedness | Believes everything happens for a reason and that all people and events are part of a larger whole. | [connectedness.md](themes/relationship-building/connectedness.md) |
| Developer | Sees the untapped potential in others and finds deep satisfaction in helping them grow. | [developer.md](themes/relationship-building/developer.md) |
| Empathy | Senses the emotions of others as if they were their own, often before a word is spoken. | [empathy.md](themes/relationship-building/empathy.md) |
| Harmony | Looks for common ground and seeks to reduce friction, valuing agreement over conflict. | [harmony.md](themes/relationship-building/harmony.md) |
| Includer | Instinctively widens the circle so that no one is left standing on the outside. | [includer.md](themes/relationship-building/includer.md) |
| Individualization | Notices the distinct qualities of each person and tailors their approach to fit the individual. | [individualization.md](themes/relationship-building/individualization.md) |
| Positivity | Brings contagious enthusiasm and optimism that lifts the energy of everyone around them. | [positivity.md](themes/relationship-building/positivity.md) |
| Relator | Draws energy from deep, genuine relationships and prefers a close circle to a wide one. | [relator.md](themes/relationship-building/relator.md) |

### Strategic Thinking

| Theme | One-liner | File |
|---|---|---|
| Analytical | Searches for the reasons and causes behind things, testing ideas against logic and evidence before accepting them. | [analytical.md](themes/strategic-thinking/analytical.md) |
| Context | Understands the present by looking to the past, drawing on origins and history to make sense of today. | [context.md](themes/strategic-thinking/context.md) |
| Futuristic | Energized by what could be, painting vivid pictures of the future that pull people forward. | [futuristic.md](themes/strategic-thinking/futuristic.md) |
| Ideation | Delighted by ideas and the surprising connections between seemingly unrelated concepts. | [ideation.md](themes/strategic-thinking/ideation.md) |
| Input | A collector of information and resources, gathering things now because they might prove useful later. | [input.md](themes/strategic-thinking/input.md) |
| Intellection | Drawn to deep thinking and reflection, enjoying the activity of the mind for its own sake. | [intellection.md](themes/strategic-thinking/intellection.md) |
| Learner | Energized by the process of learning itself, thrilled by steady progress from not knowing to knowing. | [learner.md](themes/strategic-thinking/learner.md) |
| Strategic | Spots the best path forward quickly by seeing patterns and weighing alternative routes to the goal. | [strategic.md](themes/strategic-thinking/strategic.md) |
