# Code-Shape Card

## Metadata

- ID: `bor-2022-05-23-bor-transaction-processing-ba47d800b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-input`

## Code Shape Summary

- The evidenced change is in the Goja-based tracing runtime under eth/tracers/js, where several helper paths stop using panic-driven failure handling and instead interrupt the VM and return nil. This is a real robustness improvement, but the provided evidence does not establish an exploitable vulnerability or even that these panic paths could crash a node in deployment. Root cause: The Goja tracer host helpers handled invalid inputs and helper failures with raw Go panics, and one memory slicing path treated bounds violations as a warning instead of an immediate failure.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Replace panic-on-error and warn-and-continue behavior in tracer host helpers with explicit error checks, VM interruption, and early returns.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
