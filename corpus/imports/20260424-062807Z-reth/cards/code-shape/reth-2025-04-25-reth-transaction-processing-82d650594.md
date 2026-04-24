# Code-Shape Card

## Metadata

- ID: `reth-2025-04-25-reth-transaction-processing-82d650594`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-validation`

## Code Shape Summary

- Validation rules were split across multiple entrypoints, so the canonical header validator and the alternate helper did not obviously enforce the same merge-era checks. The patch removes that split by centralizing the shown checks in the primary validator.

## Search Motifs

- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- improper-consensus-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses block or transaction input -> execution-layer validator, but protocol-rule-enforcement is incomplete before the code updates or relies on transaction acceptance or consensus rule application.

## Patch Pattern

- Consolidate duplicated or alternate validation logic into the canonical validation entrypoint and update callers to use that single path.

## False Match Warnings

- No test or reproducer is shown proving previously accepted invalid headers on a reachable path
- The full removed helper body is not provided, so prior nonce and related checks are not fully visible
- No repository-wide call-site evidence shows which callers previously bypassed equivalent merge checks
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
