# Code-Shape Card

## Metadata

- ID: `rippled-2024-02-02-rippled-core-logic-828bb64eb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reserve-enforcement-bypass`

## Code Shape Summary

- The evidence supports a protocol reserve-enforcement fix in rippled's NFTokenAcceptOffer sell-offer path. Reusable shape: check for reserve-enforcement was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact reserve-enforcement check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Centralize the NFT ownership transfer point and enforce the recipient's post-transfer reserve requirement when the transfer changes OwnerCount or NFTokenPage burden.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the reserve-enforcement gate runs before the state-changing branch.

## Patch Pattern

- Centralize the NFT ownership transfer point and enforce the recipient's post-transfer reserve requirement when the transfer changes OwnerCount or NFTokenPage burden.

## False Match Warnings

- Provided snippets do not show the actual OwnerCount or reserve-check logic.
- No supplied evidence demonstrates theft, unauthorized transfer, or direct fund loss.
