# Code-Shape Card

## Metadata

- ID: `bor-2021-12-04-bor-transaction-processing-a7d97ce58`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-state-transition`

## Code Shape Summary

- The supplied evidence supports a consensus-sensitive correctness fix in Bor's genesis/finalization path: both finalization entry points now call changeContractCodeIfNeeded(...) before state-root calculation, and engine startup now validates that configured BlockAlloc entries decode cleanly. That is relevant to deterministic state handling, but the input does not establish an actual vulnerability, attacker trigger, or real security impact. Root cause: The observed root cause is incomplete wiring of genesis-related state-change logic into the finalization paths, plus missing upfront validation for loosely typed genesis allocation config data.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Add the omitted state-transition step to every finalization entry point and validate loosely typed genesis/config payloads at initialization time instead of letting bad data persist into runtime.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
