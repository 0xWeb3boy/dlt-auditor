# Validation Card

## Metadata

- ID: `oasis-core-2020-02-06-oasis-core-staking-635fcfd29`
- Bug family: `staking_registry_and_accountability`
- Bug class: `missing-stake-enforcement`

## What Confirmed The Issue

- Evidence 1: The patch fetches consensus parameters where needed, gates the behavior on 'DebugBypassStake', invokes 'EnsureSufficientRuntimeStake', and uses the result to reject runtime registration or suspend already-registered runtimes in key manager and roothash flows.
- Evidence 2: The source finding states the invariant explicitly: When runtime deposit enforcement is enabled, runtime registration and continued runtime operation are intended to require the owning entity to satisfy the relevant stake thresholds.

## What Could Have Invalidated It

- Compensating control 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Compensating control 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Caution 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.
