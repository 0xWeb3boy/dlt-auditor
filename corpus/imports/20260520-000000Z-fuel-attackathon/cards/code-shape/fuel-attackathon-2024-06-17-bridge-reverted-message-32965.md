# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-bridge-reverted-message-32965`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reverted-transaction-withdrawal-message-inclusion`

## Code Shape Summary

- Receipt-derived message ids were appended to block execution data on both success and failure paths, while asset burns were rolled back on revert.

## Search Motifs

- message_ids extend before reverted check
- MessageOut receipt from failed transaction
- withdrawal proof accepts failed status
- receipt committed independently of tx success

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Gate message-id aggregation and proof eligibility on non-reverted execution, and add tests that failed withdrawals cannot produce spendable messages.

## False Match Warnings

- Receipts from failed transactions are safe if they are only logs and cannot enter withdrawal commitments.
- No issue if every proof verifier rejects messages from failed transaction status.
