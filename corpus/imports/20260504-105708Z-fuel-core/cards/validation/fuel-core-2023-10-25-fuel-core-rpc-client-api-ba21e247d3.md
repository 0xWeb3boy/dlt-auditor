# Validation Card

## Metadata

- ID: `fuel-core-2023-10-25-fuel-core-rpc-client-api-ba21e247d3`
- Bug family: `resource_accounting_and_limits`
- Bug class: `p2p-reserved-peer-reputation-hardening`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch rewrites reserved-source Reject outcomes to Ignore before gossip score handling.
- Commit context links the change to authority nodes punishing sentries after race-invalid transactions.

## What Could Have Invalidated It

- Reserved peers exempt from scoring elsewhere.
- The rejected condition is a cryptographic or format violation that should always penalize the sender.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Wrongly penalizing reserved peers can degrade connectivity or sentry relationships. The evidence supports hardening, not a proven chain-wide exploit.

## False-Positive Cautions

- Rejecting malformed or adversarial payloads from untrusted peers is expected.
- Reputation changes are lower risk if they cannot affect peer eviction, banning, or routing.
