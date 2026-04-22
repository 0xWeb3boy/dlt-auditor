# Validation Card

## Metadata

- ID: `oasis-core-2019-11-11-oasis-core-rpc-client-api-7816e47dd`
- Bug family: `staking_registry_and_accountability`
- Bug class: `validator-selection-policy`

## What Confirmed The Issue

- Evidence 1: The patch introduces 'ValidatorEntityThreshold', stores it in consensus parameters, requires it to be configured during chain initialization, and uses it when limiting the set of stake-ranked entities considered for validator election.
- Evidence 2: The source finding states the invariant explicitly: Validator election should apply explicitly defined eligibility limits consistently at genesis and during validator selection; the evidence shows this limit became a separate configured parameter, but does not establish that the prior behavior violated safety or allowed an exploit.

## What Could Have Invalidated It

- Compensating control 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Compensating control 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Caution 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.
