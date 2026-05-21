# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-lido-oracle-cap-withdrawal-overpayment`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `external-oracle-loss-lag`

## What Confirmed The Issue

- The competition report identifies this as `M-11` with `medium` severity.
- The affected surface is specific: yield-provider-accounting at `withdrawal checkpoint share price and payout amount`.
- The missing property can be stated as `loss-freshness-before-withdrawal` and the trigger crosses `Lido oracle/provider truth -> Blast withdrawal settlement`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: insolvency-risk, value-transfer-between-cohorts
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
