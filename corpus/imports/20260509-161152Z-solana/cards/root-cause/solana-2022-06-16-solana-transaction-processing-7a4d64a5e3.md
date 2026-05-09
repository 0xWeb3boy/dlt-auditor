# Root-Cause Card

## Metadata

- ID: `solana-2022-06-16-solana-transaction-processing-7a4d64a5e3`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The replay batch execution path lacked a bank-level per-block accounts data size validation step after transaction execution. The existing check was tied to feature-gated execution-result errors for the total accounts data limit, so the per-block limit was not evidenced as enforced in this path before the change.

## Impact Pattern

- Primary impact: resource-limit-bypass, consensus-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch hardens Solana ledger replay by adding an unconditional account-data-size validation step in `execute_batch` and extending the helper to run a bank-level per-block accounts data check before preserving the existing total-size execution-result scan.
