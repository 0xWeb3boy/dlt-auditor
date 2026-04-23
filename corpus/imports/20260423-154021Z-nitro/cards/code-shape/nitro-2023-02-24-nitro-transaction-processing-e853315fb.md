# Code-Shape Card

## Metadata

- ID: `nitro-2023-02-24-nitro-transaction-processing-e853315fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-version-gating`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch makes L2 transaction parsing version-aware across block production and reorg replay, and adds an explicit rejection of `ArbitrumExtendedTxType` when `arbOSVersion < 11`. That supports a protocol-correctness invariant, but the provided evidence does not establish a concrete vulnerability rather than feature rollout and compatibility work.

## Search Motifs

- Motif 1: transaction parsers lack access to current protocol version and guess from defaults
- Motif 2: reorg replay paths parse transactions differently from live block production
- Motif 3: unsupported transaction-type checks appear only after ArbOS or protocol-state plumbing is added

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed formatting or shallow admission checks at ingress, but the authoritative policy, payment, version, or sequencing invariant was enforced only later or from weaker context.

## Patch Pattern

- What the fix changed structurally: Thread protocol-version context from canonical state into transaction parsing and fail closed on transaction types that are not yet enabled.

## False Match Warnings

- What looks similar but is often not a bug: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
