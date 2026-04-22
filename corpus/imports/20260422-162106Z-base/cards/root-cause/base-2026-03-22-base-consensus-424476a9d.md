# Root-Cause Card

## Metadata

- ID: `base-2026-03-22-base-consensus-424476a9d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: A sequencer should only be activated when the execution engine already exposes a real initialized unsafe head, and the requested starting head should match that engine state. Starting from an uninitialized or inconsistent tip weakens consensus-safety assumptions by allowing sequencing to begin from state the engine has not established as current.

## Trust Boundary

- Boundary: `on-chain dispute or engine state->off-chain consensus actor`

## Attack Surface

- Entrypoint type: `challenge-orchestration`
- Sensitive sink: `selection of the external head consumed by derivation or verifier logic`

## Impact Pattern

- Primary impact: `consensus-integrity-risk`
- Secondary impact: `none`

## Short Reusable Lesson

- A sequencer should only be activated when the execution engine already exposes a real initialized unsafe head, and the requested starting head should match that engine state. Starting from an uninitialized or inconsistent tip weakens consensus-safety assumptions by allowing sequencing to begin from state the engine has not established as current. The start path accepted activation without enforcing that the execution engine had a valid current unsafe head, and the supplied `unsafe_head` was not shown to influence the transition before activation. Separate state-publication timing also meant callers could continue observing a zero unsafe head until later engine activity, making invalid start requests more likely. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
