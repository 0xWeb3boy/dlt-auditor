# Root-Cause Card

## Metadata

- ID: `bor-2021-04-06-bor-transaction-processing-706683ea7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection-gating`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `replay-protection and signature domain binding`

## Violated Invariant

- Invariant: Signed messages and transactions must be bound to the intended chain, domain, nonce, and execution context before they are accepted or relayed.

## Trust Boundary

- Boundary: external RPC/user signing request to local signer boundary

## Attack Surface

- Entrypoint type: RPC signing or transaction-submission method
- Sensitive sink: signature creation or signed transaction acceptance

## Impact Pattern

- Primary impact: replay-protection
- Secondary impact: rpc-behavior

## Short Reusable Lesson

- Duplicated eth_chainId implementations had diverged in behavior. One path enforced the EIP-155 activation check but narrowed the value type; the other preserved bigint width but skipped the activation check entirely.
