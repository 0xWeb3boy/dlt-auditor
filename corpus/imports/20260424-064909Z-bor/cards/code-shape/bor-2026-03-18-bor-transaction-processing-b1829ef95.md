# Code-Shape Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-b1829ef95`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`

## Code Shape Summary

- The visible patch adds and broadens range checks in RPC log/filter handlers, which is consistent with availability hardening around expensive historical log scans. The code supports a correctness/resource-control fix, but the provided evidence does not establish an actual security vulnerability or exploit path. Root cause: The visible issue is missing or inconsistent pre-construction validation for block-range log queries in multiple RPC paths. The commit subject suggests a separate config pass-through problem for the range-limit setting, but that wiring is not shown in the supplied evidence.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Add explicit validation gates at RPC entry points so malformed or oversized ranges are rejected before historical scan work is started.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
