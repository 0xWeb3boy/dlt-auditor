# Validation Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-m01-prevrandao-proposer-bias`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `proposer-biased-randomness-source`

## What Confirmed The Issue

- Public C4 report section MR-M-01 rated this as Medium.
- The mitigation review records this as acknowledged; no confirmed fix PR is listed for this issue.

## What Could Have Invalidated It

- No issue if PREVRANDAO remains documented as zero or non-random.
- No issue if source randomness comes from an unbiased consensus beacon.

## Severity Guidance

- Expected impact band: proposer-biased randomness
- Expected severity band: medium

## False-Positive Cautions

- No issue if PREVRANDAO remains documented as zero or non-random.
- No issue if source randomness comes from an unbiased consensus beacon.
- No issue if contracts cannot access or rely on the value.
