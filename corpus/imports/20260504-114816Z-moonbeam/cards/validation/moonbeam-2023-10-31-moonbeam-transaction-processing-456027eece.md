# Validation Card

## Metadata

- ID: `moonbeam-2023-10-31-moonbeam-transaction-processing-456027eece`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proxy-call-filter-hardening`

## What Confirmed The Issue

- Moonbeam/Moonriver/Moonbase NormalFilter adds pallet_proxy::Call::proxy target check.
- Proxy weights add one DB read for AccountCodes lookup.

## What Could Have Invalidated It

- EVM contract accounts cannot be represented as real proxy accounts
- A deeper origin converter rejects all contract-account proxy targets

## Severity Guidance

- Expected impact band: proxy_origin_policy
- Expected severity band: medium

## False-Positive Cautions

- Proxying to contract accounts may be intended if downstream origin semantics are explicit
- A separate proxy type filter may already deny sensitive calls
