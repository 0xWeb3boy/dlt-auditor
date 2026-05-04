# Code-Shape Card

## Metadata

- ID: `stellar-core-2026-02-03-stellar-core-consensus-a5393933f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-validation-hardening`

## Code Shape Summary

- Queue admission and wrapper transaction paths validated some Soroban constraints but did not consistently call a host-function validator until validateHostFn was introduced and propagated.

## Search Motifs

- canAdd returns pending before validateHostFn
- fee bump validation delegates to inner transaction
- txSOROBAN_INVALID added for host function
- txset phase validity checks invalid transactions explicitly

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Introduce a dedicated host-function validation method, call it at queue admission and txset validation boundaries, and delegate wrapper validation to the inner transaction.

## False Match Warnings

- If host-function validity is fully checked during deserialization, extra guards are defense in depth.
- Do not claim fund loss without a concrete malformed host function effect.
- Protocol-version-gated behavior may intentionally differ across versions.
