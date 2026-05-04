# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-05-06-stacks-core-transaction-processing-81e451bf7b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-context-binding`

## Code Shape Summary

- The patch changes signer message handling so messages carry a reward_cycle and consumers check or unwrap that reward-cycle-scoped structure before processing payloads. The evidence supports a protocol-context binding improvement, but it does not establish an exploitable vulnerability or concrete security impact.

## Search Motifs

- Motif 1: manual construction bypasses constructor checks
- Motif 2: noncanonical preimage or type accepted at signing or validation boundary
- Motif 3: VM or transaction error interpreted inconsistently

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Centralize canonical construction or validation and reject ambiguous representations before using them in sensitive logic.

## False Match Warnings

- The constructor may be used only with trusted constants.
- The changed path may improve diagnostics without changing acceptance behavior.
