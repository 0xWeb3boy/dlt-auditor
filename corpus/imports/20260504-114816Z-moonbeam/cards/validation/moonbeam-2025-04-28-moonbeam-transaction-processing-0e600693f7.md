# Validation Card

## Metadata

- ID: `moonbeam-2025-04-28-moonbeam-transaction-processing-0e600693f7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Moonbase ProxyType::Any changed from unconditional true to target-based filtering.
- Moonbeam fixed no-code/non-precompile target logic and uses account-code metadata.

## What Could Have Invalidated It

- Proxy authorizations explicitly included arbitrary contract calls and users opted into that risk
- A lower EVM layer prevented all blocked target classes before execution

## Severity Guidance

- Expected impact band: authorization_to_evm_target
- Expected severity band: high

## False-Positive Cautions

- ProxyType::Any may intentionally allow all targets only if user consent covers contract calls
- Read-only target calls have lower impact than state-changing calls
