# Code-Shape Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-70f86c4d2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-rpc-range-limit-enforcement`

## Code Shape Summary

- The patch shows previously missing or incomplete range-limit enforcement in RPC log-filter paths, plus normalization of symbolic block numbers for that check. That is resource-control relevant, but the provided evidence does not establish an actual exploitable vulnerability rather than a correctness or hardening fix. Root cause: Range-limit enforcement was not consistently applied in the RPC filter code paths handling block-range log queries, and symbolic block selectors needed explicit normalization for that validation logic.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Add centralized pre-execution range validation to each range-query entry point and normalize symbolic inputs only for the validation step.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
