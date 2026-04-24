# Code-Shape Card

## Metadata

- ID: `reth-2023-02-11-reth-transaction-processing-eba63b8f7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-transition-check`

## Code Shape Summary

- The visible root cause is an incomplete fork-activation check at the Paris/TTD boundary: callers relied on cumulative total difficulty alone and omitted the current header or payload difficulty needed to classify the transition side correctly.

## Search Motifs

- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `active_at_ttd(...)` call sites that derive, cache, or validate security-sensitive state
- consensus-transition-check fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses block or transaction input -> execution-layer validator, but protocol-rule-enforcement is incomplete before the code updates or relies on transaction acceptance or consensus rule application.

## Patch Pattern

- Expand a fork-activation predicate to include the transition-defining field that was previously omitted, then update all consensus-sensitive call sites to use the richer predicate consistently.

## False Match Warnings

- No test, reproducer, or failing scenario shows acceptance of invalid blocks or rejection of valid ones before the patch
- No evidence demonstrates a concrete attacker-controlled exploit path or remote trigger beyond transition-boundary correctness
- No proof is provided of chain split, consensus bypass, or production impact on specific networks
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
