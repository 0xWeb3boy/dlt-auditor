# Code-Shape Card

## Metadata

- ID: `nitro-2025-11-07-nitro-cryptography-4272c4cfa`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-hardening`

## Code Shape Summary

- Short description of what the buggy code looked like: The provided evidence supports correctness and hardening changes in the Anytrust DAS RPC/data-streaming path, not a confirmed vulnerability fix. The patch makes nil-signer chunked-store setup fail fast and makes `DisableSignatureChecking=true` use a consistent no-verification path instead of partially wired verifier logic.

## Search Motifs

- Motif 1: nil signers are tolerated in modes that later depend on authenticated chunk storage
- Motif 2: DisableSignatureChecking flips behavior through implicit defaults rather than explicit verifier selection
- Motif 3: later fixes fail fast on unsupported signer combinations and clarify verifier mode wiring

## Typical Asymmetry

- What was checked in one path but missing in another: One path assembled, hashed, or accepted protocol data with ad hoc rules, while the sensitive sink implicitly assumed a single canonical encoding and verification policy.

## Patch Pattern

- What the fix changed structurally: Reject unsupported security-sensitive configuration early and make verifier selection explicit for each operating mode.

## False Match Warnings

- What looks similar but is often not a bug: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
