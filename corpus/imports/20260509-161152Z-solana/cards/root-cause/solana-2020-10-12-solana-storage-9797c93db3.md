# Root-Cause Card

## Metadata

- ID: `solana-2020-10-12-solana-storage-9797c93db3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-native-loader-input`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach canonical bank state, account storage, snapshot acceptance, or ledger root.

## Trust Boundary

- Boundary: persisted or downloaded ledger/account state to trusted runtime reconstruction

## Attack Surface

- Entrypoint type: snapshot load, blockstore replay, accounts hash verification, or storage maintenance
- Sensitive sink: canonical bank state, account storage, snapshot acceptance, or ledger root

## Root Cause

The root cause was brittle error handling in the native-loader dispatch and lookup path: the code assumed required account data and environment/library state were valid, and used panic-based failure handling for cases that could instead be represented as instruction errors. The evidence does not establish that these assumptions created a security vulnerability.

## Impact Pattern

- Primary impact: availability
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch hardens Solana's runtime native-loader path by replacing unchecked first-account access and several panic paths with explicit error returns. The evidence supports improved handling for empty account lists, invalid UTF-8 account data, empty or leading-NUL native names, executable path failures, missing entrypoints, and library load failures. However, the supplied material does not prove that these conditions were reachable by an untrusted trans...
