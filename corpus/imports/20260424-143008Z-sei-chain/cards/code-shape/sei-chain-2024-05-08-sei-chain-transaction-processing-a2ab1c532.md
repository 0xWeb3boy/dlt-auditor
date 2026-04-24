# Code-Shape Card

## Metadata

- ID: `sei-chain-2024-05-08-sei-chain-transaction-processing-a2ab1c532`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `monetary-accounting-invariant`

## Code Shape Summary

- The patch likely fixes a security-relevant EVM surplus accounting bug. The strongest supported finding is that ante surplus was mishandled across ante processing, EndBlock aggregation, and total supply repair. The evidence supports a supply-accounting mismatch, not a crash, theft, replay, cryptographic validation, or proven attacker-controlled minting issue.

## Search Motifs

- Motif 1: surplus recorded outside keeper state
- Motif 2: negative surplus rejected before netting with positive values
- Motif 3: migration repairs total supply drift

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Move deltas into canonical keeper state, aggregate them once, net related values, and migrate existing drift deliberately.

## False Match Warnings

- The accounting path affects only diagnostics and not balances or supply.
- A later invariant check aborts the block before committing mismatched state.
