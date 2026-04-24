# Root-Cause Card

## Metadata

- ID: `geth-arb-2025-04-08-go-ethereum-transaction-processing-2e739fce58`
- Bug family: `resource_accounting_and_limits`
- Bug class: `txpool-resource-exhaustion-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `txpool-resource-isolation`

## Violated Invariant

- Invariant: Mempool pools must prevent one transaction type or delegated sender state from bypassing per-account and per-resource isolation rules.

## Trust Boundary

- Boundary: external transaction -> txpool/blobpool admission

## Attack Surface

- Entrypoint type: transaction pool validation path
- Sensitive sink: mempool resource reservation and peer propagation

## Impact Pattern

- Primary impact: mempool-availability
- Secondary impact: resource-exhaustion
- Severity guide: medium-high

## Short Reusable Lesson

- Blobpool and delegated-authority handling needed additional constraints so EIP-7702 or pending-delegation senders could not occupy incompatible pool resources. Reject delegated/pending-delegation sender conflicts and enforce authority/resource constraints before pool insertion.
