# Root-Cause Card

## Metadata

- ID: `rippled-2025-04-07-rippled-access-control-f839049de`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-recursion-boundary`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: externally submitted action -> account, delegate, or role authorization gate

## Attack Surface

- Entrypoint type: authorization-check-path
- Sensitive sink: privileged account action, delegated permission, or role-scoped state change

## Impact Pattern

- Primary impact: authorization-hardening, availability-hardening
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The evidence supports a correctness and possible hardening change in rippled vault asset handling: requireAuth changes its recursion guard from depth > maxFreezeCheckDepth to depth >= maxFreezeCheckDepth, VaultCreate checks MPT assets for excessive recursive vault-share authorization chains, and VaultDeposit adds or reorders asset identity, freeze, and...
