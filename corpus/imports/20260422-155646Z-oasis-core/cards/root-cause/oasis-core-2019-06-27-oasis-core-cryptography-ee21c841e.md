# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-06-27-oasis-core-cryptography-ee21c841e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `predictable-beacon-entropy`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `entropy-integrity`

## Violated Invariant

- Invariant: Production beacon generation should use the canonical Tendermint beacon path and should not silently rely on deterministic or debug entropy behavior.

## Trust Boundary

- Boundary: `committee-member->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `beacon entropy generation state`

## Impact Pattern

- Primary impact: `predictable-randomness`
- Secondary impact: `consensus-integrity-risk`

## Short Reusable Lesson

- Production beacon generation should use the canonical Tendermint beacon path and should not silently rely on deterministic or debug entropy behavior. In this pattern, the code suggests that deterministic/debug beacon behavior and the canonical Tendermint beacon path were not previously separated as explicitly as they are after the patch. The scheduler also had a more flexible beacon-backend injection point. That supports a hardening narrative, but the provided excerpts do not prove that the older design was exploitable in production. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
