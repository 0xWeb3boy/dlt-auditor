# Code-Shape Card

## Metadata

- ID: `bor-2026-03-19-bor-transaction-processing-7d6a68d8b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The supplied evidence shows added range-limit enforcement and block-number normalization in eth/filters RPC paths, which is consistent with resource-control hardening. But the provided hunks do not establish that a concrete vulnerability previously existed, how severe it was, or whether earlier code lacked other effective protections. This is better treated as security-relevant but unproven from the evidence here. Root cause: The visible issue is inconsistent or previously missing range-budget enforcement on some RPC log/filter entry points, plus the need to normalize symbolic block numbers for the guard logic. The commit message suggests config pass-through was also involved, but that part is not directly shown in the provided hunks.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Add explicit resource-budget validation at each RPC entry point before expensive filter construction, and normalize symbolic user inputs when the guard logic requires concrete numeric ranges.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
