# Root-Cause Card

## Metadata

- ID: `geth-arb-2020-12-04-go-ethereum-transaction-processing-15339cf1c9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `advisory-feed-authentication`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `advisory-feed-authenticity`

## Violated Invariant

- Invariant: Security advisory or version feeds consumed by a node must be authenticated before they influence operator-facing warnings or update decisions.

## Trust Boundary

- Boundary: remote advisory feed -> local client security warning logic

## Attack Surface

- Entrypoint type: version/advisory feed fetcher
- Sensitive sink: security warning, update recommendation, or operator trust decision

## Impact Pattern

- Primary impact: operator-safety
- Secondary impact: supply-chain-integrity
- Severity guide: low-medium

## Short Reusable Lesson

- A vulnerability-check mechanism needed signed feed validation so remote advisory content could not be trusted solely by transport or URL. Verify advisory feed signatures and trusted keys before accepting feed contents for version or vulnerability checks.
