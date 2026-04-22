# Root-Cause Card

## Metadata

- ID: `base-2025-12-29-base-storage-55893ad15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-policy-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `policy-gating`

## Violated Invariant

- Invariant: The proposer should only attempt to create a dispute game when its configured game type matches the live `respectedGameType()` published by `AnchorStateRegistry`. The supplied evidence shows enforcement of that invariant in the proposer, but does not show downstream onchain consequences if it is violated.

## Trust Boundary

- Boundary: `chain state, checkpoint, or persistent storage input->proposer or validator logic`

## Attack Surface

- Entrypoint type: `checkpoint-or-state-validation`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `protocol-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- The proposer should only attempt to create a dispute game when its configured game type matches the live `respectedGameType()` published by `AnchorStateRegistry`. The supplied evidence shows enforcement of that invariant in the proposer, but does not show downstream onchain consequences if it is violated. The proposer creation path relied on locally configured game type without consulting the live onchain policy source that defines the currently respected type. The surrounding config and ABI plumbing also did not yet expose the registry query needed to enforce that check in this path. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
