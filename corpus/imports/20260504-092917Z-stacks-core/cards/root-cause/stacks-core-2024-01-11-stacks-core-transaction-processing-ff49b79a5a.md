# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-01-11-stacks-core-transaction-processing-ff49b79a5a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `noncanonical-signing-preimage`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-input-validation`

## Violated Invariant

- Invariant: Protocol inputs must be normalized and validated in their canonical context before they influence state, signatures, or consensus outcomes.

## Trust Boundary

- Boundary: Externally supplied transaction, block proposal, or signer payload crosses into transaction validation.

## Attack Surface

- Entrypoint type: `transaction_or_block_proposal`
- Sensitive sink: transaction acceptance, block proposal evaluation, or signer coordination state

## Impact Pattern

- Primary impact: signature-integrity
- Secondary impact: protocol-correctness

## Short Reusable Lesson

- The patch corrects the message passed into `RunLoopCommand::Sign` after a validated block proposal. The coordinator previously used serialized full block bytes; it now computes `block_validate_ok.block.header.signature_hash()` and signs that digest. Structural cue: In `stacks-signer/src/runloop.rs`, the patch replaces `message: block_validate_ok.block.serialize_to_vec(),` with `let In `stacks-signer/src/runloop.rs`, the patch changes a sensitive implementation path.
