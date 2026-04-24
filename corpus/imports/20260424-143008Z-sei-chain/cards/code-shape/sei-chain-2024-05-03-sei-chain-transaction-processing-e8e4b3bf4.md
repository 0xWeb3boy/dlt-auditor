# Code-Shape Card

## Metadata

- ID: `sei-chain-2024-05-03-sei-chain-transaction-processing-e8e4b3bf4`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit`

## Code Shape Summary

- The patch is best characterized as likely denial-of-service hardening for the EVM RPC websocket subscription path. It adds a configuration-backed limit for eth_newHeads subscriptions, passes that limit into SubscriptionAPI, and rejects new subscriptions once the tracked listener count reaches the configured maximum.

## Search Motifs

- Motif 1: newHeads listeners map grows without limit
- Motif 2: config has subscription limit but server does not pass it
- Motif 3: count-and-insert not protected by same mutex

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Thread a configuration-backed limit to the allocation point and reject registrations under the same lock used for listener state.

## False Match Warnings

- The endpoint is admin-only or already fronted by strict rate limits.
- A reverse proxy enforces a smaller authenticated subscription cap.
