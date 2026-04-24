# Code-Shape Card

## Metadata

- ID: `bor-2022-05-04-bor-p2p-networking-ecae8e4f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation-regression`

## Code Shape Summary

- The evidence supports a regression fix in how configured required-block mappings are wired from configuration into the ETH peer handler. It does not, from the provided hunks alone, establish a concrete vulnerability or prove an exploitable security bypass. Root cause: A regression left required-block handling wired to an older PeerRequiredBlocks path instead of the current RequiredBlocks path, causing inconsistent propagation of configured required-block data into peer startup logic.

## Search Motifs

- handshake or protocol handler advances peer state before validating identity, key, or request correlation
- sync response is accepted without matching an outstanding request or expected peer capability
- peer-controlled metadata is trusted for scheduling, scoring, or chain progress before verification

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Unify a regressed configuration-controlled validation path onto one canonical field across parsing, config loading, and runtime use.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
