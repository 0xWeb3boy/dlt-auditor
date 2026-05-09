# Root-Cause Card

## Metadata

- ID: `solana-2019-09-12-solana-staking-5dceeec1ca`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization`
- Confidence tier: `tier_b_likely`

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

The evidence supports only that authorization logic was redesigned from a signer-presence check to state-specific authorization checks. It does not prove that the earlier signer check accepted an unauthorized party, nor does it include enough surrounding account semantics or `check_authorized` implementation to establish a concrete root-cause vulnerability.

## Impact Pattern

- Primary impact: unauthorized-staking-operation, unauthorized-funds-movement
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch changes staking control paths to use `stake.check_authorized(...)` and `lockup.check_authorized(...)` with `other_signers`, but the supplied evidence does not establish that the previous behavior was an exploitable vulnerability. The commit also appears to add or generalize authorized-staker functionality, so this is best treated as potentially security-relevant authorization work rather than a confirmed vulnerability fix.
