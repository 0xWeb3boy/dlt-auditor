# Code-Shape Card

## Metadata

- ID: `bor-2021-09-13-bor-transaction-processing-b8d7c662c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `trace-output-exposure-hardening`

## Code Shape Summary

- The patch changes EVM trace logging defaults so memory and return data are no longer emitted by default. That is supported as a tracing hardening or correctness change, but the supplied evidence does not establish a concrete vulnerability or exploit scenario. Root cause: The trace configuration used permissive default semantics for verbose fields by expressing them as disable-flags, so zero-value/default behavior included memory and return data unless callers turned them off.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Invert verbose trace fields from default-on disable-flags to explicit enable-flags, and align CLI defaults with the new opt-in behavior.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
