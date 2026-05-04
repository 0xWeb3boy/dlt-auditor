# Code-Shape Card

## Metadata

- ID: `stacks-core-2020-10-01-stacks-core-storage-1ba4efc836`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `delegated-stacking-validation`

## Code Shape Summary

- The patch adjusts PoX delegated stacking behavior: the VM special handler no longer requires the returned stacker to equal the transaction sender, and the delegated stacking path adds a balance check against `stacker`. This is plausibly security relevant, but the evidence more directly supports a delegation semantics and validation correctness fix than a confirmed vulnerability fix.

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
