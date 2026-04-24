# Validation Card

## Metadata

- ID: `sei-chain-2024-05-03-sei-chain-transaction-processing-e8e4b3bf4`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit`

## What Confirmed The Issue

- Evidence 1: Adds a newHeadLimit check before inserting into newHeadListeners.
- Evidence 2: Performs the listener count check and insertion under newHeadListenersMtx.

## What Could Have Invalidated It

- Compensating control 1: The endpoint is admin-only or already fronted by strict rate limits.
- Compensating control 2: A reverse proxy enforces a smaller authenticated subscription cap.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The endpoint is admin-only or already fronted by strict rate limits.
- Caution 2: A reverse proxy enforces a smaller authenticated subscription cap.
