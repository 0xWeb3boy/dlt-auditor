# Code-Shape Card

## Metadata

- ID: `bor-2015-03-20-bor-cryptography-d8fe8f60e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- The patch in vendored Ethash code replaces several assertion-based assumptions with explicit runtime checks and failure returns in size lookup, cache generation, DAG generation, and hashing helpers. That is a real robustness improvement, but the provided evidence does not establish a concrete vulnerability, exploit path, or security impact beyond safer handling of invalid parameters. Root cause: Critical Ethash helper routines depended on assertion-only checks for bounds and alignment instead of explicit runtime validation and error propagation.

## Search Motifs

- input decoder feeds state-changing logic before semantic validation
- error path logs or ignores invalid data instead of failing closed
- security-relevant state changes occur before all invariants are checked

## Typical Asymmetry

- Attacker-controlled data crosses untrusted protocol input to trusted node logic boundary and reaches state mutation or security-relevant decision before the missing property is enforced.

## Patch Pattern

- Replace assertion-only invariant enforcement with explicit runtime validation and propagated error returns.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
