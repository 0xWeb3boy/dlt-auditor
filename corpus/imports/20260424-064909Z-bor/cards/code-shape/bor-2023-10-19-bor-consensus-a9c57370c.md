# Code-Shape Card

## Metadata

- ID: `bor-2023-10-19-bor-consensus-a9c57370c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## Code Shape Summary

- The patch removes a random tie-breaker from Bor's fork-choice logic and replaces it with a deterministic block-hash ordering. The evidence supports a consensus-safety hardening claim: the old code used local randomness in a consensus-critical decision path, and the new code makes that path deterministic and adds regression tests. The provided material does not prove a real-world exploit, chain split, or cross-client incompatibility. Root cause: The fork-choice implementation allowed an equal-TD, equal-height tie to be resolved by local randomness instead of a deterministic rule derived from the competing headers.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Replace local randomness in a consensus-critical tie-break with a deterministic ordering derived from consensus-visible inputs, then add regression tests for that edge case.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
