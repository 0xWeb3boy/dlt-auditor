# Code-Shape Card

## Metadata

- ID: `bor-2026-04-16-bor-transaction-processing-11ecb6aa7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`

## Code Shape Summary

- The evidence shows a consensus-sensitive correctness hardening: Bor.Finalize now returns explicit errors for unsupported body fields, and both block processors now propagate those errors and fail on state-sync receipt-accounting mismatches. The supplied excerpts do not establish a concrete pre-patch vulnerability beyond silent or delayed handling of invalid conditions. Root cause: The shown issue is an enforcement gap at the Bor finalization boundary: invalid or unsupported conditions were not surfaced as explicit errors from Finalize, and callers had no direct failure channel. The excerpts support missing validation and error propagation; they do not fully prove a deeper corruption or exploit path.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Replace implicit or sentinel failure behavior in a consensus-sensitive path with explicit validation, typed errors, and immediate caller-side propagation; add invariant checks for derived receipt accounting.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
