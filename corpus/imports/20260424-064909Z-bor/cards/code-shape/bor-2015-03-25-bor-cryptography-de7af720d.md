# Code-Shape Card

## Metadata

- ID: `bor-2015-03-25-bor-cryptography-de7af720d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-amplification`

## Code Shape Summary

- This patch addresses a discovery-protocol UDP reflection/amplification issue. Before the change, a findnode request could reach the neighbors reply path without a prior bond check. After the change, unbonded senders are rejected with errUnknownNode, preventing that reply path. Root cause: The discovery handler trusted an unbonded sender enough to process findnode and emit a larger UDP response, enabling spoofed-source reflection/amplification.

## Search Motifs

- UDP or unauthenticated request handler sends a larger reply before bond/session validation
- discovery find/lookup request reaches neighbors or peer-list response without source proof
- reply generation and peer-table mutation occur before reachability or request-correlation checks

## Typical Asymmetry

- Attacker-controlled data crosses unauthenticated UDP discovery packet to node networking boundary and reaches larger outbound reply generation and peer-table update before the missing property is enforced.

## Patch Pattern

- Require prior protocol state before honoring a request that can trigger a larger response.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Availability claims need an externally triggerable path and enough cost asymmetry, crashability, or missing throttling to matter.
