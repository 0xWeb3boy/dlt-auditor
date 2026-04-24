# Validation Card

## Metadata

- ID: `bor-2025-04-14-bor-p2p-networking-c5c75977a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-churn`

## What Confirmed The Issue

- The commit message says full peer sets could remain largely fixed until error or timeout and that the change adds slow random churn.
- eth/backend.go now starts a background dropper during network startup via s.dropper.Start(...).

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No functional code from eth/dropper.go is shown, so the actual drop policy and safeguards are not evidenced.
- No attacker model or proof of eclipse, slot-pinning, or network-isolation exploitation is included.
