# Code-Shape Card

## Metadata

- ID: `bor-2023-01-03-bor-storage-fcf3d0048`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation`

## Code Shape Summary

- The evidence supports a fork ID validation fix in ETH/LES peer compatibility checks. It corrects how local fork state is represented and compared, but the provided diff does not establish a concrete vulnerability beyond incorrect peer accept/reject behavior, so the security thesis remains unclear. Root cause: Fork ID validation did not cleanly separate block-based versus time-based fork transitions and did not clearly anchor the full decision to one local snapshot, which could lead to incorrect compatibility results.

## Search Motifs

- handshake or protocol handler advances peer state before validating identity, key, or request correlation
- sync response is accepted without matching an outstanding request or expected peer capability
- peer-controlled metadata is trusted for scheduling, scoring, or chain progress before verification

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Separate heterogeneous transition types and validate each against the correct snapshot of local state.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
