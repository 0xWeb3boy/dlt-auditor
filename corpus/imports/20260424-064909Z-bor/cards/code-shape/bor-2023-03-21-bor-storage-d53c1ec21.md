# Code-Shape Card

## Metadata

- ID: `bor-2023-03-21-bor-storage-d53c1ec21`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-set-verification`

## Code Shape Summary

- The patch changes Bor header verification so validator retrieval no longer walks backward across ancestor hashes on lookup failure and instead uses a single explicit block-number-or-hash query path. That supports a consensus-correctness fix around validator-set sourcing, but the provided evidence does not establish that the pre-fix behavior was an exploitable vulnerability or even whether it accepted invalid headers, rejected valid ones, or both. Root cause: The verifier's validator lookup logic mixed consensus checking with fallback retry behavior that could change the state source from the immediate parent context to older ancestors after errors, instead of using one explicit lookup path.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Replace error-driven fallback across multiple historical state snapshots with a single explicit state-selection API and fail on retrieval errors.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
