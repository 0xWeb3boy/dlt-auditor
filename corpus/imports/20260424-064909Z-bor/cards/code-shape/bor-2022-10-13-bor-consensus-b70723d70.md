# Code-Shape Card

## Metadata

- ID: `bor-2022-10-13-bor-consensus-b70723d70`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-chain-validation`

## Code Shape Summary

- The diff supports a correctness or hardening change in Bor's whitelist milestone lock state, but it does not establish a concrete vulnerability. The implementation now tightens lock progression rules and stores the locked sprint hash, and the tests were updated to exercise that behavior. Root cause: The evidence points to incomplete milestone lock-state handling: the prior code did not fully enforce monotonic lock transitions and did not retain the associated end-block hash in the lock state.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Tighten a local state machine by enforcing additional transition guards, clearing stale state on advancement, and storing the full state needed for later validation.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
