# Code-Shape Card

## Metadata

- ID: `bor-2015-01-19-bor-p2p-networking-e252c634c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `public-key-validation`

## Code Shape Summary

- The evidence supports a responder-side invalid-public-key check added during an in-progress p2p crypto handshake integration, not a clearly established vulnerability fix. The patch changes respondToHandshake to accept raw DER bytes, decode them locally, and return an error on invalid input, but the commit message and surrounding edits are dominated by refactoring/integration work and explicitly note the flow still crashes later in DH setup. Root cause: The only grounded issue shown is that the responder helper previously relied on a pre-parsed public key from its caller instead of decoding and rejecting invalid key bytes at the point of use. The provided evidence does not establish whether that was an exploitable security flaw or simply a correctness problem during handshake integration.

## Search Motifs

- handshake or protocol handler advances peer state before validating identity, key, or request correlation
- sync response is accepted without matching an outstanding request or expected peer capability
- peer-controlled metadata is trusted for scheduling, scoring, or chain progress before verification

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Move key parsing to the trust boundary and fail closed on invalid key material, bundled with handshake API refactoring.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
