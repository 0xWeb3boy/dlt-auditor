# Code-Shape Card

## Metadata

- ID: `geth-arb-2021-07-22-go-ethereum-transaction-processing-97aacd9b35`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-balance-validation`

## Code Shape Summary

- The EIP-1559 balance precheck considered fee exposure but omitted transferred value, so affordability validation was incomplete before execution.

## Search Motifs

- fee precheck omits value transfer amount
- new transaction type has separate affordability formula
- balance check differs between legacy and upgraded transaction rules
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that fee-and-value-balance-precheck was enforced only partially, late, or in one branch while another path could still reach gas purchase, balance debit, and value transfer.

## Patch Pattern

- Include transferred value in the transaction-type-specific balance check before buying gas or entering execution.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
