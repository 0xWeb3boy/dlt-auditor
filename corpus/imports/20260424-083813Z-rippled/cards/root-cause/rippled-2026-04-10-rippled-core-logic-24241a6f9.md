# Root-Cause Card

## Metadata

- ID: `rippled-2026-04-10-rippled-core-logic-24241a6f9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `asset-restriction-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: policy-bypass
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The supported finding is a likely security fix for incomplete MPT and issued-asset restriction checks in specific CheckCreate and OfferCreate paths.
