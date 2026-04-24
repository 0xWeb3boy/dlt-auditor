# Code-Shape Card

## Metadata

- ID: `bor-2016-11-28-bor-p2p-networking-e949a2ed2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-boundary-enforcement`

## Code Shape Summary

- The supported evidence shows a correctness fix in Swarm network ID handling across configuration, protocol startup, and handshake validation. It does not by itself establish a concrete security vulnerability or exploit path. Root cause: The configured swarm network ID was not carried consistently into connection-specific protocol state, and the handshake check used a global default value instead of the local instance value.

## Search Motifs

- handshake or protocol handler advances peer state before validating identity, key, or request correlation
- sync response is accepted without matching an outstanding request or expected peer capability
- peer-controlled metadata is trusted for scheduling, scoring, or chain progress before verification

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Propagate instance-specific configuration into runtime protocol state and enforce checks against that instance-scoped value instead of a package-level default.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
