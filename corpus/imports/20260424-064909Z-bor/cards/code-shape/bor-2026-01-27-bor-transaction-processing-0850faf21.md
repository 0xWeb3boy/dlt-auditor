# Code-Shape Card

## Metadata

- ID: `bor-2026-01-27-bor-transaction-processing-0850faf21`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-invariant-checks`

## Code Shape Summary

- The shown patch adds fail-closed consistency checks in Bor state processing, root-hash derivation, and checkpoint/milestone rewind handling. That is evidence of consensus-integrity hardening, but the provided diff does not establish a concrete exploitable vulnerability or a confirmed security incident. Root cause: The evidenced root cause is missing validation of internal consensus-related invariants at sensitive boundaries, especially after Bor finalization and before root-hash or rewind decisions.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Add explicit invariant checks at consensus-sensitive boundaries and abort instead of continuing on inconsistent state.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
