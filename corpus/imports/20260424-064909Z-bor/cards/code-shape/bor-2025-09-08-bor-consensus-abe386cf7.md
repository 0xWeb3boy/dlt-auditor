# Code-Shape Card

## Metadata

- ID: `bor-2025-09-08-bor-consensus-abe386cf7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-set-validation`

## Code Shape Summary

- The patch clearly strengthens Bor consensus validation around pre-Rio validator bytes and span data quality, but the provided evidence does not establish a concrete exploitable vulnerability. The strongest supported reading is consensus-correctness or security-hardening work in a sensitive path, not a confirmed security fix. Root cause: The visible root cause is under-enforced consistency checking in pre-Rio consensus handling: header validator or producer bytes were not explicitly checked in this path before seal verification, and span handling tolerated empty SelectedProducers data. The evidence does not prove whether this was exploitable or only a correctness issue.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Add explicit consensus-input validation at header processing time and reject incomplete upstream span data before it can influence later decisions.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
