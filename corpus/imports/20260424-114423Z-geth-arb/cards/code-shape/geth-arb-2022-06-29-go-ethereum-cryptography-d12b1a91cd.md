# Code-Shape Card

## Metadata

- ID: `geth-arb-2022-06-29-go-ethereum-cryptography-d12b1a91cd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation-hardening`

## Code Shape Summary

- Header verification needed explicit handling for mixed proof-of-work/proof-of-stake or merge-boundary batches so terminal difficulty and per-header errors were correct.

## Search Motifs

- header batch spans fork boundary but uses one generic verifier
- terminal difficulty not checked for mixed consensus modes
- per-header error mapping lost around merge transition
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that fork-boundary-consensus-validation was enforced only partially, late, or in one branch while another path could still reach header validity result and invalid-header cache.

## Patch Pattern

- Split verification at the fork boundary, validate terminal total difficulty explicitly, and cache or report invalid transition headers precisely.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
