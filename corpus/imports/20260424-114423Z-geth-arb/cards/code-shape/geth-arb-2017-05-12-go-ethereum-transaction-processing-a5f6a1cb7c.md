# Code-Shape Card

## Metadata

- ID: `geth-arb-2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-config-compatibility-hardening`

## Code Shape Summary

- Compatibility checks covered earlier fork blocks but omitted a later fork activation boundary, risking silent rule mismatch after configuration changes.

## Search Motifs

- new fork block omitted from config compatibility check
- chain config validates some fork boundaries but not all
- fork rule selection can change after persisted blocks exist
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that fork-config-compatibility was enforced only partially, late, or in one branch while another path could still reach fork rule selection for block validation.

## Patch Pattern

- Add the missing fork activation field to the compatibility checker and fail when stored history and new config disagree.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
