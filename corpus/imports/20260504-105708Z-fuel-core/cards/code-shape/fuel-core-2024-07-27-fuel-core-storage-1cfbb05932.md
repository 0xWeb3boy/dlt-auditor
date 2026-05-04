# Code-Shape Card

## Metadata

- ID: `fuel-core-2024-07-27-fuel-core-storage-1cfbb05932`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reverted-transaction-withdrawal-message-inclusion`

## Code Shape Summary

- Receipt aggregation iterated over message ids independently from the final reverted flag, so failed transactions still influenced block-level execution data.

## Search Motifs

- message_ids updated before reverted check
- receipt.message_id collected for failed transaction
- withdrawal message included in header for reverted tx
- execution_data.message_ids gate

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Move message-id aggregation behind a non-reverted status gate and add regression tests for successful versus reverted withdrawal message inclusion.

## False Match Warnings

- Receipts from reverted transactions may be retained for logs if they are not committed as spendable withdrawal messages.
- No issue if later proof verification rejects any message id from a reverted transaction.
