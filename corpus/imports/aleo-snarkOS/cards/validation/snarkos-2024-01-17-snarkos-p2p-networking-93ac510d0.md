# Validation Card

## Metadata

- ID: `snarkos-2024-01-17-snarkos-p2p-networking-93ac510d0`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-fix` with verdict `confirmed` and kept in the security corpus.
- The patch pattern matches the missing property: Add a response nonce, include it in the response schema, sign the combined challenge and response nonce bytes, and verify the exact transcript.
- Root-cause evidence from the finding: The pre-fix challenge-response signature covered only the counterparty challenge nonce. That made the signed bytes narrower than the response being authenticated and allowed the handshake path to produce or accept signatures without binding response-side freshness into the signed data. 1. A peer sends a ChallengeRequest containing a nonce. 2. Before the fix, the receiver signed only that peer-provided nonce when constructing a ChallengeResponse. 3. Before the fix, router and BFT gateway verifica

## What Could Have Invalidated It

- Mutual-auth transport signs full transcript independently.
- Verifier rejects reused response nonces elsewhere.

## Severity Guidance

- Expected impact band: `authentication-integrity`
- Expected severity band: `high`
- Rationale: High severity is appropriate when the affected boundary is reachable and the sink controls replay or misbinding of handshake response; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- If an outer channel binds the full transcript, the bug may be mitigated
- Nonce-schema migrations without verifier changes are not enough
- Do not conflate with private-key exposure
