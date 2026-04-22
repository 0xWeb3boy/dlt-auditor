# Root-Cause Card

## Metadata

- ID: `base-2025-12-29-base-storage-d9350fcc9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-precondition-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `policy-gating`

## Violated Invariant

- Invariant: The proposer should only create dispute games when its configured `game_type` matches the live `respectedGameType` returned by `AnchorStateRegistry`. The patch enforces that invariant in proposer-side logic, but the provided evidence does not show what happens on-chain if the proposer fails to do so.

## Trust Boundary

- Boundary: `chain state, checkpoint, or persistent storage input->proposer or validator logic`

## Attack Surface

- Entrypoint type: `checkpoint-or-state-validation`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- The proposer should only create dispute games when its configured `game_type` matches the live `respectedGameType` returned by `AnchorStateRegistry`. The patch enforces that invariant in proposer-side logic, but the provided evidence does not show what happens on-chain if the proposer fails to do so. The proposer relied on local `game_type` configuration without a runtime check against the authoritative on-chain registry state, so it could continue attempting game creation even when local configuration no longer matched the currently respected type. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
