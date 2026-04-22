# Validation Card

## Metadata

- ID: `oasis-core-2019-11-21-oasis-core-transaction-processing-e2d134a5a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-gas-accounting`

## What Confirmed The Issue

- Evidence 1: The fix inserts gas-accounting code into the affected registry handlers. Each added block fetches consensus parameters, returns on error, and invokes ctx.Gas().UseGas with the relevant registry gas operation. In registerNode, the charge is applied only when the registration is entity-signed, matching the comment that node-signed registrations are prepaid.
- Evidence 2: The source finding states the invariant explicitly: Registry transactions that mutate on-chain state should apply the configured gas charges before continuing, and the node-registration charging path should remain consistent with the stated fee-payer model for entity-signed versus prepaid node-signed registrations.

## What Could Have Invalidated It

- Compensating control 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Compensating control 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Caution 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.
