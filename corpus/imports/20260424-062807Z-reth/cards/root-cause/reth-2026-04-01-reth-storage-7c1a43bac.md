# Root-Cause Card

## Metadata

- ID: `reth-2026-04-01-reth-storage-7c1a43bac`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-state-reuse`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `per-call-resource-accounting`

## Violated Invariant

- Invariant: A precompile cache hit must preserve the current caller frame's gas accounting. Cached entries may reuse output bytes and regular gas usage, but must not replay a stale GasTracker carrying another call's reservoir or other live accounting state.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: resource-accounting
- Secondary impact: execution-integrity

## Short Reusable Lesson

- A precompile cache hit must preserve the current caller frame's gas accounting. Cached entries may reuse output bytes and regular gas usage, but must not replay a stale GasTracker carrying another call's reservoir or other live accounting state.
