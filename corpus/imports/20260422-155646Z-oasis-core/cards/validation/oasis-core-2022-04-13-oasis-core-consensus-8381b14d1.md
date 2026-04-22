# Validation Card

## Metadata

- ID: `oasis-core-2022-04-13-oasis-core-consensus-8381b14d1`
- Bug family: `resource_accounting_and_limits`
- Bug class: `insufficient-resource-limits`

## What Confirmed The Issue

- Evidence 1: The patch stores sender identity and sender sequence on checked txpool transactions, adds a unique fallback sender when the runtime provides none, and preserves original batch indices while processing checked transactions. That lets the code associate a later scheduling rejection with the correct transaction result and return a 'txpool' error to the submitter.
- Evidence 2: The source finding states the invariant explicitly: Txpool admission should preserve any sender identity returned by CheckTx so sender-aware scheduling or admission rules can be applied consistently, and any downstream queue rejection should be returned to the submitter instead of being left as a log-only condition. The provided evidence does not establish a stronger invariant than local txpool resource control, and the hash-based fallback shows sender-based handling is not uniformly available across runtimes.

## What Could Have Invalidated It

- Compensating control 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Compensating control 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Caution 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.
