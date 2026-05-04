# Root-Cause Card

## Metadata

- ID: `moonbeam-2026-02-21-moonbeam-transaction-processing-8cff9775f9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `unprotected-transaction-admission`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `ethereum-replay-protection-admission-policy`

## Violated Invariant

- Invariant: Transaction admission must enforce replay-protected signatures for Ethereum-format transactions on production networks.

## Trust Boundary

- Boundary: Untrusted Ethereum transaction submissions cross into runtime validation and block inclusion.

## Attack Surface

- Entrypoint type: ethereum-transaction-admission
- Sensitive sink: legacy Ethereum transaction acceptance

## Impact Pattern

- Primary impact: request-forgery-or-replay
- Secondary impact: transaction-admission-policy-bypass

## Short Reusable Lesson

- A production runtime allowed unprotected legacy Ethereum transactions by configuration. The fix sets AllowUnprotectedTxs false and aligns RPC/tests with protected transaction requirements. Set transaction-admission policy to reject unprotected legacy transactions consistently across runtime and node RPC code.
