# Code-Shape Card

## Metadata

- ID: `nitro-2022-04-10-nitro-transaction-processing-3a9ee3753`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `artifact-identity-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch adds explicit module-root canonicalization and a root-match check when loading validator machines, and it wires staker initialization through loader-based latest-root update logic. That supports a correctness or integrity-hardening reading, but the provided evidence does not establish a demonstrated vulnerability.

## Search Motifs

- Motif 1: latest or alias roots are canonicalized in one place but not rechecked at the sink
- Motif 2: loader APIs return resolved identities that callers ignore
- Motif 3: artifact identity checks appear only after proof or machine setup has already started

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Canonicalize alias inputs first, then validate the loaded artifact's reported identity against the canonical value before accepting it.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
