# Validation Card

## Metadata

- ID: `fuel-core-2026-04-23-fuel-core-storage-bf285299c4`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `leader-lease-release-delay`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch changes drop_release_guard to Option-like ownership semantics and clears it on spawned-task clones.
- Regression test covers slow-node publish tasks keeping the guard alive after short-circuit.

## What Could Have Invalidated It

- Lease release is not security-relevant because a separate consensus mechanism handles failover safely.
- The cloned object is never moved into long-lived background tasks.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Delayed leader lease release can slow or block failover in a PoA system. Evidence supports availability hardening rather than invalid leadership or signature failure.

## False-Positive Cautions

- No issue if leases always expire quickly and failover ignores explicit release.
- No issue if worker clones cannot outlive the owning adapter.
