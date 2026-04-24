# Root-Cause Card

## Metadata

- ID: `optimism-2025-05-19-optimism-consensus-dfafb52630`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-forkchoice-initialization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `path-confinement`

## Violated Invariant

- Invariant: During sync startup, the node should not mark an L2 block as "safe" or "finalized" solely because EL sync reached a transition point; those labels should be derived from chain context. The provided evidence supports that the new path derives startup forkchoice by walking backward from the unsafe head and using L1-origin distance instead of blindly promoting the current unsafe block.

## Trust Boundary

- Boundary: artifact/archive input -> host filesystem

## Attack Surface

- Entrypoint type: archive-extraction or file-materialization path
- Sensitive sink: filesystem write outside the intended extraction or artifact directory

## Impact Pattern

- Primary impact: incorrect-forkchoice-state
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- During sync startup, the node should not mark an L2 block as "safe" or "finalized" solely because EL sync reached a transition point; those labels should be derived from chain context. The provided evidence supports that the new path derives startup forkchoice by walking backward from the unsafe head and using L1-origin distance instead of blindly promoting the current unsafe block. Similar bugs appear when archive-extraction or file-materialization path code treats partially checked input as authoritative and lets it reach filesystem write outside the intended extraction or artifact directory. The reusable fix is to enforce path-confinement.
