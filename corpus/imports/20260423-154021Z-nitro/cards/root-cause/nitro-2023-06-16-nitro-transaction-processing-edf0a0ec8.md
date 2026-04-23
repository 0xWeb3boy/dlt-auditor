# Root-Cause Card

## Metadata

- ID: `nitro-2023-06-16-nitro-transaction-processing-edf0a0ec8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-challenge-metadata`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authoritative-challenge-metadata`

## Violated Invariant

- Invariant: Challenge edge construction should use the challenged assertion's own creation metadata, not metadata inherited from an adjacent or previous assertion.

## Trust Boundary

- Boundary: `assertion metadata->challenge edge construction`

## Attack Surface

- Entrypoint type: `challenge-construction-or-dispute-initialization`
- Sensitive sink: `building commitments or edges for a challenge`

## Impact Pattern

- Primary impact: `challenge-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Challenge edge construction should use the challenged assertion's own creation metadata, not metadata inherited from an adjacent or previous assertion. The evidence supports a challenge-initiation correctness bug, not a clearly established vulnerability. The patch changes level-zero edge construction to use the challenged assertion's `creationInfo` instead of previously using `prevCreationInfo` for commitment inputs, and it threads that metadata back to the caller. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
