# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-06-28-stacks-core-storage-4fd033f283`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-fork-context-reward-set-lookup`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-consensus-context-validation`

## Violated Invariant

- Invariant: Consensus decisions must validate evidence, fork context, canonical tip monotonicity, and signer sets against the authoritative chain view before accepting results.

## Trust Boundary

- Boundary: Persisted or peer-derived chain state crosses into storage-backed validation.

## Attack Surface

- Entrypoint type: `state_database_lookup_or_update`
- Sensitive sink: canonical state database, cached validation state, or durable index

## Impact Pattern

- Primary impact: liveness
- Secondary impact: consensus-divergence-risk

## Short Reusable Lesson

- Likely security-relevant consensus/liveness fix in the Nakamoto coordinator. The patch changes reward-cycle handling to use or justify the correct fork context for reward-set lookup, with comments explaining why the canonical tip is safe at the end of prepare phase and why local-best use is only safe for the first Nakamoto reward set. The evidence supports a canonical fork-context lookup issue, but does not prove exploitability, invalid block acceptance, or a malformed transaction panic.
