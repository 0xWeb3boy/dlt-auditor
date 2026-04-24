# Code-Shape Card

## Metadata

- ID: `bor-2025-11-28-bor-cryptography-544e6b7c7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `numeric-truncation`

## Code Shape Summary

- The supported security-relevant change is stricter consensus/header validation for Difficulty. Before the patch, seal verification compared header.Difficulty.Uint64() to the expected signer difficulty while header sanity checks still allowed Difficulty values above 64 bits. After the patch, non-uint64 Difficulty values are rejected in verifySeal and header sanity checking is tightened to a 64-bit limit, closing a truncation-based acceptance gap for malformed headers. Root cause: Canonical width validation for the Difficulty field was inconsistent. verifySeal narrowed big.Int to uint64 before validating representability, while Header.SanityCheck permitted wider values, allowing malformed non-canonical encodings to reach consensus comparison.

## Search Motifs

- gas, fee, size, or work accounting uses unchecked add/mul/cast on attacker-influenced values
- large protocol parameter crosses uint/int or narrow/wide type boundary before validation
- resource charge is computed after state mutation or uses a value that can wrap or truncate

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Reject oversized or non-canonical numeric encodings before narrowing or comparing protocol fields in consensus logic.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
