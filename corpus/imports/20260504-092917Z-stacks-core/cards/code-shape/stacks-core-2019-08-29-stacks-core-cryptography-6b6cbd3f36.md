# Code-Shape Card

## Metadata

- ID: `stacks-core-2019-08-29-stacks-core-cryptography-6b6cbd3f36`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-constructor-validation`

## Code Shape Summary

- The patch changes Clarity VM list type/value construction to rely on constructor-validated ListTypeData/TypeSignature metadata instead of direct field construction and repeated downstream size checks. This supports an invariant-cleanup or hardening interpretation around MAX_VALUE_SIZE, but the supplied evidence does not establish an externally reachable vulnerability or concrete security impact.

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
