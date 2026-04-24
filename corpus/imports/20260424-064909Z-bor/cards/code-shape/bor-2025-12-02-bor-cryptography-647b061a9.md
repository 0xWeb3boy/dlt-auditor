# Code-Shape Card

## Metadata

- ID: `bor-2025-12-02-bor-cryptography-647b061a9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- The grounded security-relevant change is in Bor consensus difficulty validation. Before the patch, generic header sanity allowed Difficulty values above 64 bits, and seal verification compared header.Difficulty.Uint64() to the expected signer-turn value without first proving the value was representable as uint64. After the patch, both layers enforce a 64-bit bound and reject malformed difficulty values. Root cause: Validation of a consensus-significant field was inconsistent across layers: header sanity permitted wider Difficulty values than the consensus path actually intended to support, and seal verification narrowed the value to uint64 without first enforcing representability.

## Search Motifs

- input decoder feeds state-changing logic before semantic validation
- error path logs or ignores invalid data instead of failing closed
- security-relevant state changes occur before all invariants are checked

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Align generic object validation with protocol-width requirements and reject non-representable numeric values before narrowing them in security- or consensus-critical logic.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
