# Code-Shape Card

## Metadata

- ID: `bor-2026-02-18-bor-transaction-processing-bff847a3d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The provided evidence supports a bounded-work hardening/fix in Bor's background pending-header verification path, motivated by possible OOM from large header reads. It does not establish a confirmed security vulnerability, because the visible hunks do not show a proven attacker-controlled trigger or fully show the claimed cap logic. Root cause: The background verifier built its work from the distance between a milestone boundary and the current head and materialized headers into memory before batch verification. The supplied evidence suggests that this path lacked a sufficiently explicit bounded-work control and relied on weaker configuration/startup assumptions than the patched version.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Constrain a background validation loop with an explicit checkpoint source and add tests for the new bounded-start behavior.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
