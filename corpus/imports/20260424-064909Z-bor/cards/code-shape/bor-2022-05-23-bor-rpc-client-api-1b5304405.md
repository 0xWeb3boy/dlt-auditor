# Code-Shape Card

## Metadata

- ID: `bor-2022-05-23-bor-rpc-client-api-1b5304405`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `privileged-api-exposure`

## Code Shape Summary

- The patch separates signing setup from the node stack account manager and adds an authorized guard around Clique authorization during mining startup. That is consistent with hardening around wallet-endpoint disabling, but the provided evidence does not establish a concrete pre-patch vulnerability or a proven unauthorized signing path. Root cause: The shown code mixed server-local signing setup with the node-wide account manager and did not explicitly track the case where consensus authorization had already been completed before StartMining. The evidence supports a design-tightening change, not a demonstrated exploit.

## Search Motifs

- RPC method continues after backend error or returns success with partial/unchecked data
- public query accepts unbounded range, path, or selector before authorization and limit checks
- administrative or debug endpoint exposes privileged behavior without explicit gating

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Separate privileged signing setup from the shared node account manager and add explicit state to avoid repeating authorization during miner startup.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- RPC findings are lower risk when the method is disabled by default, authenticated, strictly local-only, or returns only non-sensitive metadata.
