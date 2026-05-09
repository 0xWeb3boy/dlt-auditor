# Root-Cause Card

## Metadata

- ID: `solana-2018-04-05-solana-transaction-processing-c960e8d351`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `freshness-anchor-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The validation path conflated checking a transaction-supplied last_id with registering a new ledger anchor. That allowed arbitrary unknown last_id values supplied with transactions to become accepted replay/freshness buckets instead of requiring them to originate from the ledger registration path.

## Impact Pattern

- Primary impact: replay-protection, transaction-freshness
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch changes accountant last_id handling so transaction validation fails closed for unknown last_id values instead of accepting and registering them on demand. The provided evidence supports a replay/freshness hardening finding, but does not prove a concrete double-spend, signature-forgery, or balance-bypass vulnerability.
