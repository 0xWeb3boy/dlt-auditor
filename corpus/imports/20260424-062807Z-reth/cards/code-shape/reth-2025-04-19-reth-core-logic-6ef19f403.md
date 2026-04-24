# Code-Shape Card

## Metadata

- ID: `reth-2025-04-19-reth-core-logic-6ef19f403`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-upper-bound-check`

## Code Shape Summary

- The visible root cause is an incomplete validation routine: this function checked the relationship between `gas_used` and `gas_limit`, but did not also enforce the configured maximum gas limit before returning `Ok(())`. From the provided evidence alone, it is not clear whether that omission was the only enforcement point or merely a missing early check.

## Search Motifs

- search for `validate_header_gas` call sites that derive, cache, or validate security-sensitive state
- search for `gas_used` call sites that derive, cache, or validate security-sensitive state
- search for `gas_limit` call sites that derive, cache, or validate security-sensitive state
- missing-upper-bound-check fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but numeric-bound-validation is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- Add an explicit upper-bound validation for a protocol field in the primary validation function, and surface violations through dedicated typed errors.

## False Match Warnings

- No call-site or control-flow evidence shows this was the only effective enforcement point
- No test, bug report, or exploit scenario demonstrates prior acceptance of oversized-gas-limit blocks
- No direct evidence shows concrete downstream impact such as chain split, denial of service, or state corruption
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
