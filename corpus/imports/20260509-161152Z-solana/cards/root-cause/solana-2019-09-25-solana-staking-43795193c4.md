# Root-Cause Card

## Metadata

- ID: `solana-2019-09-25-solana-staking-43795193c4`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-hardening`
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

The withdrawal path used a generic vote-account signer requirement instead of checking the role-specific withdraw authority stored in vote account state. Related voter authorization logic was duplicated inline rather than routed through the shared authorized-signer verification helper.

## Impact Pattern

- Primary impact: privilege-boundary-hardening
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch is likely an access-control fix in Solana's vote API. The strongest supported change is that withdrawals now verify `vote_state.authorized_withdrawer` using a shared authorized-signer path, instead of only requiring the vote account itself to sign. Vote processing was also moved from inline authorized-voter signer matching to a shared helper, and the authorization API was generalized to handle voter or withdrawer roles.
