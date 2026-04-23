# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-05-14-go-ethereum-transaction-processing-a4246c2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unknown-parent-sync-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: During block synchronization, the downloader should distinguish benign absence of ready blocks from an invalid queued head whose parent is not locally known, and callers should abort on the invalid state instead of treating it as normal no-work.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `sync-disruption`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- Likely security-hardening in go-ethereum's block downloader for a potential unknown-parent synchronization attack.
