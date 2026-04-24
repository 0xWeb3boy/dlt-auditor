# Root-Cause Card

## Metadata

- ID: `optimism-2025-02-21-optimism-transaction-processing-7ceadae456`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: Block-signing code should derive signatures from one canonical message format with correctly sized fields, including a 32-byte payload hash and a bounded chain ID.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: signature-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Block-signing code should derive signatures from one canonical message format with correctly sized fields, including a 32-byte payload hash and a bounded chain ID. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
