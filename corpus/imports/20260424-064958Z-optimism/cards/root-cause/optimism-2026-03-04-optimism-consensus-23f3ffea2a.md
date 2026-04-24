# Root-Cause Card

## Metadata

- ID: `optimism-2026-03-04-optimism-consensus-23f3ffea2a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: After the execution layer has been observed as synced, a later SYNCING response to forkchoice updates must be treated as loss of state alignment rather than as normal progress; the node should re-discover the execution layer's actual chain state before continuing.

## Trust Boundary

- Boundary: remote or persisted chain signal -> consensus state machine

## Attack Surface

- Entrypoint type: forkchoice/finality state-transition path
- Sensitive sink: safe/finalized head promotion, rewind, or consensus checkpoint update

## Impact Pattern

- Primary impact: state-divergence
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- After the execution layer has been observed as synced, a later SYNCING response to forkchoice updates must be treated as loss of state alignment rather than as normal progress; the node should re-discover the execution layer's actual chain state before continuing. Similar bugs appear when forkchoice/finality state-transition path code treats partially checked input as authoritative and lets it reach safe/finalized head promotion, rewind, or consensus checkpoint update. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
