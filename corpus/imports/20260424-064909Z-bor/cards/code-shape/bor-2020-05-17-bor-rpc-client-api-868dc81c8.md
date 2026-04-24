# Code-Shape Card

## Metadata

- ID: `bor-2020-05-17-bor-rpc-client-api-868dc81c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fail-open-error-handling`

## Code Shape Summary

- The patch changes Bor's sprint-boundary state-sync flow to return an error when CommitStates fails, adds an early c.config.Sprint guard, moves state commit work into genesisContractsClient, and replaces a local span-pending helper with a current-span contract read. That is evidence of consensus/state-transition refactoring or hardening, but the provided excerpts do not establish a concrete vulnerability or show that the prior behavior was exploitable. Root cause: The only clearly supported issue is permissive error handling in a consensus-related path: FinalizeAndAssemble could continue after CommitStates failed. The rest of the diff shows restructuring around canonical contract-backed helpers, but the evidence does not prove the old local logic was unsafe rather than simply being replaced.

## Search Motifs

- RPC method continues after backend error or returns success with partial/unchecked data
- public query accepts unbounded range, path, or selector before authorization and limit checks
- administrative or debug endpoint exposes privileged behavior without explicit gating

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Fail closed on consensus-path errors and centralize state-sync/span interactions behind explicit contract-backed helper calls.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- RPC findings are lower risk when the method is disabled by default, authenticated, strictly local-only, or returns only non-sensitive metadata.
