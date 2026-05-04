# Root-Cause Card

## Metadata

- ID: `stacks-core-2023-01-24-stacks-core-consensus-17ae4d1671`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-unaware-consensus-lookup`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-consensus-context-validation`

## Violated Invariant

- Invariant: Consensus decisions must validate evidence, fork context, canonical tip monotonicity, and signer sets against the authoritative chain view before accepting results.

## Trust Boundary

- Boundary: Fork-choice, signer, or chain-tip data crosses into consensus validation.

## Attack Surface

- Entrypoint type: `consensus_state_transition`
- Sensitive sink: canonical tip, fork choice, signer set, or block validation decision

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: node-state-divergence

## Short Reusable Lesson

- The patch appears to fix a consensus-relevant fork-awareness bug in burnchain database lookups. Before the change, some paths selected burnchain operations or anchor block commit metadata using identifiers that did not include burnchain fork context. The patch adds burn block hash/header context to operation lookup and changes anchor metadata selection so canonical fork context can be considered before choosing the commit used in affirmation-map construction.
