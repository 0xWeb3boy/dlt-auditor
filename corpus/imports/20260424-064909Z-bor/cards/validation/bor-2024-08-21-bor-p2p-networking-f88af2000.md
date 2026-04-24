# Validation Card

## Metadata

- ID: `bor-2024-08-21-bor-p2p-networking-f88af2000`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation`

## What Confirmed The Issue

- Runtime logic in eth/downloader/bor_downloader.go now returns errStallingPeer when no headers were received but the peer still claims higher total difficulty.
- The affected code is in the downloader's peer-driven header processing path, which is security-sensitive and network exposed.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- The excerpt does not show the full lifecycle of gotHeaders, including where it becomes true.
- The patch does not demonstrate a concrete exploit, attacker-controlled impact, or prior successful abuse.
