# Root-Cause Card

## Metadata

- ID: `base-2026-04-16-base-consensus-6381f6a83`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-fallback-liveness`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `lifecycle-continuity`

## Violated Invariant

- Invariant: The challenger should keep progressing a dispute when one proving/submission path fails, but the provided evidence only establishes an internal fallback/liveness expectation for the challenger process, not a demonstrated protocol-level security invariant breach.

## Trust Boundary

- Boundary: `on-chain dispute or engine state->off-chain consensus actor`

## Attack Surface

- Entrypoint type: `challenge-orchestration`
- Sensitive sink: `admission of work into shared network, RPC, or challenger resources`

## Impact Pattern

- Primary impact: `availability`
- Secondary impact: `none`

## Short Reusable Lesson

- The challenger should keep progressing a dispute when one proving/submission path fails, but the provided evidence only establishes an internal fallback/liveness expectation for the challenger process, not a demonstrated protocol-level security invariant breach. The pending-proof and retry logic for TEE proofs did not preserve or use the information needed to transition from a failed TEE submission into the alternate ZK path. This is a state-management and retry-flow defect, not evidence of a cryptographic or consensus flaw. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
