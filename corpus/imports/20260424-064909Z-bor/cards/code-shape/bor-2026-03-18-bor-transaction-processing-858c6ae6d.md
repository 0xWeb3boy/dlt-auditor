# Code-Shape Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-858c6ae6d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit-enforcement`

## Code Shape Summary

- The evidence supports a resource-control and correctness change in the RPC log-filter subsystem: range-based log queries now check a configured block-range limit before building filters, and symbolic block numbers are normalized for that check. The supplied hunks do not establish a concrete vulnerability or demonstrated exploit path, so this should be treated as unclear rather than confirmed security work. Root cause: The visible issue is inconsistent or missing enforcement of a configured block-range limit in several RPC log-filter entry points. The commit subject also mentions config pass-through, but the provided evidence does not show that wiring bug directly.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Add centralized precondition checks at each range-query entry point so configured resource limits are enforced before expensive filter construction, with explicit normalization of symbolic inputs for validation.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
