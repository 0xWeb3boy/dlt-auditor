# Code-Shape Card

## Metadata

- ID: `nitro-2022-09-13-nitro-transaction-processing-d23127344`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-initialization`

## Code Shape Summary

- Short description of what the buggy code looked like: The supplied evidence supports an API and startup-hardening change around broadcast-feed verifier setup: `BroadcastClient` now builds its own verifier and can fail during construction, and relay startup now propagates those initialization errors.

## Search Motifs

- Motif 1: security-sensitive verifier objects are injected separately from the client that needs them
- Motif 2: constructors become fallible only after signature-validation bugs are found
- Motif 3: startup paths ignore verifier construction errors until later patches propagate them

## Typical Asymmetry

- What was checked in one path but missing in another: One path assembled, hashed, or accepted protocol data with ad hoc rules, while the sensitive sink implicitly assumed a single canonical encoding and verification policy.

## Patch Pattern

- What the fix changed structurally: Centralize security-sensitive dependency construction inside the consumer's constructor and propagate initialization failure to startup so the component fails closed.

## False Match Warnings

- What looks similar but is often not a bug: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
