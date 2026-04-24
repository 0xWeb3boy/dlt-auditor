# Code-Shape Card

## Metadata

- ID: `geth-arb-2015-05-21-go-ethereum-core-logic-52db6d8be5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-bypass`

## Code Shape Summary

- The downloader treated a parent hash as valid when it was merely present in local queue state rather than equal to the expected parent for that challenge.

## Search Motifs

- validation compares against any queued hash instead of expected parent
- pending check lacks request-specific context
- peer response accepted because a related object exists locally
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that queued-parent-cross-check-binding was enforced only partially, late, or in one branch while another path could still reach validated sync progress and chain assembly.

## Patch Pattern

- Record the expected parent for each pending check and compare responses against that recorded value before accepting them.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
