# Validation Card

## Metadata

- ID: `snarkvm-2023-10-07-snarkvm-transaction-processing-289b9edad`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-validation`

## What Confirmed The Issue

- Authorization construction changed from `From` to `TryFrom`.
- Human-readable deserialization now calls the checked constructor and rejects mismatched counts.

## What Could Have Invalidated It

- The constructor is unreachable from untrusted input.
- A stronger signature-binding check independently couples every request to every transition.

## Severity Guidance

- Expected impact band: authorization_and_state_integrity_hardening
- Expected severity band: medium_or_low

## False-Positive Cautions

- Binary deserialization or canonical parsing already rejects mismatched vectors before construction.
- The object is never used until another mandatory verifier checks the same invariant.
