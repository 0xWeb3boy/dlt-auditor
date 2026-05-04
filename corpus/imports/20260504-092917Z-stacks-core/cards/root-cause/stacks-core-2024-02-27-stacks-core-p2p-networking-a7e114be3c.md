# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-02-27-stacks-core-p2p-networking-a7e114be3c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `inconsistent-signer-transaction-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-domain-and-signer-binding`

## Violated Invariant

- Invariant: Every signed protocol message must be verified against the exact signer set, message domain, reward cycle, and payload hash that authorize the downstream action.

## Trust Boundary

- Boundary: Remote peer message crosses into networking, relay, or peer-state validation.

## Attack Surface

- Entrypoint type: `p2p_message_or_block`
- Sensitive sink: peer relay buffer, block acceptance path, or network reputation state

## Impact Pattern

- Primary impact: transaction-integrity
- Secondary impact: replay-resistance

## Short Reusable Lesson

- The patch appears to centralize vote-transaction filtering in `NakamotoSigners` and apply that shared logic from signer and miner paths. This may be security relevant because it touches signer transaction validation, but the supplied evidence does not prove that invalid transactions could be executed, finalized, replayed, or used to cause a consensus failure before the patch. Structural cue: In `stacks-signer/src/signer.rs`, the patch removes `fn parse_vote_for_aggregate_public_key(`.
