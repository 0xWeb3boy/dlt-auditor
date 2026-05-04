# Validation Card

## Metadata

- ID: `moonbeam-2022-09-12-moonbeam-staking-dade7f12a7`
- Bug family: `authz_and_role_gates`
- Bug class: `evm-precompile-access-control-hardening`

## What Confirmed The Issue

- pallet_evm::AccountCodes caller check added to proxy precompile.
- Dispatch<R> registration removed/commented for Moonbeam and Moonriver.

## What Could Have Invalidated It

- The call path is protected by an independent origin filter equivalent to the new guard
- The affected precompiles were never included in deployed runtime metadata

## Severity Guidance

- Expected impact band: precompile_authorization_boundary
- Expected severity band: high

## False-Positive Cautions

- Some precompiles intentionally support contract callers and are safe if read-only
- A no-code sentinel account exception may be valid
