# Root-Cause Card

## Metadata

- ID: `optimism-2025-05-19-optimism-consensus-6cf0b3a613`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-forkchoice-promotion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `path-confinement`

## Violated Invariant

- Invariant: When EL sync completes, startup forkchoice should derive safe and finalized from protocol-backed chain context, not blindly relabel the current unsafe head or first inserted payload as safe/finalized.

## Trust Boundary

- Boundary: artifact/archive input -> host filesystem

## Attack Surface

- Entrypoint type: archive-extraction or file-materialization path
- Sensitive sink: filesystem write outside the intended extraction or artifact directory

## Impact Pattern

- Primary impact: incorrect-forkchoice-classification
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- When EL sync completes, startup forkchoice should derive safe and finalized from protocol-backed chain context, not blindly relabel the current unsafe head or first inserted payload as safe/finalized. Similar bugs appear when archive-extraction or file-materialization path code treats partially checked input as authoritative and lets it reach filesystem write outside the intended extraction or artifact directory. The reusable fix is to enforce path-confinement at the boundary and fail closed before state, privilege, or consensus-visible output changes.
