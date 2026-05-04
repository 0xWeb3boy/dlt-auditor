# Validation Card

## Metadata

- ID: `moonbeam-2022-09-12-moonbeam-staking-c7d8fc12f2`
- Bug family: `authz_and_role_gates`
- Bug class: `evm-precompile-authorization-boundary-hardening`

## What Confirmed The Issue

- Proxy precompile now reads caller AccountCodes and rejects arbitrary contract callers.
- Moonbeam/Moonriver precompile sets disable Dispatch<R>.

## What Could Have Invalidated It

- Downstream RuntimeHelper dispatch always maps contract callers to an unprivileged origin with no sensitive calls
- Dispatch precompile was unreachable in deployed networks

## Severity Guidance

- Expected impact band: precompile_authorization_boundary
- Expected severity band: high

## False-Positive Cautions

- Contract callers may be safe if downstream origin conversion always denies privileged calls
- Precompile may be dev-only or disabled by runtime feature flags
