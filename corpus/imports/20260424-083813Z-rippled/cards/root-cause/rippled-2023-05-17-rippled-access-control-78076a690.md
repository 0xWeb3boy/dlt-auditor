# Root-Cause Card

## Metadata

- ID: `rippled-2023-05-17-rippled-access-control-78076a690`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-input-acceptance`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-and-state-invariant-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: externally submitted action -> account, delegate, or role authorization gate

## Attack Surface

- Entrypoint type: authorization-check-path
- Sensitive sink: privileged account action, delegated permission, or role-scoped state change

## Impact Pattern

- Primary impact: credential-exposure-risk
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The change hardens rippled RPC account parsing by removing legacy RPC::accountFromString handling from multiple account-query handlers and requiring parseBase58<AccountID> instead.
