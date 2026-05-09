# Root-Cause Card

## Metadata

- ID: `solana-2020-07-31-solana-staking-61d9d219f9`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-role-confusion`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The root cause was authorization role confusion: the lockup bypass decision used membership in a generic transaction signer set instead of a role-qualified custodian input. If another role used the same public key as the custodian, that role's signature could be interpreted as satisfying the custodian exemption.

## Impact Pattern

- Primary impact: access-control-bypass, lockup-bypass, economic-policy-bypass
- Expected band: integrity_or_funds
- Severity guide: Medium

## Short Reusable Lesson

The patch fixes a stake lockup role-confusion issue. Before the change, `Lockup::is_in_force` treated the lockup as not in force when the custodian public key appeared anywhere in a generic signer set. The commit message states this allowed a withdraw authority signature, and similarly fee-payer signing, to imply custodian authority when keys overlapped, causing lockup enforcement to be skipped. After the change, the lockup exemption is granted only whe...
