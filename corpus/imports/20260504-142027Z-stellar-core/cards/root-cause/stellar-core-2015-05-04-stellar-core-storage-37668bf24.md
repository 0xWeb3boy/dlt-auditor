# Root-Cause Card

## Metadata

- ID: `stellar-core-2015-05-04-stellar-core-storage-37668bf24`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-state-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `issuer-authorization-state-transition-guard`

## Violated Invariant

- Invariant: Issuer authorization flags and trustline authorization state must not be changed in ways that contradict already-issued credit or the issuer revocation policy.

## Trust Boundary

- Boundary: issuer-configuration-operation -> trustline-authorization-state

## Attack Surface

- Entrypoint type: transaction-operation-apply
- Sensitive sink: authorization flag mutation and trustline authorization revocation
- Attacker capability: Submit issuer-controlled SetOptions or AllowTrust operations.
- Main precondition: The issuer can set authorization-related flags after issuing credit.

## Impact Pattern

- Primary impact: authorization-policy-integrity
- Secondary impact: asset-accounting-policy, ledger-invariant-violation
- Severity guess: medium because The change protects issued-asset authorization semantics and user expectations, but evidence does not show direct fund theft or chain-wide compromise.

## Short Reusable Lesson

- Authorization policy transitions must account for already-created state; changing the rules after assets exist can violate holder and issuer invariants.
