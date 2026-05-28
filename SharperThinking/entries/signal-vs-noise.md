---
name: Signal vs. Noise
type: distinction
tags: [epistemics, information, interpretation]
related: [first-principles, second-order-thinking]
source: "User-supplied prompt; concept traces to Shannon's information theory (1948); popularized for general audiences by Nate Silver, The Signal and the Noise (2012)"
captured: 2026-05-28
activated:
---

## Side A
**Signal** — the part of an information stream that actually carries the pattern
you care about. It's the underlying truth, trend, or relationship the data is
trying to tell you about.

## Side B
**Noise** — everything else in the stream: random variation, measurement error,
irrelevant content, coincidence. It looks like information but doesn't reflect
the underlying reality you're trying to read.

## The distinction
The line between signal and noise is **domain-dependent and goal-dependent** —
the same data point can be signal in one context and noise in another. A
spike in daily website traffic is signal if you're tracking whether a launch
worked, but noise if you're estimating long-run user growth.

Drawing the line prevents two failure modes:
- **Treating noise as signal** — chasing patterns that aren't real (overfitting,
  conspiracy thinking, reacting to one bad quarter).
- **Treating signal as noise** — dismissing real information as randomness
  because it doesn't fit your model (early warning signs ignored, weak signals
  of regime change written off).

The discipline is asking, before you interpret: *what would I expect this stream
to look like if there were no signal?* If you can't picture pure noise in this
domain, you can't recognize signal.

## Examples
1. Stock prices over a single day are mostly noise; multi-year fundamentals
   are mostly signal. Day traders and long-term investors disagree about
   the same data because they're filtering for different signals.
2. A single user complaint is usually noise. The same complaint from ten
   independent users in a week is probably signal. The threshold depends on
   your user base — for a 100-user product, three complaints is signal;
   for a million-user product, three is noise.
3. In medical testing: a slightly elevated lab value in an otherwise healthy
   patient is usually noise (false positive at the tails of a distribution);
   the same value plus a symptom plus a risk factor is signal.

## Notes
The trap: **more data does not mean more signal.** Often it means more noise,
and the signal-to-noise ratio gets *worse* as the stream gets larger. The
skill is not "look at more" — it's "know what you're filtering for, and what
pure noise would look like in this domain."

Related failure mode: signal/noise is not a property of the data alone — it's
the data crossed with a question. Asking the wrong question turns signal into
noise. "Is this stock going up tomorrow?" makes nearly all of the price stream
noise; "is this company well-managed?" makes some of the same stream signal.
Define the question first, then sort the stream.
