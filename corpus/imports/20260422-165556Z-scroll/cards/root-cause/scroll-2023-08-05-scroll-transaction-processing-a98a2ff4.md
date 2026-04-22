# Root-Cause Card

## Metadata

- ID: `scroll-2023-08-05-scroll-transaction-processing-a98a2ff4`
- Bug family: `authz_and_role_gates`
- Bug class: `authentication-challenge-replay-protection`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `replay-freshness-binding`

## Violated Invariant

- Invariant: A prover login flow should consume a single-use challenge that is bound to the presented bearer token and must not accept replayed challenge material.

## Trust Boundary

- Boundary: `prover->coordinator-auth-session`

## Attack Surface

- Entrypoint type: `session-setup`
- Sensitive sink: `issuance of an authenticated coordinator login session for a prover`

## Impact Pattern

- Primary impact: `unauthorized-action`
- Secondary impact: `stale-trust-state`

## Short Reusable Lesson

- A prover login flow should consume a single-use challenge that is bound to the presented bearer token and must not accept replayed challenge material. The patch is best supported as an authentication replay fix in the coordinator login path. The visible code adds an explicit equality check between the Authorization bearer token and login.Message.Challenge, and changes replay tracking from storing login.Signature to storing login.Message.Challenge. That is grounded evidence of fixing nonce/challenge binding and replay consumption in login. The robust fix is to bind the presented token to the signed challenge and store or invalidate the canonical challenge value rather than a derived signature field when consuming login requests.
