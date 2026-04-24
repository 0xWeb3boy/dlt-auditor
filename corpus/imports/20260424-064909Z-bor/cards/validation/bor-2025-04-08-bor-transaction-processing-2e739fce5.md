# Validation Card

## Metadata

- ID: `bor-2025-04-08-bor-transaction-processing-2e739fce5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- Commit body explicitly frames the change as mitigation for an attacker-driven blobpool spam and eviction pattern.
- BlobPool.checkDelegationLimit limits delegated or pending-delegation senders to one executable in-flight transaction.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No exploit reproduction or failing test is provided to show real-world impact against peers or the network.
- The comments acknowledge a remaining cross-subpool race, so the protection is not absolute.
