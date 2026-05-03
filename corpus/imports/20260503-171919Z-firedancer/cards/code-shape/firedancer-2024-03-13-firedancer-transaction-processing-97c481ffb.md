# Code-Shape Card

## Metadata

- ID: `firedancer-2024-03-13-firedancer-transaction-processing-97c481ffb`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The runtime answered “is this writable?” by searching for any writable alias of the same address instead of checking the exact indexed instruction account being mutated.

## Search Motifs

- Motif 1: same-address alias searched during writability check
- Motif 2: helper rewritten from address-based to index-based authorization
- Motif 3: authorization answer derived from any matching account instead of exact instruction account

## Typical Asymmetry

- The attacker can supply aliasing accounts, but the guard must reason about the exact account instance that reaches the sink.

## Patch Pattern

- Bind helper APIs to the concrete instruction-account index and perform mutability or ownership checks on that exact indexed entry.

## False Match Warnings

- No exploit transaction or reproduction is provided.
- No concrete asset theft, lamport loss, or consensus impact is shown.
