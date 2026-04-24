# Code-Shape Card

## Metadata

- ID: `bor-2026-04-13-bor-transaction-processing-bc8857fc8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`

## Code Shape Summary

- The patch hardens Bor block finalization by turning silent failure cases into explicit errors and by making both state processors stop when finalization or state-sync receipt accounting is inconsistent. The provided evidence supports a consensus-correctness and invariant-enforcement fix, but it does not establish a concrete security vulnerability or show that invalid blocks were previously accepted. Root cause: The finalization interface did not provide an explicit error channel for invalid Bor finalization outcomes, so unsupported block-body fields and some state-sync receipt inconsistencies were represented indirectly through the returned receipts instead of being authoritative failures at the finalization boundary.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Convert a consensus finalization hook from an implicit receipt-only result into an error-returning validation boundary, then propagate that error through callers and add explicit consistency checks around synthetic receipt generation.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
