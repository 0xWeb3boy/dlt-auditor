# Validation Card

## Metadata

- ID: `snarkos-2022-11-29-snarkos-p2p-networking-607d5a7ec`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `p2p-handshake-authentication-hardening`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Add nonce signing to challenge responses and verify response data against peer identity, expected genesis header, and expected nonce.
- Root-cause evidence from the finding: The provided evidence shows the old handshake response lacked the newly added nonce/signature authentication material, but it does not prove that this omission was exploitable or that unauthenticated peers reached a privileged state. 1. The router creates a fresh local nonce and sends it in a challenge request. 2. The peer's challenge request is received and validated before the local side proceeds. 3. The patched code signs the peer-provided nonce before sending its own challenge response. 4. T

## What Could Have Invalidated It

- Noise/TLS layer already authenticates peer keys.
- Router treats identity as informational only.

## Severity Guidance

- Expected impact band: `peer-authentication`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls weaker peer identity assurance; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- If peer identity is not trusted for any later decision, impact is reduced
- Transport-level mutual authentication can compensate
- Do not infer full exploit without evidence that unauthenticated sessions become privileged
