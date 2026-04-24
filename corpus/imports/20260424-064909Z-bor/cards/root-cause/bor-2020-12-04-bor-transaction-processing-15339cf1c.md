# Root-Cause Card

## Metadata

- ID: `bor-2020-12-04-bor-transaction-processing-15339cf1c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsigned-advisory-feed`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature authorization and domain binding`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: untrusted signed payload to verifier or signer boundary

## Attack Surface

- Entrypoint type: transaction/message signature verification path
- Sensitive sink: signer recovery, authorization, or replay-protection decision

## Impact Pattern

- Primary impact: integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- Not established by the provided evidence. At most, the commit shows that advisory-feed authenticity was implemented or strengthened in the new checker. The evidence does not prove that older code accepted unauthenticated advisory data or that a concrete security bug existed before this commit.
