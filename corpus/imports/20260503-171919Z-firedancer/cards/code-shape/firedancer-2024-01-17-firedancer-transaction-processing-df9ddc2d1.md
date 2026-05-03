# Code-Shape Card

## Metadata

- ID: `firedancer-2024-01-17-firedancer-transaction-processing-df9ddc2d1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-isolation-hardening`

## Code Shape Summary

- The hardening introduces a dedicated remote-signing path with role-aware authorization and seccomp isolation so signing requests are mediated instead of implicit.

## Search Motifs

- Motif 1: signing request routed through isolated helper
- Motif 2: role-tag or opcode gate on signing RPC
- Motif 3: seccomp or sandbox profile added to signing worker

## Typical Asymmetry

- Less-trusted runtime code can ask for privileged signatures, but only a narrowly authorized request set should reach the signer.

## Patch Pattern

- Route signing through a dedicated client or tile, add explicit request-type authorization, and isolate the signer process with a tighter sandbox.

## False Match Warnings

- No evidence that the previous shred signing path accepted attacker-controlled signing requests.
- No evidence of arbitrary payload signing before the patch.
