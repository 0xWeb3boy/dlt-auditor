# Root-Cause Card

## Metadata

- ID: `reth-2023-04-12-reth-consensus-e87960ea8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-state-consistency`

## Violated Invariant

- Invariant: Forkchoice restoration should only proceed when the node can reconcile the supplied forkchoice state with local execution state. If the finalized block is unknown, or the finalized block is known but the referenced head is still missing locally, the engine should transition to pipeline/syncing instead of continuing on a partially restored tree.

## Trust Boundary

- Boundary: consensus layer signal -> execution client forkchoice/block state

## Attack Surface

- Entrypoint type: engine-api/forkchoice-handler
- Sensitive sink: canonical head, payload status, or pipeline scheduling

## Impact Pattern

- Primary impact: forkchoice-state-integrity
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- Forkchoice restoration should only proceed when the node can reconcile the supplied forkchoice state with local execution state. If the finalized block is unknown, or the finalized block is known but the referenced head is still missing locally, the engine should transition to pipeline/syncing instead of continuing on a partially restored tree.
