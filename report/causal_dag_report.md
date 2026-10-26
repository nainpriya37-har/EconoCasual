# EconoCausal Causal DAG

## Treatment
`discount`

## Outcome
`purchased`

## Assumed confounders
- `age`
- `past_purchases`
- `loyalty_score`
- `previous_spend`

## Directed edges
- age -> discount
- age -> purchased
- past_purchases -> discount
- past_purchases -> purchased
- loyalty_score -> discount
- loyalty_score -> purchased
- previous_spend -> discount
- previous_spend -> purchased
- discount -> purchased

## Model setup
DoWhy constructed the causal model and ran the
effect-identification step.

## Important limitations
This graph represents an assumed causal structure.
It does not estimate the treatment effect or prove
that all confounders have been observed.

The graph is a starting hypothesis for simulated data.
Real observational data requires domain knowledge
and further validation.
