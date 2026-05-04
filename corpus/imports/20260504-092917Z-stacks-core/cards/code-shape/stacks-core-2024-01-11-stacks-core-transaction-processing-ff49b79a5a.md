# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-01-11-stacks-core-transaction-processing-ff49b79a5a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `noncanonical-signing-preimage`

## Code Shape Summary

- The patch corrects the message passed into `RunLoopCommand::Sign` after a validated block proposal. The coordinator previously used serialized full block bytes; it now computes `block_validate_ok.block.header.signature_hash()` and signs that digest. Structural cue: In `stacks-signer/src/runloop.rs`, the patch replaces `message: block_validate_ok.block.serialize_to_vec(),` with `let In `stacks-signer/src/runloop.rs`, the patch changes a sensitive implementation path.

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
