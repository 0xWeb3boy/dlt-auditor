# Root-Cause Card

## Metadata

- ID: `snarkos-2022-11-29-snarkos-p2p-networking-607d5a7ec`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `p2p-handshake-authentication-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `handshake-identity-binding`

## Violated Invariant

- Invariant: A peer handshake should prove control of the advertised identity key over fresh challenge material before the session is admitted.

## Trust Boundary

- Boundary: `peer->session-setup`

## Attack Surface

- Entrypoint type: `session-setup`
- Sensitive sink: authenticated peer identity and connection admission
- Attacker capability: initiate or respond to p2p handshakes; send challenge responses without proving address key ownership under fresh transcript.
- Preconditions: peer identity matters for routing or trust decisions; handshake previously accepted header/nonce material without signature binding.

## Impact Pattern

- Primary impact: weaker peer identity assurance.
- Secondary impact: possible spoofed or replayed connection metadata.
- Severity guide: `medium` for `peer-authentication` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- A peer handshake should prove control of the advertised identity key over fresh challenge material before the session is admitted. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch adds authenticated-handshake mechanics to the router handshake path, including nonce signing, a signature-bearing challenge response, and expanded verification inputs. The supplied evidence supports security-relevant hardening, but it does not establish a concrete pre-patch vulnerability or show the full signature verification logic, so this should not be kept as a confirmed vulnerability fix. 1. In `node/router/src/handshake.rs`, the patch replaces `message: ChallengeResponse<N>,` with `peer_address: Address<N>,`. 2. In `node/router/src/handshake.rs`, the patch replaces `trace!("Received '{}-B' from '{peer_addr}'", challenge_request.name());` with `trace!("Received '{}-B' from '{p
