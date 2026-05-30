# Subjective Probability

**Category:** Basic structured analytic technique
**Source:** ATP 2-33.4, *Intelligence Analysis*

## Definition

Subjective probability is a quantitative expression of an analyst's degree of belief in the truth of a statement relative to all other alternative possibilities. It may be presented in text or graphic form (for example, using an [event tree](event-trees.md)).

## When to use

Subjective probabilities express an analyst's overall degree of belief in the truth of a statement, where the total belief is allocated among the possibilities in proportion to how likely each answer or event is to be correct. It is useful for:

- Comparing the perceived likelihood of hypotheses.
- Supporting event tree or matrix analysis by providing quantitative estimates for each event.
- Quantitatively evaluating the value of additional information in shaping the conclusions of an analysis.

Expressing numerical probabilities mitigates the imprecision of probability phrases (such as "very likely" or "improbable") and reduces the potential for analysts to exploit imprecision in favor of their position. Using numbers ensures mathematical rules are followed and forces consideration of a complete set of alternatives, giving the analyst a rational basis to judge whether the probability distribution accurately reflects their beliefs.

> **Distinction from [event mapping](event-mapping.md):** With subjective probability you are *not* determining a timeline for events; you are simply attempting to predict an outcome and applying a percentage of probability to each outcome.

## Subjective probability table

| Term | Score | Range (percent) |
|---|---|---|
| Highly probable | 10 | 91 to 100 |
| Probable | 9 | 81 to 90 |
| Highly likely | 8 | 71 to 80 |
| Likely | 7 | 61 to 70 |
| Possible | 5 to 6 | 41 to 60 |
| Unlikely | 4 | 31 to 40 |
| Highly unlikely | 3 | 21 to 30 |
| Improbable | 2 | 11 to 20 |
| Highly improbable | 1 | 1 to 10 |

When using subjective probability, define a numerical score and range so all personnel involved understand the meaning of the terms.

## Rules

- The probability assigned to a given hypothesis must be within the range of 0.0 (0%) to 1.0 (100%). A probability of 0.0 means the hypothesis is certainly wrong; 1.0 means it is certainly correct.
- The total probability distributed among all hypotheses — which must form a complete, non-overlapping set — must add up to 1.0 (100%).

## Method

1. Identify a complete set of high-level, non-overlapping hypotheses that answer a clearly defined question. Use the technique of defining the issue to ensure the question is clear.
2. Generate simple chains of events or facts for each hypothesis. [Event trees](event-trees.md) and [event mapping](event-mapping.md) aid this step. Each scenario describes one instance of how the associated hypothesis may come to pass.
3. The probability of a given hypothesis is a function of the probabilities of all the scenarios that would support it. The probability of a scenario is a function of all the events within it occurring — that is, the probabilities (percentages) for each option are multiplied throughout the scenario. Two types of probability events must be analyzed:
   - **Mutually exclusive.** The occurrence of one event precludes the others. Either one or another occurs, but not both (e.g., in an election, if one individual wins, another cannot). The total probability for all events must equal 100%.
   - **Conditionally dependent.** The probability of one event depends on whether another has occurred. These are the events within a scenario whose probabilities are multiplied to determine the probability of the end result.

## Tips

- Draw a circle and allocate slices of the "pie," where the relative size of each slice represents how likely the analyst believes that hypothesis is true.
- Assign numbers to each hypothesis according to how strongly it is believed. Determine the subjective probability by dividing the points for each hypothesis by the total of all numbers assigned.
- Determine the amount of money you would be willing to bet on a hypothesis being true, given that you would win $1,000,000 if true; the subjective probability is the ratio of your wager to the total pot (e.g., $1,000 / $1,000,000 = 0.001, or 0.1%).

## Cautions

- Assignments of probability require a complete set of non-overlapping (mutually exclusive) answers, events, scenarios, or courses of action.
- Misuse can feed availability and anchoring biases.
