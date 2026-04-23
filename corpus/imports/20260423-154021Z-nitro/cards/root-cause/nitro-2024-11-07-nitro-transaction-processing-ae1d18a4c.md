# Root-Cause Card

## Metadata

- ID: `nitro-2024-11-07-nitro-transaction-processing-ae1d18a4c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-proof-generation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `proof-boundary-state-selection`

## Violated Invariant

- Invariant: Boundary-case proof generation should return the concrete fallback state to use, not a boolean hint that leaves callers free to guess the correct finished state.

## Trust Boundary

- Boundary: `virtual challenge range metadata->proof or hash generation`

## Attack Surface

- Entrypoint type: `proof-generation-or-challenge-response`
- Sensitive sink: `building challenge proofs or hashes for boundary cases`

## Impact Pattern

- Primary impact: `challenge-proof-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Boundary-case proof generation should return the concrete fallback state to use, not a boolean hint that leaves callers free to guess the correct finished state. The evidence supports a correctness fix in BoLD challenge handling: virtual-range block challenges were previously handled with a boolean shortcut that did not provide the concrete finished state to use, and the commit message says this could lead to looking up a block index for which no real block existed and producing incorrect inclusion proofs. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
