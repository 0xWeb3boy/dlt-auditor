# Validation Card

## Metadata

- ID: `bor-2016-11-28-bor-p2p-networking-e949a2ed2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-boundary-enforcement`

## What Confirmed The Issue

- Handshake validation changed from package-global NetworkId to instance-specific self.NetworkId.
- Configured networkId is now passed into run(...) so per-peer runtime state uses the intended network boundary.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No proof that the old behavior allowed a real attacker to join or influence an unintended network in practice.
- No evidence of authentication bypass, cryptographic failure, privilege gain, or confidentiality/integrity compromise.
