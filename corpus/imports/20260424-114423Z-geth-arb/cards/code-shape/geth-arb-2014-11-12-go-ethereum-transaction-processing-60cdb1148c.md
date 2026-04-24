# Code-Shape Card

## Metadata

- ID: `geth-arb-2014-11-12-go-ethereum-transaction-processing-60cdb1148c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-commitment-validation`

## Code Shape Summary

- Block-processing code had the transaction commitment comparison present but disabled, allowing body data to approach execution without proving it matched the header commitment.

## Search Motifs

- block body accepted without recomputing the transaction/root commitment
- header commitment compared only in tests or dead code
- block import reaches execution before body/header consistency is checked
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that block-body-commitment-integrity was enforced only partially, late, or in one branch while another path could still reach block acceptance, transaction execution, and canonical state update.

## Patch Pattern

- Restore the body-root recomputation and equality check at block import, and fail closed before execution when the header commitment does not match.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
