# Root-Cause Card

## Metadata

- ID: `optimism-2022-09-08-optimism-transaction-processing-1c787aa01d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Untrusted block-gossip messages must be large enough to contain a 65-byte signature and a non-empty payload, and the payload bytes should be authenticated as coming from the configured sequencer before deeper decoding or bookkeeping.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: correctness-or-hardening
- Secondary impact: signature-or-domain-confusion

## Short Reusable Lesson

- Untrusted block-gossip messages must be large enough to contain a 65-byte signature and a non-empty payload, and the payload bytes should be authenticated as coming from the configured sequencer before deeper decoding or bookkeeping. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
