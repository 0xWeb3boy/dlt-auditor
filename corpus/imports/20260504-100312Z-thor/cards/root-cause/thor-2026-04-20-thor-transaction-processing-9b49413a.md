# Root-Cause Card

## Metadata

- ID: `thor-2026-04-20-thor-transaction-processing-9b49413a`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-chain-id-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `domain-separation`

## Violated Invariant

- Invariant: A transaction format that uses chain ID as replay-protection material must be rejected unless its signed domain matches the active network and fork rules.

## Trust Boundary

- Boundary: `transaction-submitter->mempool-and-consensus-validation`

## Attack Surface

- Entrypoint type: `transaction-admission-and-block-validation`
- Sensitive sink: network acceptance of EIP-1559 typed transactions and EVM CHAINID semantics
- Attacker capability: Craft EIP-1559 typed transactions with a chosen Ethereum chain ID.
- Preconditions: The transaction type is enabled or partially accepted by the node.

## Impact Pattern

- Primary impact: signature replay-domain integrity
- Secondary impact: mempool/consensus rule consistency
- Blast radius: `chain-wide`

## Short Reusable Lesson

- Compatibility transaction formats need explicit replay-domain validation wherever transactions enter the node and wherever blocks are validated, not only in runtime configuration.
