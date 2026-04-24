# Root-Cause Card

## Metadata

- ID: `optimism-2026-01-27-optimism-transaction-processing-b8a91297ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integer-truncation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `domain-separation`

## Violated Invariant

- Invariant: When chain IDs are used for matching or derived-field computation, code should preserve the full value or reject out-of-range inputs rather than silently truncating them to 64 bits.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- When chain IDs are used for matching or derived-field computation, code should preserve the full value or reject out-of-range inputs rather than silently truncating them to 64 bits. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce domain-separation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
