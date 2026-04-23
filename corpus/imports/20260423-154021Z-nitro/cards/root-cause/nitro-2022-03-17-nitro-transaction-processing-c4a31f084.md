# Root-Cause Card

## Metadata

- ID: `nitro-2022-03-17-nitro-transaction-processing-c4a31f084`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reorg-state-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-chain-binding`

## Violated Invariant

- Invariant: Recovered validator progress should stay bound to the canonical chain identity, not just a block height, and should fail closed across same-height reorgs.

## Trust Boundary

- Boundary: `stored progress state->resumed validator or staking logic`

## Attack Surface

- Entrypoint type: `validator-recovery-or-reorg-handling`
- Sensitive sink: `continuing validation or staking from restored chain progress`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Recovered validator progress should stay bound to the canonical chain identity, not just a block height, and should fail closed across same-height reorgs. This patch is best supported as security hardening in validator reorg handling. The code adds and checks validated block hashes so the validator does not keep operating from a stale validated height after the canonical chain changes at the same block number. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
