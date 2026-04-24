# Code-Shape Card

## Metadata

- ID: `geth-arb-2015-05-15-go-ethereum-core-logic-5c1a7b965c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-validation-bypass`

## Code Shape Summary

- Downloader validation accepted a returned block hash without proving it matched the expected parent relationship for the pending cross-check.

## Search Motifs

- pending validation cleared by matching hash alone
- cross-check state lacks expected parent binding
- peer response advances sync without satisfying requested relation
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that peer-response-parent-binding was enforced only partially, late, or in one branch while another path could still reach clearing pending cross-check state and continuing sync.

## Patch Pattern

- Bind pending validation state to the expected parent or context and clear it only when the response matches that exact tuple.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
