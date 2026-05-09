# Code-Shape Card

## Metadata

- ID: `nibiru-2024-05-17-nibiru-transaction-processing-dbbcfd60`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-validation`

## Code Shape Summary

- A state-changing transaction handler added an explicit basic-validation gate before converting and executing a foreign-runtime transaction.

## Search Motifs

- msg.ValidateBasic missing at keeper entrypoint
- conversion to geth/core transaction before validation
- tests added for invalid intrinsic gas or malformed transaction
- handler assumes ante or client validation already ran

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Fail fast at the keeper boundary with basic message validation before context unwrap, transaction conversion, gas checks, or execution.

## False Match Warnings

- Do not flag if an earlier mandatory ante path always validates the same message
- Formatting-only gas changes are not evidence
- Chain ID changes need replay evidence before being treated as security
