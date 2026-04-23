# Root-Cause Card

## Metadata

- ID: `go-ethereum-2016-11-24-go-ethereum-storage-12d654a6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-revert-bug`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-validation`

## Violated Invariant

- Invariant: Ethereum state transition execution must produce the same post-state across clients for EIP158 empty-account clearing, including when execution uses Snapshot/Revert. If an empty account is touched by a zero-value balance operation, that touch state must be recorded and reverted consistently.

## Trust Boundary

- Boundary: Peer-supplied synchronization or protocol data crossing into local validation and scheduling logic.

## Attack Surface

- Entrypoint type: `p2p message`
- Sensitive sink: `consensus-visible state transition or journal replay`

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `state-integrity`

## Short Reusable Lesson

- The patch is best classified as a likely consensus-security fix in go-ethereum core/state.
