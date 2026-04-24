# Code-Shape Card

## Metadata

- ID: `reth-2023-09-26-reth-storage-eb6dc5197`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-validation`

## Code Shape Summary

- The shown validation entrypoint lacked an explicit fork-gated check for blob transactions on pre-Cancun timestamps, and the old flow constructed or validated a sealed block before exposing a place to apply that rule in this function.

## Search Motifs

- derived blob, commitment, or fork fields are computed but not compared against declared protocol values
- blob sidecar metadata validated for count/proof but not bound to declared versioned hashes or fork rules
- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `BeaconOnNewPayloadError` call sites that derive, cache, or validate security-sensitive state
- consensus-rule-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but protocol-rule-enforcement is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- Add explicit fork-aware validation before downstream sealing or hash validation, and use a separate error path for malformed or disallowed inputs when the API requires different handling.

## False Match Warnings

- No pre-patch execution trace proves such payloads were previously accepted through to canonical processing
- No test or runtime evidence shows a consensus split, chain halt, or remotely triggerable exploit
- The excerpts do not show downstream state transition effects from the old behavior
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
