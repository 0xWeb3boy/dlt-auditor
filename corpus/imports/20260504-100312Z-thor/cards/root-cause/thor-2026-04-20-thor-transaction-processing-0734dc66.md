# Root-Cause Card

## Metadata

- ID: `thor-2026-04-20-thor-transaction-processing-0734dc66`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `chain-id-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `domain-separation`

## Violated Invariant

- Invariant: Typed transactions that rely on chain ID for replay protection must be accepted only after the enabling fork and only when their embedded chain ID matches the network domain used by runtime execution.

## Trust Boundary

- Boundary: `transaction-submitter->mempool-and-consensus-validation`

## Attack Surface

- Entrypoint type: `transaction-admission-and-block-validation`
- Sensitive sink: acceptance of EIP-1559 typed transactions and runtime CHAINID domain exposure
- Attacker capability: Submit EIP-1559 typed transactions with arbitrary embedded chain IDs.
- Preconditions: The network supports or is approaching the fork that enables the typed transaction format.

## Impact Pattern

- Primary impact: signature replay-domain integrity
- Secondary impact: fork rule consistency
- Blast radius: `chain-wide`

## Short Reusable Lesson

- When introducing a new transaction domain, fork gates, mempool admission, consensus validation, and runtime-visible chain identity must all enforce the same domain-separation rule.
