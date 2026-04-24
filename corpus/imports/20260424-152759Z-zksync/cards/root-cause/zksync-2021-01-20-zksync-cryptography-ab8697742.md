# Root-Cause Card

## Metadata

- ID: `zksync-2021-01-20-zksync-cryptography-ab8697742`
- Bug family: `authz_and_role_gates`
- Bug class: `transaction-authentication-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `account-auth-mode-consistency`

## Violated Invariant

- Invariant: Transaction authentication must respect the account creation/control mode; deterministic or CREATE2-derived accounts should not accept unrelated Ethereum signature data as an alternate authority.

## Trust Boundary

- Boundary: User-submitted transaction authentication data crosses into transaction sender signature verification.

## Attack Surface

- Entrypoint type: `transaction_submission_and_batch_validation`
- Sensitive sink: transaction admission for CREATE2 account operations and account-id extraction

## Impact Pattern

- Primary impact: transaction authorization hardening
- Secondary impact: panic avoidance in disabled transaction handling

## Short Reusable Lesson

- The transaction sender signature path rejects Ethereum signature data for CREATE2 accounts in single and batch checks, and a disabled Close transaction path returns an error instead of panicking. The reusable shape is accepting auth material that is inconsistent with the account authority model.
