# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-02-14-stacks-core-transaction-processing-5ad797514e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-message-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-domain-and-signer-binding`

## Violated Invariant

- Invariant: Every signed protocol message must be verified against the exact signer set, message domain, reward cycle, and payload hash that authorize the downstream action.

## Trust Boundary

- Boundary: Externally supplied transaction, block proposal, or signer payload crosses into transaction validation.

## Attack Surface

- Entrypoint type: `transaction_or_block_proposal`
- Sensitive sink: transaction acceptance, block proposal evaluation, or signer coordination state

## Impact Pattern

- Primary impact: protocol-integrity
- Secondary impact: authorization-bypass-hardening

## Short Reusable Lesson

- The patch changes Nakamoto miner/signer coordination logic in testnet/stacks-node/src/nakamoto_node/miner.rs. It builds a signer slot-to-address map, filters signer-submitted transactions by origin address, begins nonce-related chainstate handling, and changes rejection accounting to use signer weights while skipping already-seen signer IDs.
