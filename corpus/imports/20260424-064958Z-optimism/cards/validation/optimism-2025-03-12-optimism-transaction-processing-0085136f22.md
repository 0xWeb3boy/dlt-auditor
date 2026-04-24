# Validation Card

## Metadata

- ID: `optimism-2025-03-12-optimism-transaction-processing-0085136f22`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-integrity`

## What Confirmed The Issue

- InitLiveStrategy now requires isStandardIntent before using the predeployed OPCM/global SuperchainConfig path.
- The new path consults standard superchain-role data instead of relying only on tag presence and predeployment availability.
- Standard intent creation stops ignoring lookup failures for challenger and proxy-admin owner addresses.
- The commit message describes prior unintended inheritance of the global SuperchainConfig on official tagged chains.

## What Could Have Invalidated It

- No proof that an untrusted actor could trigger this deployment path.
- No proof that the prior behavior caused actual unauthorized control or exploitable privilege escalation.
- No evidence of an incident, compromise, or concrete downstream impact from the misbinding.
- The excerpts do not fully show how role comparisons are enforced after lookup.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No proof that an untrusted actor could trigger this deployment path.
- No proof that the prior behavior caused actual unauthorized control or exploitable privilege escalation.
- No evidence of an incident, compromise, or concrete downstream impact from the misbinding.
