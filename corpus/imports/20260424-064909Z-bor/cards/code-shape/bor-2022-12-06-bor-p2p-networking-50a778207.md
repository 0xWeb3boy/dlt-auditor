# Code-Shape Card

## Metadata

- ID: `bor-2022-12-06-bor-p2p-networking-50a778207`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `path-validation`

## Code Shape Summary

- The supported change is limited to local path-handling hardening. Several call sites that previously used supplied paths directly now call a shared VerifyPath helper before reading files or mutating directories, but the provided evidence does not establish a concrete exploitable vulnerability or a complete path-traversal fix. Root cause: The changed code accepted local path strings and used them directly for filesystem operations without a shared resolution step. The evidence supports that this was considered risky path handling, but it does not prove attacker reachability, a specific exploit path, or that the old behavior was independently vulnerable in practice.

## Search Motifs

- handshake or protocol handler advances peer state before validating identity, key, or request correlation
- sync response is accepted without matching an outstanding request or expected peer capability
- peer-controlled metadata is trusted for scheduling, scoring, or chain progress before verification

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Introduce a shared path-resolution helper and require call sites to fail closed before filesystem access when resolution fails.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
