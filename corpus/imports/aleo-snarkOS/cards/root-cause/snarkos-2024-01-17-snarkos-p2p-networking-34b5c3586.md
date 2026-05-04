# Root-Cause Card

## Metadata

- ID: `snarkos-2024-01-17-snarkos-p2p-networking-34b5c3586`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signature-transcript-binding`

## Violated Invariant

- Invariant: Handshake signatures must cover all freshness and identity fields that the verifier relies on when admitting a peer session.

## Trust Boundary

- Boundary: `peer->session-setup`

## Attack Surface

- Entrypoint type: `session-setup`
- Sensitive sink: authenticated handshake acceptance
- Attacker capability: participate in handshake; reuse or craft challenge-response signatures over partial transcript data.
- Preconditions: challenge response signature authenticates peer/session; response-side freshness was not included in signed bytes.

## Impact Pattern

- Primary impact: replay or misbinding of handshake response.
- Secondary impact: weakened peer identity/session authentication.
- Severity guide: `high` for `authentication-integrity` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Handshake signatures must cover all freshness and identity fields that the verifier relies on when admitting a peer session. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch fixes a signature-binding flaw in the snarkOS handshake path. Before the change, challenge responses signed and verified only the requester-provided nonce. After the change, the response creator generates a local response nonce, signs the requester nonce together with that local nonce, includes the local nonce in the response, and verifiers check the same combined byte string. 1. In `node/router/src/handshake.rs`, the patch replaces `if !signature.verify_bytes(&peer_address, &expected_nonce.to_le_bytes()) {` with `if !signature.verify_bytes(&peer_address, &[expected_nonce.to_le_bytes(), nonce.to_le...`. 2. In `node/bft/src/gateway.rs`, the patch replaces `if !signature.verify_bytes
