# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-uninitialized-usd-yield-manager-implementation`
- Bug family: `authz_and_role_gates`
- Bug class: `unlocked-proxy-implementation-initializer`

## What Confirmed The Issue

- The competition report identifies this as `H-04` with `high` severity.
- The affected surface is specific: yield-manager-upgradeability at `owner-only provider registration and delegatecall to provider code`.
- The missing property can be stated as `implementation-initializer-locking` and the trigger crosses `external caller -> implementation contract address`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: denial-of-service, upgrade-safety
- Expected severity band: high

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
