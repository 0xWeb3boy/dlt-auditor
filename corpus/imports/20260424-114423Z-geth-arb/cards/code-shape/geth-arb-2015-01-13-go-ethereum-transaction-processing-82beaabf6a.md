# Code-Shape Card

## Metadata

- ID: `geth-arb-2015-01-13-go-ethereum-transaction-processing-82beaabf6a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-mismatch`

## Code Shape Summary

- Consensus-sensitive edge cases used inconsistent local error propagation or boundary constants, so equivalent nodes could disagree about whether execution should continue or which relatives are valid.

## Search Motifs

- nested execution error overwrites outer transaction result
- uncle/ancestor/fork boundary uses an off-by-one constant
- debug or alternate execution path handles a consensus error differently
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that consensus-rule-consistency was enforced only partially, late, or in one branch while another path could still reach consensus validity decision and state-root calculation.

## Patch Pattern

- Scope nested errors locally, align boundary constants with the protocol rule, and add regression coverage for the consensus edge case.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
