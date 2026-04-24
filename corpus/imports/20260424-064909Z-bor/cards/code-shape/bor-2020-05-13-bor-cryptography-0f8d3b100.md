# Code-Shape Card

## Metadata

- ID: `bor-2020-05-13-bor-cryptography-0f8d3b100`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-boundary-validation`

## Code Shape Summary

- The patch corrects a sprint-boundary validator-set check in Bor consensus verification. The evidence supports an off-by-one boundary bug in which expected validator bytes were compared against the wrong block's Extra field. The code change is in consensus logic, but the provided evidence does not establish a concrete vulnerability outcome beyond incorrect validation behavior. Root cause: The verifier used data from different points in the sprint transition: it built expected validator bytes from a snapshot rooted at number-1 but previously compared them to the current header's Extra bytes instead of the parent sprint-boundary header that corresponds to that snapshot.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Align boundary validation with the block/state boundary actually represented by the snapshot, and improve mismatch reporting with structured error data.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
